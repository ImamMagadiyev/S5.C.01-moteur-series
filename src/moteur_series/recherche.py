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
    Score d'une série = somme des poids des mots de la requête qu'elle contient
    """
    # Même nettoyage que le corpus (accents, stop-words...), sinon rien ne correspond
    mots = nettoyer_texte(requete)

    scores = {}
    for mot in mots:
        if mot not in index:
            continue   # mot absent du corpus : il n'apporte rien
        for titre, poids in index[mot].items():
            if titre not in scores:
                scores[titre] = 0
            scores[titre] = scores[titre] + poids

    classement = sorted(scores.items(), key=lambda paire: paire[1], reverse=True)
    return classement[:nb_resultats]