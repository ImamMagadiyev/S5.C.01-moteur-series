# SAE S5.C.01
# Moteur de recommandation series similaires par similarite cosinus
# chaque serie est un vecteur {mot: poids} les vecteurs sont calcules une 
# seule fois au demarrage a partir des frequences de la table apparait 

import math 
import sqlite3

from moteur_series.config import BASE

# Un mot present dans moins de series est ignore
NB_SERIES_MIN = 3

def charger_vecteurs(langue="vf"):
    """
    Renvoie {titre: {id_mot: poids}}, chaque vecteur ayant une longueur de 1
    poids = (1 + log(frequence)) * log(nb_series / nb_series_du_mot)
    a appeler une seule fois au demarrage
    """
    connexion = sqlite3.connect(BASE)

    titre_de_la_serie = {}
    for id_serie, titre in connexion.execute("SELECT ID_Serie, Titre FROM Serie"):
        titre_de_la_serie[id_serie] = titre

    # 1. Frequence brutes regroupees par mot : {id_mot: {titre: frequence}}
    frequences = {}
    lignes = connexion.execute(
        "SELECT fk_mot, fk_serie, frequence FROM apparait WHERE langue = ?", (langue,)
    )
    for id_mot, id_serie, frequence in lignes:
        if id_mot not in frequences:
            frequences[id_mot] = {}
        frequences[id_mot][titre_de_la_serie[id_serie]] = frequence
    connexion.close()

    # 2. Nombre de series qui ont au moins un mot dans cette langue 
    series_presentes = set()
    for series_du_mot in frequences.values():
        for titre in series_du_mot:
            series_presentes.add(titre)
    nb_series = len(series_presentes)

    # 3. Poids TF-IDF de chaque mot dans chaque serie 
    vecteurs = {}
    for id_mot, series_du_mot in frequences.items():
        nb_series_du_mot = len(series_du_mot)
        if nb_series_du_mot < NB_SERIES_MIN:
            continue
        # idf = 0 pour un mot present partout (pere, temps) il ne compte plus 
        idf = math.log(nb_series / nb_series_du_mot)
        if idf == 0:
            continue
        for titre, frequence in series_du_mot.items():
            if titre not in vecteurs:
                vecteurs[titre] = {}
            # 1 + log un mot dit 1000 fois ne compte pas 1000 fois plus 
            vecteurs[titre][id_mot] = (1 + math.log(frequence)) * idf

    # 4. On divise chaque vecteur par sa longueur (norme) une fois pour toutes
    # le cosinus entre deux series se reduit alors a une somme de produits
    for titre, vecteur in vecteurs.items():
        somme = 0
        for poids in vecteur.values():
            somme = somme + poids * poids
        norme = math.sqrt(somme)
        for id_mot in vecteur:
            vecteur[id_mot] = vecteur[id_mot] / norme

    return vecteurs


def series_similaires(titre, vecteurs, nb_resultats=10):
    """
    Renvoie les series les plus proches de titre sous la forme 
    [(titre, similarite), ...] de la plus proche a la moins proche 
    similarite cosinus 0 = aucun mot en commun 1 = vecteurs identiques
    """
    if titre not in vecteurs:
        return []   # serie inconnue
    vecteur = vecteurs[titre]

    scores = []
    for autre_titre, autre_vecteur in vecteurs.items():
        if autre_titre == titre:
            continue    # on ne recommande pas la serie elle-meme
        # les vecteurs ont une longueur de 1
        # le cosinus est la somme des produits des poids des mots communs
        produit = 0
        for id_mot, poids in vecteur.items():
            if id_mot in autre_vecteur:
                produit = produit + poids * autre_vecteur[id_mot]
        scores.append((autre_titre, produit))

    scores.sort(key=lambda paire: paire[1], reverse=True)
    return scores[:nb_resultats]