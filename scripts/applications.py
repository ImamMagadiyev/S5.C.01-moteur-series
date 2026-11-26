# SAE S5.C.01
# Application en ligne de commande : comptes, recherche, notes
# Usage : uv run scripts/application.py

from getpass import getpass

from moteur_series.base import connexion
from moteur_series.comptes import creer_compte, se_connecter
import os
import subprocess
import sys

from moteur_series.config import RACINE

SCRIPT_RECHERCHE = os.path.join(RACINE, "scripts", "recherche.py")

def ecran_accueil():
    print("\n=== ACCUEIL ===")
    print("1. Se connecter")
    print("2. Creer un compte")
    print("3. Continuer en anonyme")
    print("0. Quitter")
    while True:
        choix = input("Votre choix : ").strip()
        if choix == "1":
            return "connexion"
        if choix == "2":
            return "inscription"
        if choix == "3":
            return "anonyme"
        if choix == "0":
            return "quitter"
        print("Choix invalide.")


def ecran_connexion(conn):
    print("\n=== CONNEXION ===")
    pseudo = input("Votre pseudio :").strip()
    mdp = getpass("Mot de passe : ")

    resultat,id_utilisateur = se_connecter(conn,pseudo,mdp)
    if resultat == "mauvais_mdp":
        print("Mot de passe incorrect, reessayez.")
        return ("connexion", None)
    elif resultat == "ok":
        print("Bienvenue", pseudo, "!")
        return ("connecte", id_utilisateur)
    if resultat == "inconnu":
        print("Ce pseudo n'existe pas.")
        print("1. Creer un compte")
        print("2. Continuer en anonyme")
        print("0. Retour a l'accueil")
        while True:
            choix = input("Votre choix : ").strip()
            if choix == "1":
                return ("inscription", None)
            if choix == "2":
                return ("anonyme", None)
            if choix == "0":
                return ("accueil", None)
            print("Choix invalide.")

def ecran_creer_compte(conn):
    print("\n=== CREER UN COMPTE ===")
    pseudo = input("Votre pseudo : ").strip()
    email = input("Votre email : ").strip()
    mdp = getpass("Mot de passe : ")

    if pseudo == "" or email == "" or mdp == "":
        print("Tous les champs sont obligatoires.")
        return "inscription"

    if creer_compte(conn, pseudo, email, mdp):
        print("Compte cree, vous pouvez vous connecter.")
        return "connexion"

    print("Ce pseudo ou cet email est deja utilise.")
    return "inscription"

def lancer_recherche():
         """ 
         Lance scripts/recherche.py et attend qu'il se termine
    sys.executable = le Python de uv, comme "uv run scripts/recherche.py"
       """
         subprocess.run([sys.executable, SCRIPT_RECHERCHE])

def main():
    conn = connexion()
    print("Chargement de l'index...")

    ecran = "accueil"
    id_utilisateur = None            # None = personne de connecte
    while ecran != "quitter":
        if ecran == "accueil":
            id_utilisateur = None    # revenir a l'accueil = se deconnecter
            ecran = ecran_accueil()
        elif ecran == "connexion":
            ecran, id_utilisateur = ecran_connexion(conn)
        elif ecran == "inscription":
            ecran = ecran_creer_compte(conn)
        elif ecran == "connecte" or ecran == "anonyme":
            lancer_recherche()
            ecran = "accueil"        # fin de la recherche : retour a l'accueil

    conn.close()
    print("Au revoir !")


main()