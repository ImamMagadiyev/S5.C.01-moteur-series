import os

import numpy as np
#calcul du score TF d'un mot dans un document : càd le nombre d'occurrences du mot dans le document divisé par le nombre total de mots dans le document
def term_frequency(word,document):
    #on utilise la méthode count() pour compter le nombre d'occurrences du mot dans le document et on divise par le nombre total de mots dans le document pour obtenir la fréquence du mot
    return document.count(word) / len(document) 
tf = term_frequency 

Document = "my dog is the best dog that ever was a pet dog"
document_words = Document.split() #on utilise la méthode split afin de séparer le texte en mots et de créer une liste de mots
print("Score TF du Chien: ", term_frequency("dog",document_words))# on applique la méthode sur le mot "dog"
print("Score TF de animal: ", term_frequency("pet",document_words))# on applique la methode sur le mot "pet" 

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
corpus_vf = [] #on initialise une liste vide pour stocker les documents du corpus
corpus_vo = []
liste_nom_fic_vf =[]
liste_nom_fic_vo = []
for fichier in liste:
    if fichier.lower().endswith("vf.txt"): #on vérifie si le fichier est en vo ou vf 
        liste_nom_fic_vf.append(fichier) #on ajoute le nom du fichier à la liste des noms de series vf
        with open(corpus_chemin + "/" + fichier, "r", encoding="utf-8") as f: #on ouvre chaque fichier en mode lecture avec l'encodage utf-8
            corpus_vf.append(f.read().split()) ##on lit le contenu du fichier avant de le splitter en mots et de l'ajouter à la liste corpus_vf
    elif fichier.lower().endswith("vo.txt"): #on vérifie si le fichier est en vo ou vf 
        liste_nom_fic_vo.append(fichier) #on ajoute le nom du fichier à la liste des noms de series vo
        with open(corpus_chemin + "/" + fichier, "r", encoding="utf-8") as f: #on ouvre chaque fichier en mode lecture avec l'encodage utf-8
            corpus_vo.append(f.read().split()) #on lit le contenu du fichier avant de le splitter en mots et de l'ajouter à la liste corpus_vo
target_word = "ile"
print("----------------------------------------------------------------------------------------------")
print("--------------------------------------TEST VERSION 1 TF-IDF------------------------------------")
print("----------------------------------------------------------------------------------------------")
print("VERSION DE TEST 1- INDEXATION VRAI DATASET")
print ( "recherche du mot '%s'" %target_word) 
for i, serie in enumerate(liste_nom_fic_vf):  #on utilise un enumerate pour faciliter l'affichage de l'index du doc + son contenu
    tf_score = tf(target_word, corpus_vf[i]) #on calcule le score TF du mot cible dans le document courant
    idf_score = idf(target_word, corpus_vf)
    tf_idf_score = tf_idf(target_word, corpus_vf[i], corpus_vf)
    print ( "document %s: '%s'\n score tf: %s\n score idf: %s\n score tf_idf:%s" %(i, serie, tf_score, idf_score, tf_idf_score)) 
    print ( "-" * 30 )

print("----------------------------------------------------------------------------------------------" \
"--------------------------------------TEST VERSION 2 TF-IDF vo ------------------------------------" \
"")
for i, serie in enumerate(liste_nom_fic_vo):  #on utilise un enumerate pour faciliter l'affichage de l'index du doc + son contenu
    tf_score = tf(target_word, corpus_vo[i]) #on calcule le score TF du mot cible dans le document courant
    idf_score = idf(target_word, corpus_vo)
    tf_idf_score = tf_idf(target_word, corpus_vo[i], corpus_vo)
    print ( "document %s: '%s'\n score tf: %s\n score idf: %s\n score tf_idf:%s" %(i, serie, tf_score, idf_score, tf_idf_score)) 
    print ( "-" * 30 )