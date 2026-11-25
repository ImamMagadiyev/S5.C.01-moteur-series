# SAE S5.C.01
# Moteur de recherche l'index est chargé une seule fois en mémoire au démarrage,
# ensuite chaque requête n'est qu'un calcul sur des dictionnaires (pas de SQL)

import sqlite3

from moteur_series.config import BASE
from moteur_series.texte import nettoyer_texte

def charger_index(langue="vf"):
    """
    Lit la table apparait et renvoie {mot: {titre_serie: poids}}
    À appeler une seule fois, au démarrage
    On lit les trois tables séparement une jointure SQL sur 1.4 million de 
    lignes est beaucoup plus lente (envrion 15 s contre 2 s)
    """
    connexion = sqlite3.connect(BASE)

    # Id -> texte, pour traduire les identifiants de la table apparait
    libelle_du_mot = {}
    for id_mot, libelle in connexion.execute("SELECT Id_MOT, libelle FROM Mot"):
        libelle_du_mot[id_mot] = libelle

    titre_de_la_serie = {}
    for id_serie, titre in connexion.execute("SELECT ID_Serie, Titre FROM Serie"):
        titre_de_la_serie[id_serie] = titre

    index = {}
    lignes = connexion.execute(
        "SELECT fk_MOT, fk_serie, poids FROM apparait WHERE langue = ?", (langue,)
    )
    for id_mot, id_serie, poids in lignes:
        mot = libelle_du_mot[id_mot]
        if mot not in index:
            index[mot] = {}
        index[mot][titre_de_la_serie[id_serie]] = poids

    connexion.close()
    return index

def rechercher(requete, index, nb_resultats=10):
    """
    Renvoie les séries les plus pertinentes pour la requête sous la forme
    [(titre, score), ...] de la meilleure à la moins bonne
    Score d'une série = somme, pour chaque mot de la requête, de son poids
    dans la série divisé par le plus gros poids de ce mot (entre 0 et 1)    
    """
    # Même nettoyage que le corpus (accents, stop-words...), sinon rien ne correspond
    mots = nettoyer_texte(requete)

    scores = {}
    for mot in mots:
        if mot not in index:
            continue   # mot absent du corpus : il n'apporte rien
        series_du_mot = index[mot]
        # On divise par le plus gros poids de ce mot : chaque mot de la requête
        # apporte au plus 1 point, un mot fréquent ne peut plus écraser les autres
        poids_max = max(series_du_mot.values())   # renvoie le plus gros poids
        for titre, poids in series_du_mot.items():
            if titre not in scores:
                scores[titre] = 0
            scores[titre] = scores[titre] + poids / poids_max
            
    classement = sorted(scores.items(), key=lambda paire: paire[1], reverse=True)
    return classement[:nb_resultats]