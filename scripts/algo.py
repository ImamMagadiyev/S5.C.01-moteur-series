import os

import numpy as np
#calcul du score TF d'un mot dans un document : càd le nombre d'occurrences du mot dans le document divisé par le nombre total de mots dans le document
def term_frequency(word,document):
    #on utilise la méthode count() pour compter le nombre d'occurrences du mot dans le document et on divise par le nombre total de mots dans le document pour obtenir la fréquence du mot
    return document.count(word) / len(document) 
tf = term_frequency 

#CaLcul DU SCORE IDF D'UN MOT DANS UN CORPUS : càd le logarithme du nombre total de documents divisé par le nombre de documents contenant le mot
#On passe en paramètre le mot que l'on cherche et le corpus càd une liste de documents dont chaque document est une liste de mots
def  inverse_document_frequency ( word, corpus ): 
    count_of_documents = len (corpus) + 1 #on récupere le nb de documents dans le corpus et on ajoute 1 pour éviter la division par zéro
    count_of_documents_with_word = sum ([ 1  for doc in corpus if word in doc]) + 1 #on compte le nombre de documents contenant le mot et on ajoute 1 pour éviter la division par zéro
    idf = np.log10(count_of_documents/count_of_documents_with_word) + 1 #on utilise le logarithme base 10 pour calculer le score IDF et on ajoute 1 pour éviter les valeurs négatives
    return idf # on retourne le résultat du calcul du score IDF
idf = inverse_document_frequency

#il ne nous reste plus qu'a calculer le score TF-IDF d'un mot dans un document par rapport à un corpus, càd le produit du score TF et du score IDF
def tf_idf(mot,document,corpus):
    tf_idf = tf(mot,document) * idf(mot,corpus)
    return tf_idf
#recupere le nom du repertoire dans lequel se trouve le projet
#quand on rappelle os.path.dirname deux fois, on remonte de deux niveaux dans l'arborescence des dossiers pour obtenir le chemin du répertoire racine du projet
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#on teste notre fonction sur un petit corpus de documents initialisé sous forme de liste, chaque string => 1 document
corpus_chemin = RACINE + "/data/corpus_propre" #on construit le chemin vers le fichier corpus.txt en utilisant le chemin du répertoire racine du projet 
liste = os.listdir(corpus_chemin) #on utilise la méthode listdir() pour lister les fichiers dans le répertoire corpus_propre
corpus_vf = {} #on initialise un dictionnaire vide pour stocker les documents du corpus
corpus_vo = {}
for fichier in liste:
    if fichier.lower().endswith("vf.txt"): #on vérifie si le fichier est en vo ou vf 
        nom = fichier.split(".")[0] #on récupère le nom du fichier sans l'extension
        with open(corpus_chemin + "/" + fichier, "r", encoding="utf-8") as f: #on ouvre chaque fichier en mode lecture avec l'encodage utf-8
            corpus_vf[nom] = f.read().split() ##on lit le contenu du fichier avant de le splitter en mots et de l'ajouter comme valeur dans le dictionnaire corpus_vf
    elif fichier.lower().endswith("vo.txt"): #on vérifie si le fichier est en vo ou vf 
        name = fichier.split(".")[0] #on récupère le nom du fichier sans l'extension
        with open(corpus_chemin + "/" + fichier, "r", encoding="utf-8") as f: #on ouvre chaque fichier en mode lecture avec l'encodage utf-8
            corpus_vo[name] = f.read().split() #on lit le contenu du fichier avant de le splitter en mots et de l'ajouter comme valeur dans le dictionnaire corpus_vo
options = {"1": "français", "2": "anglais"}
choix = input("1 = français, 2 = anglais : ")
langue = options.get(choix)
target_word = input("Quel mot voulez-vous rechercher dans le corpus ? ") 
print("----------------------------------------------------------------------------------------------")
print("--------------------------------------TEST VERSION 1 TF-IDF------------------------------------")
print("----------------------------------------------------------------------------------------------")
print("VERSION DE TEST 1- INDEXATION VRAI DATASET")


print ( "recherche du mot '%s' en %s" %(target_word, langue)) 

if langue == "français":
    for i, (cle, valeur) in enumerate(corpus_vf.items()):
        tf_score = tf(target_word, valeur) #on calcule le score TF du mot cible dans le document courant
        idf_score = idf(target_word, corpus_vf)
        tf_idf_score = tf_idf(target_word, valeur, corpus_vf)
        print ( "document %s: '%s'\n score tf: %s\n score idf: %s\n score tf_idf:%s" %(i, cle, tf_score, idf_score, tf_idf_score)) 
        print ( "-" * 30 )
elif langue == "anglais":
    for i, (cle, valeur) in enumerate(corpus_vo.items()):
        tf_score = tf(target_word, valeur) #on calcule le score TF du mot cible dans le document courant
        idf_score = idf(target_word, corpus_vo)
        tf_idf_score = tf_idf(target_word, valeur, corpus_vo)
        print ( "document %s: '%s'\n score tf: %s\n score idf: %s\n score tf_idf:%s" %(i, cle, tf_score, idf_score, tf_idf_score)) 
        print ( "-" * 30 )
