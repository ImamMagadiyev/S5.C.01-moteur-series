# SAE S5.C.01
# Moteur de recommandation series similaires par similarite cosinus
# chaque serie est un vecteur {mot: poids} les vecteurs sont calcules une 
# seule fois au demarrage a partir des frequences de la table apparait 

import math 
import sqlite3

from moteur_series.config import BASE

# Un mot present dans moins de series est ignore
NB_SERIES_MIN = 3

# On ne garde que les NB_MOTS_MAX mots les plus forts de chaque serie
NB_MOTS_MAX = 1000

# Penalite des series "aimants" : nombre de voisines prises pour la moyenne
NB_VOISINS = 10

def charger_vecteurs(langue="vf"):
    """
    Renvoie {titre: {id_mot: poids}}, chaque vecteur ayant une longueur de 1
    poids = (1 + log(frequence)) * log(nb_series / nb_series_du_mot)
    seuls les NB_MOTS_MAX mots les plus forts de chaque serie sont gardes
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

    # 3b. Toutes les series a egalite : on garde seulement leurs NB_MOTS_MAX
    # mots les plus forts. Sans ca, une longue serie (ncis : 25 000 mots contre
    # 2 000 pour whitechapel) partage des mots avec tout le monde et ressort
    # dans presque toutes les recommandations
    for titre in vecteurs:
        mots_tries = sorted(vecteurs[titre].items(), key=lambda paire: paire[1], reverse=True)
        vecteurs[titre] = dict(mots_tries[:NB_MOTS_MAX])

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


def calculer_similarites(vecteurs):
    """
    Calcule une seule fois, au demarrage, la similarite de TOUTES les paires
    de series (environ 0,5 s). Renvoie {titre: {autre_titre: score}}

    score(A, B) = 2 x cosinus(A, B) - moyenne_voisins(A) - moyenne_voisins(B)
    moyenne_voisins(A) = cosinus moyen de A avec ses NB_VOISINS series les plus proches
    Une serie proche de tout le monde (une serie "aimant") a une moyenne elevee :
    elle recule dans les recommandations des autres. Le score peut etre negatif,
    seul l'ordre compte
    """
    titres = list(vecteurs)

    # 1. Cosinus de chaque paire. Les vecteurs ont une longueur de 1 : le cosinus
    # est la somme des produits des poids des mots communs. Il est symetrique,
    # on le calcule une seule fois pour A-B et B-A
    cosinus = {}
    for titre in titres:
        cosinus[titre] = {}
    for i in range(len(titres)):
        titre_a = titres[i]
        vecteur_a = vecteurs[titre_a]
        for j in range(i + 1, len(titres)):
            titre_b = titres[j]
            vecteur_b = vecteurs[titre_b]
            produit = 0
            for id_mot, poids in vecteur_a.items():
                if id_mot in vecteur_b:
                    produit = produit + poids * vecteur_b[id_mot]
            cosinus[titre_a][titre_b] = produit
            cosinus[titre_b][titre_a] = produit

    # 2. Pour chaque serie, cosinus moyen avec ses NB_VOISINS plus proches
    moyenne_voisins = {}
    for titre in titres:
        meilleurs = sorted(cosinus[titre].values(), reverse=True)[:NB_VOISINS]
        moyenne_voisins[titre] = sum(meilleurs) / len(meilleurs)

    # 3. Score final avec la penalite des aimants
    similarites = {}
    for titre_a in titres:
        similarites[titre_a] = {}
        for titre_b, valeur in cosinus[titre_a].items():
            similarites[titre_a][titre_b] = (
                2 * valeur - moyenne_voisins[titre_a] - moyenne_voisins[titre_b]
            )
    return similarites


def series_similaires(titre, similarites, nb_resultats=10):
    """
    Renvoie les series les plus proches de titre sous la forme
    [(titre, score), ...] de la plus proche a la moins proche
    similarites vient de calculer_similarites() : ici on ne fait que trier
    """
    if titre not in similarites:
        return []   # serie inconnue
    classement = sorted(similarites[titre].items(), key=lambda paire: paire[1], reverse=True)
    return classement[:nb_resultats]


def charger_notes(id_utilisateur):
    """
    Renvoie les notes d'un utilisateur sous la forme {titre: note de 1 a 5}
    (table Noter). Dictionnaire vide si l'utilisateur n'a rien note
    """
    connexion = sqlite3.connect(BASE)
    lignes = connexion.execute(
        "SELECT Serie.Titre, Noter.note FROM Noter"
        " JOIN Serie ON Serie.ID_Serie = Noter.fk_serie"
        " WHERE Noter.fk_utilisateur = ?",
        (id_utilisateur,),
    )
    notes = {}
    for titre, note in lignes:
        notes[titre] = note
    connexion.close()
    return notes


def noter_serie(conn, id_utilisateur, titre, note):
    """
    Enregistre la note (de 1 a 5) d'un utilisateur pour une serie (table Noter)
    Si la serie etait deja notee, l'ancienne note est remplacee
    Renvoie True si la note est enregistree, False si la serie n'existe pas
    """
    ligne = conn.execute("SELECT ID_Serie FROM Serie WHERE Titre = ?", (titre,)).fetchone()
    if ligne is None:
        return False   # serie inconnue

    id_serie = ligne[0]
    # La cle primaire (fk_utilisateur, fk_serie) interdit deux notes pour la
    # meme serie : INSERT OR REPLACE remplace alors l'ancienne ligne
    conn.execute(
        "INSERT OR REPLACE INTO Noter (fk_serie, fk_utilisateur, note) VALUES (?, ?, ?)",
        (id_serie, id_utilisateur, note),
    )
    conn.commit()
    return True


def recommander_selon_notes(notes, similarites, nb_resultats=10):
    """
    notes : {titre: note de 1 a 5} donnees par un utilisateur
    Renvoie [(titre, score), ...] parmi les series qu'il n'a PAS encore notees

    score(S) = somme, pour chaque serie notee R, de (note(R) - 3) x similarite(S, R)
    Une note de 5 attire (+2), 4 attire un peu (+1), 3 est neutre (0),
    2 repousse un peu (-1), 1 repousse (-2) : les series proches d'une serie
    detestee descendent dans le classement
    """
    scores = {}
    for titre_note, note in notes.items():
        if titre_note not in similarites:
            continue   # serie inconnue : ignoree
        poids = note - 3
        if poids == 0:
            continue   # note neutre : elle n'apporte rien
        for titre, similarite in similarites[titre_note].items():
            if titre in notes:
                continue   # deja notee : on ne la recommande pas
            if titre not in scores:
                scores[titre] = 0
            scores[titre] = scores[titre] + poids * similarite

    classement = sorted(scores.items(), key=lambda paire: paire[1], reverse=True)
    return classement[:nb_resultats]