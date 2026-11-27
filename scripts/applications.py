# SAE S5.C.01
# Application en ligne de commande : comptes, recherche, notes
# Usage : uv run scripts/applications.py

import os
import subprocess
import sys

from getpass import getpass
from moteur_series.base import connexion
from moteur_series.comptes import creer_compte, se_connecter
from moteur_series.config import RACINE

SCRIPT_RECHERCHE = os.path.join(RACINE, "scripts", "recherche.py")

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
        ("0", sortie),
    ])
    if choix == "1":
        return "recherche"
    if utilisateur is not None:
        annoncer("Vous êtes déconnecté.", GRIS)
    return "accueil"


def lancer_recherche(utilisateur):
    """
    Lance scripts/recherche.py et attend qu'il se termine
    sys.executable = le Python de uv, comme "uv run scripts/recherche.py"
    """
    afficher_entete("RECHERCHE", utilisateur)
    try:
        subprocess.run([sys.executable, SCRIPT_RECHERCHE])
    except KeyboardInterrupt:
        # Sous Windows, Ctrl+C arrive aussi ici : on revient simplement au menu
        pass

def main():
    os.system("")   # active les couleurs ANSI dans la console Windows
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
            lancer_recherche(utilisateur)
            ecran = "menu"        # fin de la recherche : retour au menu

    conn.close()
    print(couleur(" Au revoir !", CYAN))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C (ou Ctrl+Z puis Entree) n'importe ou : on quitte proprement
        print()
        print(couleur(" Au revoir !", CYAN))