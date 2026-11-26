# SAE S5.C.01
# Indexation : remplit les tables Mot, Serie et apparait (TF-IDF) a partir de data/corpus_propre
# Relancable : l'index est vide au debut
# Usage : uv run scripts/preparation/indexation/main.py

from moteur_series.config import CORPUS_PROPRE
from corpus import charger_corpus
from tfidf import calculer_document_frequencies, top_mots_serie
from database import  vider_index, obtenir_ou_creer_serie, obtenir_ou_creer_mot, inserer_apparait
from moteur_series.base import connexion

def peupler_langue(conn, corpus, langue, id_series):
    document_frequencies = calculer_document_frequencies(corpus)
    nb_documents = len(corpus)
    for nom_serie, mots in corpus.items():
        id_serie = id_series[nom_serie]
        # n=None : on garde TOUS les mots de la série, sinon la recherche
        # ne trouve que les 20 mots les plus caractéristiques
        mots_serie = top_mots_serie(mots, document_frequencies, nb_documents, n=None)
        for mot, poids, frequence, idf_score in mots_serie:
            id_mot = obtenir_ou_creer_mot(conn, mot, idf_score)
            inserer_apparait(conn, id_mot, id_serie, langue, poids, frequence)
        conn.commit()
        print(f"{langue} - {nom_serie} : {len(mots_serie)} mots insérés")

def main():
    corpus_vf = charger_corpus(CORPUS_PROPRE, "vf.txt")
    corpus_vo = charger_corpus(CORPUS_PROPRE, "vo.txt")

    conn = connexion()
    vider_index(conn)

    toutes_series = set(corpus_vf.keys()) | set(corpus_vo.keys())
    id_series = {}
    for nom in sorted(toutes_series):
        id_series[nom] = obtenir_ou_creer_serie(conn, nom)
    conn.commit()

    peupler_langue(conn, corpus_vf, "vf", id_series)
    peupler_langue(conn, corpus_vo, "vo", id_series)

    conn.close()
    print("Indexation terminée.")

if __name__ == "__main__":
    main()