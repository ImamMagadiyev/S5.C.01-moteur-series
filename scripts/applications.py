# SAE S5.C.01
# Application en ligne de commande : comptes, recherche, notes
# Usage : uv run scripts/applications.py

import difflib
import os
import re
import time

from getpass import getpass
from moteur_series.base import connexion
from moteur_series.comptes import creer_compte, se_connecter
from moteur_series.config import BASE
from moteur_series.recherche import charger_index, rechercher
from moteur_series.recommandation import calculer_similarites, charger_vecteurs, series_similaires
from moteur_series.texte import supprimer_accents

LARGEUR = 52

# Codes couleur ANSI : le terminal les interprete au lieu de les afficher
RESET = "\033[0m"
GRAS = "\033[1m"
GRIS = "\033[90m"
ROUGE = "\033[91m"
VERT = "\033[92m"
JAUNE = "\033[93m"
CYAN = "\033[96m"

# L'ecran est efface a chaque page : les messages ("Compte cree", "Mot de passe
# incorrect"...) sont gardes ici et affiches en haut de la page suivante
messages = []

def couleur(texte, code):
    return code + texte + RESET

def annoncer(texte, code):
    """
    Garde un message pour l'afficher en haut de la prochaine etape
    """
    messages.append(couleur(texte, code))

def effacer_ecran():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def afficher_entete(titre, utilisateur):
    """
    Efface l'ecran puis affiche : le cadre du haut, le titre de la page,
    qui est connecte, et les messages en attente.
    utilisateur : None ou (id_utilisateur, pseudo)
    """
    effacer_ecran()
    bord = couleur("║", CYAN)
    print(couleur("╔" + "═" * LARGEUR + "╗", CYAN))
    print(bord + couleur("MOTEUR DE SERIES".center(LARGEUR), GRAS) + bord)
    print(bord + couleur("Recherche et recommandation par les sous-titres".center(LARGEUR), GRIS) + bord)
    print(couleur("╚" + "═" * LARGEUR + "╝", CYAN))
    print()

    if utilisateur is None:
        statut = "Non connecté"
        code_statut = GRIS
    else:
        statut = "Connecté : " + utilisateur[1]
        code_statut = VERT
    # titre a gauche, statut a droite (on aligne AVANT d'ajouter les couleurs,
    # car les codes ANSI comptent dans len() mais ne s'affichent pas)
    espace = LARGEUR - len(titre) - len(statut)
    print(" " + couleur(titre, GRAS + JAUNE) + " " * espace + couleur(statut, code_statut))
    print(" " + couleur("-" * LARGEUR, GRIS))

    for message in messages:
        print(" " + message)
    messages.clear()
    print()

def choisir(options):
    """
    Affiche le menu et redemande tant que le choix n'est pas valide.
    Renvoie la touche choisie.
    """
    touches = []
    for touche, libelle in options:
        print("   " + couleur("[" + touche + "]", CYAN) + "  " + libelle)
        touches.append(touche)
    print()
    while True:
        choix = input(couleur(" > ", JAUNE)).strip()
        if choix in touches:
            return choix
        print(" " + couleur("Choix invalide, tapez " + ", ".join(touches) + ".", ROUGE))


def ecran_accueil():
    afficher_entete("ACCUEIL", None)
    choix = choisir([
        ("1", "Se connecter"),
        ("2", "Créer un compte"),
        ("3", "Continuer sans compte"),
        ("0", "Quitter"),
    ])
    if choix == "1":
        return "connexion"
    if choix == "2":
        return "inscription"
    if choix == "3":
        return "menu"
    return "quitter"

def ecran_connexion(conn):
    """
    Renvoie (ecran suivant, utilisateur) ; utilisateur = (id, pseudo) ou None
    """
    afficher_entete("CONNEXION", None)
    print(couleur(" Laissez le pseudo vide pour revenir à l'accueil.", GRIS))
    print()
    pseudo = input(" Pseudo       : ").strip()
    if pseudo == "":
        return ("accueil", None)
    mdp = getpass(" Mot de passe : ")

    resultat, id_utilisateur = se_connecter(conn, pseudo, mdp)
    if resultat == "ok":
        annoncer("Bienvenue " + pseudo + " !", VERT)
        return ("menu", (id_utilisateur, pseudo))
    if resultat == "mauvais_mdp":
        annoncer("Mot de passe incorrect, réessayez.", ROUGE)
        return ("connexion", None)

    # resultat == "inconnu"
    print()
    print(" " + couleur("Le pseudo « " + pseudo + " » n'existe pas.", ROUGE))
    print()
    choix = choisir([
        ("1", "Créer un compte"),
        ("2", "Continuer sans compte"),
        ("0", "Retour à l'accueil"),
    ])
    if choix == "1":
        return ("inscription", None)
    if choix == "2":
        return ("menu", None)
    return ("accueil", None)

def ecran_creer_compte(conn):
    afficher_entete("CRÉER UN COMPTE", None)
    print(couleur(" Laissez le pseudo vide pour revenir à l'accueil.", GRIS))
    print()
    pseudo = input(" Pseudo       : ").strip()
    if pseudo == "":
        return "accueil"
    email = input(" Email        : ").strip()
    mdp = getpass(" Mot de passe : ")
    confirmation = getpass(" Confirmation : ")

    if email == "" or mdp == "":
        annoncer("Tous les champs sont obligatoires.", ROUGE)
        return "inscription"
    if mdp != confirmation:
        annoncer("Les deux mots de passe sont différents.", ROUGE)
        return "inscription"

    if creer_compte(conn, pseudo, email, mdp):
        annoncer("Compte créé, vous pouvez vous connecter.", VERT)
        return "connexion"

    annoncer("Ce pseudo ou cet email est déjà utilisé.", ROUGE)
    return "inscription"


def ecran_menu(utilisateur):
    """Menu principal, avec ou sans compte."""
    afficher_entete("MENU", utilisateur)
    if utilisateur is None:
        sortie = "Retour à l'accueil"
    else:
        sortie = "Se déconnecter"
    choix = choisir([
        ("1", "Rechercher une série par mots-clés"),
        ("2", "Séries similaires à une série"),
        ("0", sortie),
    ])
    if choix == "1":
        return "recherche"
    if choix == "2":
        return "similaires"
    if utilisateur is not None:
        annoncer("Vous êtes déconnecté.", GRIS)
    return "accueil"


def charger_donnees():
    """
    Charge l'index de recherche et calcule les similarites entre series
    Une seule fois, au demarrage : ensuite chaque requete est instantanee
    """
    debut = time.time()
    print(couleur(" Chargement de l'index de recherche...", GRIS))
    index = charger_index()
    print(couleur(" Calcul des similarités entre séries...", GRIS))
    similarites = calculer_similarites(charger_vecteurs())
    print(couleur(" Prêt en " + str(round(time.time() - debut, 1)) + " s", GRIS))
    return index, similarites


def afficher_resultats(resultats):
    """
    Affiche une liste [(titre, score), ...] numerotee
    """
    rang = 1
    for titre, score in resultats:
        numero = couleur(str(rang).rjust(2) + ".", CYAN)
        print("   " + numero + " " + titre.ljust(30) + couleur(f"{score:.3f}", GRIS))
        rang = rang + 1


def demander_titre(similarites, invite):
    """
    Demande le nom d'une serie jusqu'a ce qu'il corresponde a une serie connue
    Renvoie le titre tel qu'il est dans la base, ou None si la ligne est vide
    """
    while True:
        saisie = input(couleur(invite, JAUNE)).strip()
        if saisie == "":
            return None
        # Les titres de la base sont colles, en minuscules, sans accents :
        # "Grey's Anatomy" -> "greysanatomy"
        titre = re.sub(r"[^a-z0-9]", "", supprimer_accents(saisie.lower()))
        if titre in similarites:
            return titre

        # Titre inconnu : on propose d'abord les titres qui s'ecrivent presque
        # pareil (fautes de frappe), puis ceux qui contiennent ce qui a ete tape
        propositions = difflib.get_close_matches(titre, list(similarites), n=3, cutoff=0.6)
        for titre_connu in sorted(similarites):
            if titre != "" and titre in titre_connu and titre_connu not in propositions:
                propositions.append(titre_connu)
        if len(propositions) > 0:
            print(" " + couleur("Série inconnue. Vouliez-vous dire : " + ", ".join(propositions[:5]) + " ?", ROUGE))
        else:
            print(" " + couleur("Série inconnue.", ROUGE))


def ecran_recherche(index, utilisateur):
    afficher_entete("RECHERCHE", utilisateur)
    print(couleur(" Tapez des mots-clés (ligne vide pour revenir au menu).", GRIS))
    while True:
        print()
        requete = input(couleur(" Recherche : ", JAUNE)).strip()
        if requete == "":
            return "menu"
        debut = time.time()
        resultats = rechercher(requete, index)
        duree = (time.time() - debut) * 1000
        if len(resultats) == 0:
            print(" " + couleur("Aucune série trouvée.", ROUGE))
        else:
            afficher_resultats(resultats)
            print(couleur(f" ({duree:.0f} ms)", GRIS))


def ecran_similaires(similarites, utilisateur):
    afficher_entete("SÉRIES SIMILAIRES", utilisateur)
    print(couleur(" Tapez le nom d'une série (ligne vide pour revenir au menu).", GRIS))
    while True:
        print()
        titre = demander_titre(similarites, " Série : ")
        if titre is None:
            return "menu"
        print(" Les séries les plus proches de " + couleur(titre, GRAS) + " :")
        afficher_resultats(series_similaires(titre, similarites))


def main():
    os.system("")   # active les couleurs ANSI dans la console Windows
    # sqlite3.connect creerait une base vide si le fichier n'existe pas
    if not os.path.exists(BASE):
        print(couleur(" ERREUR : base introuvable : " + BASE, ROUGE))
        print(" Lancer d'abord la préparation (create_base.py puis indexation/main.py).")
        return
    index, similarites = charger_donnees()
    conn = connexion()

    ecran = "accueil"
    utilisateur = None            # None = personne de connecte, sinon (id, pseudo)
    while ecran != "quitter":
        if ecran == "accueil":
            utilisateur = None    # revenir a l'accueil = se deconnecter
            ecran = ecran_accueil()
        elif ecran == "connexion":
            ecran, utilisateur = ecran_connexion(conn)
        elif ecran == "inscription":
            ecran = ecran_creer_compte(conn)
        elif ecran == "menu":
            ecran = ecran_menu(utilisateur)
        elif ecran == "recherche":
            ecran = ecran_recherche(index, utilisateur)
        elif ecran == "similaires":
            ecran = ecran_similaires(similarites, utilisateur)

    conn.close()
    print(couleur(" Au revoir !", CYAN))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C (ou Ctrl+Z puis Entree) n'importe ou : on quitte proprement
        print()
        print(couleur(" Au revoir !", CYAN))