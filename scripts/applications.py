# SAE S5.C.01
# Application en ligne de commande : comptes, recherche, notes
# Usage : uv run scripts/applications.py

import difflib
import os
import re
import sys
import time

from getpass import getpass
from moteur_series.base import connexion
from moteur_series.comptes import creer_compte, se_connecter
from moteur_series.config import BASE
from moteur_series.recherche import charger_index, rechercher
from moteur_series.recommandation import (
    calculer_similarites,
    charger_notes,
    charger_vecteurs,
    noter_serie,
    recommander_selon_notes,
    series_similaires,
)
from moteur_series.texte import supprimer_accents

# msvcrt (Windows seulement) lit le clavier touche par touche : c'est ce qui
# permet de reconnaitre la touche Echap, que input() ne voit pas
if os.name == "nt":
    import msvcrt

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


def saisir(invite, masque=False):
    """
    Remplace input() : lit une ligne au clavier, mais la touche Echap annule.
    Renvoie le texte tape (sans espaces autour), ou None si Echap.
    masque=True : les caracteres s'affichent en * (mot de passe, non nettoye)
    """
    # Hors Windows, ou si la saisie vient d'un fichier (tests) : lecture
    # normale d'une ligne, sans la touche Echap
    if os.name != "nt" or not sys.stdin.isatty():
        if masque and sys.stdin.isatty():
            return getpass(invite)
        texte = input(invite)
        if masque:
            return texte
        return texte.strip()

    print(invite, end="", flush=True)
    texte = ""
    while True:
        touche = msvcrt.getwch()            # attend une touche, sans Entree
        if touche == "\r":                  # Entree : la saisie est finie
            print()
            if masque:
                return texte
            return texte.strip()
        if touche == "\x1b":                # Echap : on annule
            print()
            return None
        if touche == "\x03":                # Ctrl+C : quitter, comme avec input()
            raise KeyboardInterrupt
        if touche == "\x08":                # Retour arriere : on efface le dernier caractere
            if len(texte) > 0:
                texte = texte[:-1]
                print("\b \b", end="", flush=True)
            continue
        if touche in ("\x00", "\xe0"):      # fleches, F1... : envoient 2 codes, on les ignore
            msvcrt.getwch()
            continue
        if touche < " ":                    # autres touches de controle (Tab...) : ignorees
            continue
        texte = texte + touche
        if masque:
            print("*", end="", flush=True)
        else:
            print(touche, end="", flush=True)


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
    if titre != "ACCUEIL":
        print(couleur(" Échap : revenir en arrière", GRIS))

    for message in messages:
        print(" " + message)
    messages.clear()
    print()

def choisir(options):
    """
    Affiche le menu et redemande tant que le choix n'est pas valide.
    Renvoie la touche choisie, ou None si Echap.
    """
    touches = []
    for touche, libelle in options:
        print("   " + couleur("[" + touche + "]", CYAN) + "  " + libelle)
        touches.append(touche)
    print()
    while True:
        choix = saisir(couleur(" > ", JAUNE))
        if choix is None or choix in touches:
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
    if choix == "0":
        return "quitter"
    return "accueil"   # Echap sur l'accueil : rien avant, on reste

def ecran_connexion(conn):
    """
    Renvoie (ecran suivant, utilisateur) ; utilisateur = (id, pseudo) ou None
    """
    afficher_entete("CONNEXION", None)
    print(couleur(" Laissez le pseudo vide pour revenir à l'accueil.", GRIS))
    print()
    pseudo = saisir(" Pseudo       : ")
    if pseudo is None or pseudo == "":
        return ("accueil", None)
    mdp = saisir(" Mot de passe : ", masque=True)
    if mdp is None:
        return ("accueil", None)

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
    pseudo = saisir(" Pseudo       : ")
    if pseudo is None or pseudo == "":
        return "accueil"
    email = saisir(" Email        : ")
    if email is None:
        return "accueil"
    mdp = saisir(" Mot de passe : ", masque=True)
    if mdp is None:
        return "accueil"
    confirmation = saisir(" Confirmation : ", masque=True)
    if confirmation is None:
        return "accueil"

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
    options = [
        ("1", "Rechercher une série par mots-clés"),
        ("2", "Séries similaires à une série"),
    ]
    if utilisateur is None:
        print(couleur(" Connectez-vous pour noter des séries et recevoir des recommandations.", GRIS))
        print()
        options.append(("0", "Retour à l'accueil"))
    else:
        options.append(("3", "Noter une série"))
        options.append(("4", "Mes recommandations"))
        options.append(("0", "Se déconnecter"))

    choix = choisir(options)
    if choix == "1":
        return "recherche"
    if choix == "2":
        return "similaires"
    if choix == "3":
        return "noter"
    if choix == "4":
        return "recommandations"
    # "0" ou Echap : retour a l'accueil (ce qui deconnecte)
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
    Renvoie le titre tel qu'il est dans la base, ou None si Echap ou ligne vide
    """
    while True:
        saisie = saisir(couleur(invite, JAUNE))
        if saisie is None or saisie == "":
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


def proposer_de_noter(conn, utilisateur, resultats):
    """
    Apres une liste de resultats [(titre, score), ...] : propose de noter les
    series affichees en tapant leur numero (seulement si l'utilisateur est connecte)
    Renvoie True si au moins une note a ete enregistree
    """
    if utilisateur is None or len(resultats) == 0:
        return False
    a_note = False
    while True:
        saisie = saisir(couleur(" Numéro de la série à noter (Entrée pour continuer) : ", JAUNE))
        if saisie is None or saisie == "":
            return a_note
        # isdigit() avant int() : "abc" ou "-1" ne font pas planter le programme
        if not saisie.isdigit() or int(saisie) < 1 or int(saisie) > len(resultats):
            print(" " + couleur("Tapez un numéro entre 1 et " + str(len(resultats)) + ", ou Entrée.", ROUGE))
            continue
        titre = resultats[int(saisie) - 1][0]   # la liste commence a 0, l'affichage a 1
        note = demander_note()
        if note is None:
            print(couleur(" Note annulée.", GRIS))
            continue
        noter_serie(conn, utilisateur[0], titre, note)
        print(" " + couleur("Note enregistrée : " + titre + " " + str(note) + "/5", VERT))
        a_note = True


def ecran_recherche(conn, index, utilisateur):
    afficher_entete("RECHERCHE", utilisateur)
    print(couleur(" Tapez des mots-clés (ligne vide pour revenir au menu).", GRIS))
    while True:
        print()
        requete = saisir(couleur(" Recherche : ", JAUNE))
        if requete is None or requete == "":
            return "menu"
        debut = time.time()
        resultats = rechercher(requete, index)
        duree = (time.time() - debut) * 1000
        if len(resultats) == 0:
            print(" " + couleur("Aucune série trouvée.", ROUGE))
        else:
            afficher_resultats(resultats)
            print(couleur(f" ({duree:.0f} ms)", GRIS))
            proposer_de_noter(conn, utilisateur, resultats)


def ecran_similaires(conn, similarites, utilisateur):
    afficher_entete("SÉRIES SIMILAIRES", utilisateur)
    print(couleur(" Tapez le nom d'une série (ligne vide pour revenir au menu).", GRIS))
    while True:
        print()
        titre = demander_titre(similarites, " Série : ")
        if titre is None:
            return "menu"
        print(" Les séries les plus proches de " + couleur(titre, GRAS) + " :")
        resultats = series_similaires(titre, similarites)
        afficher_resultats(resultats)
        proposer_de_noter(conn, utilisateur, resultats)


def afficher_notes(notes):
    """
    Affiche les notes {titre: note} avec des etoiles, de la meilleure a la moins bonne
    """
    if len(notes) == 0:
        print(couleur(" Vous n'avez encore noté aucune série.", GRIS))
        return
    print(" Vos notes :")
    classement = sorted(notes.items(), key=lambda paire: paire[1], reverse=True)
    for titre, note in classement:
        etoiles = "★" * note + "☆" * (5 - note)
        print("   " + titre.ljust(30) + couleur(etoiles, JAUNE))


def demander_note():
    """
    Redemande tant que la saisie n'est pas un entier de 1 a 5
    Renvoie la note, ou None si Echap
    """
    while True:
        saisie = saisir(couleur(" Note de 1 à 5 : ", JAUNE))
        if saisie is None:
            return None
        if saisie in ["1", "2", "3", "4", "5"]:
            return int(saisie)
        print(" " + couleur("La note doit être un nombre entier de 1 à 5.", ROUGE))


def ecran_noter(conn, similarites, utilisateur):
    afficher_entete("NOTER UNE SÉRIE", utilisateur)
    id_utilisateur = utilisateur[0]
    afficher_notes(charger_notes(id_utilisateur))
    print()
    print(couleur(" Tapez le nom d'une série (ligne vide pour revenir au menu).", GRIS))
    print(couleur(" Si elle est déjà notée, la nouvelle note remplace l'ancienne.", GRIS))
    while True:
        print()
        titre = demander_titre(similarites, " Série : ")
        if titre is None:
            return "menu"
        note = demander_note()
        if note is None:
            print(couleur(" Note annulée.", GRIS))
            continue
        noter_serie(conn, id_utilisateur, titre, note)
        print(" " + couleur("Note enregistrée : " + titre + " " + str(note) + "/5", VERT))


def ecran_mes_recommandations(conn, similarites, utilisateur):
    afficher_entete("MES RECOMMANDATIONS", utilisateur)
    notes = charger_notes(utilisateur[0])
    afficher_notes(notes)
    print()

    if len(notes) == 0:
        print(couleur(" Notez quelques séries (menu, option 3) pour recevoir des recommandations.", GRIS))
    else:
        resultats = recommander_selon_notes(notes, similarites)
        if len(resultats) == 0:
            # recommander_selon_notes ignore les notes de 3 (poids note - 3 = 0)
            print(couleur(" Toutes vos notes valent 3 (neutre) : notez des séries que vous", GRIS))
            print(couleur(" aimez (4 ou 5) ou que vous n'aimez pas (1 ou 2).", GRIS))
        else:
            print(" Séries recommandées pour vous :")
            afficher_resultats(resultats)
            print()
            # Une nouvelle note change les recommandations : on reaffiche l'ecran
            if proposer_de_noter(conn, utilisateur, resultats):
                return "recommandations"
            return "menu"

    print()
    saisir(couleur(" Appuyez sur Entrée ou Échap pour revenir au menu.", GRIS))
    return "menu"


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
            ecran = ecran_recherche(conn, index, utilisateur)
        elif ecran == "similaires":
            ecran = ecran_similaires(conn, similarites, utilisateur)
        elif ecran == "noter":
            ecran = ecran_noter(conn, similarites, utilisateur)
        elif ecran == "recommandations":
            ecran = ecran_mes_recommandations(conn, similarites, utilisateur)

    conn.close()
    print(couleur(" Au revoir !", CYAN))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C (ou Ctrl+Z puis Entree) n'importe ou : on quitte proprement
        print()
        print(couleur(" Au revoir !", CYAN))