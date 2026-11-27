# SAE S5.C.01
# Ecrans des series : recherche par mots-cles, series similaires
# Accessibles avec ou sans compte (noter n'est propose qu'aux connectes)

import time

from moteur_series.interface.saisies import demander_titre, proposer_de_noter
from moteur_series.interface.terminal import (
    GRAS, GRIS, JAUNE, ROUGE, afficher_entete, afficher_resultats, couleur, saisir,
)
from moteur_series.moteurs.recherche import rechercher
from moteur_series.moteurs.recommandation import series_similaires


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
