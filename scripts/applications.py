# SAE S5.C.01
# Application en ligne de commande : comptes, recherche, notes
# Usage : uv run scripts/applications.py
# Les ecrans sont dans src/moteur_series/interface/ ; ici : le menu et la
# boucle qui passe d'un ecran a l'autre

import os
import time

from moteur_series.donnees.base import connexion
from moteur_series.config import BASE
from moteur_series.interface.ecrans_compte import ecran_accueil, ecran_connexion, ecran_creer_compte
from moteur_series.interface.ecrans_notes import ecran_mes_recommandations, ecran_noter
from moteur_series.interface.ecrans_series import ecran_recherche, ecran_similaires
from moteur_series.interface.terminal import (
    CYAN, GRIS, ROUGE, afficher_entete, annoncer, choisir, couleur,
)
from moteur_series.moteurs.recherche import charger_index
from moteur_series.moteurs.recommandation import calculer_similarites, charger_vecteurs


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
