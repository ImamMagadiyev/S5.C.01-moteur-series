from config import CORPUS_CHEMIN
from corpus import charger_corpus
from tfidf import calculer_document_frequencies, top_mots_serie
from database import connexion, inserer_serie, obtenir_ou_creer_mot, inserer_apparait

def peupler_langue(conn, corpus, langue, id_series):
    document_frequencies = calculer_document_frequencies(corpus)
    nb_documents = len(corpus)
    for nom_serie, mots in corpus.items():
        print(f"Traitement de {nom_serie} ({langue})...")
        id_serie = id_series[nom_serie]
        top20 = top_mots_serie(mots, document_frequencies, nb_documents, n=20)
        for mot, poids, frequence, idf_score in top20:
            id_mot = obtenir_ou_creer_mot(conn, mot, idf_score)
            inserer_apparait(conn, id_mot, id_serie, langue, poids, frequence)
        conn.commit()
        print(f"{langue} - {nom_serie} : {len(top20)} mots insérés")

def main():
    corpus_vf = charger_corpus(CORPUS_CHEMIN, "vf.txt")
    corpus_vo = charger_corpus(CORPUS_CHEMIN, "vo.txt")

    conn = connexion()
    toutes_series = set(corpus_vf.keys()) | set(corpus_vo.keys())
    id_series = {nom: inserer_serie(conn, nom) for nom in toutes_series}
    conn.commit()

    peupler_langue(conn, corpus_vf, "vf", id_series)
    peupler_langue(conn, corpus_vo, "vo", id_series)

    conn.close()
    print("Indexation terminée.")

if __name__ == "__main__":
    main()