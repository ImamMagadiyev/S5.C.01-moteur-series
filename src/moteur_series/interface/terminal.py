# SAE S5.C.01
# Outils du terminal : couleurs, saisie au clavier (avec Echap), en-tete, menus
# Ne connait ni les series ni les comptes : utilise par tous les ecrans

import os
import sys

from getpass import getpass

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


def afficher_resultats(resultats):
    """
    Affiche une liste [(titre, score), ...] numerotee
    """
    rang = 1
    for titre, score in resultats:
        numero = couleur(str(rang).rjust(2) + ".", CYAN)
        print("   " + numero + " " + titre.ljust(30) + couleur(f"{score:.3f}", GRIS))
        rang = rang + 1