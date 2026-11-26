import numpy as np
from collections import Counter

def term_frequency(word, document):
    return document.count(word) / len(document)
tf = term_frequency

def inverse_document_frequency(word, corpus):
    count_of_documents = len(corpus) + 1
    count_of_documents_with_word = sum([1 for doc in corpus if word in doc]) + 1
    return np.log10(count_of_documents / count_of_documents_with_word) + 1
idf = inverse_document_frequency

def tf_idf(mot, document, corpus):
    return tf(mot, document) * idf(mot, corpus)


def calculer_document_frequencies(corpus):
    """Une seule passe sur tout le corpus : {mot: nombre_de_documents_le_contenant}."""
    df = Counter()
    for document in corpus.values():
        for mot in set(document):  # set() : chaque mot compte une fois par document, pas par occurrence
            df[mot] += 1
    return df

def idf_depuis_df(df_mot, nb_documents):
    return np.log10((nb_documents + 1) / (df_mot + 1)) + 1

def top_mots_serie(document, document_frequencies, nb_documents, n=20):
    """Calcule le tf-idf de chaque mot unique de `document`, renvoie les n meilleurs
            sous forme de (mot, poids, frequence)."""
    compteur = Counter(document)
    scores = []
    for mot, frequence in compteur.items():
        tf_score = frequence / len(document)
        idf_score = idf_depuis_df(document_frequencies.get(mot, 0), nb_documents)
        poids = tf_score * idf_score
        scores.append((mot, poids, frequence, idf_score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]