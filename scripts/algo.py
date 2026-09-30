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

#CaLCUL DU SCORE IDF D'UN MOT DANS UN CORPUS : càd le logarithme du nombre total de documents divisé par le nombre de documents contenant le mot
#On passe en paramètre le mot que l'on cherche et le corpus càd une liste de documents dont chaque document est une liste de mots
def  inverse_document_frequency ( word, corpus ): 
    count_of_documents = len (corpus) + 1 #on récupere le nb de documents dans le corpus et on ajoute 1 pour éviter la division par zéro
    count_of_documents_with_word = sum ([ 1  for doc in corpus if word in doc]) + 1 #on compte le nombre de documents contenant le mot et on ajoute 1 pour éviter la division par zéro
    idf = np.log10(count_of_documents/count_of_documents_with_word) + 1 #on utilise le logarithme base 10 pour calculer le score IDF et on ajoute 1 pour éviter les valeurs négatives
    return idf # on retourne le résultat du calcul du score IDF
idf = inverse_document_frequency

#il ne nous reste pluq qu'a calculer le score TF-IDF d'un mot dans un document par rapport à un corpus, càd le produit du score TF et du score IDF
def tf_idf(mot,document,corpus):
    tf_idf = tf(mot,document) * idf(mot,corpus)
    return tf_idf

#recupere le nom du repertoire dans lequel se trouve le projet
#quand on rappelle os.path.dirname deux fois, on remonte de deux niveaux dans l'arborescence des dossiers pour obtenir le chemin du répertoire racine du projet
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#on teste notre fonction sur un petit corpus de documents initialisé sous forme de liste, chaque string => 1 document
corpus_unsplit = [ 
     "Mon chien est très bon au jeu de la balle" , 
    "J'avais un chien qui ne ressemblait pas vraiment à un chien, mais c'en était un" , 
    "chien lapin chat lapin coq chien cochon chèvre cheval chien chien chat vache otarie oiseau pigeon pingouins et baleines et coffres au trésor et quels autres objets aléatoires peuvent figurer dans ce long document, je me demande" , 
    "J'ai un chat" , 
    "J'ai une chèvre" , 
    "Pourquoi tout le monde parle de ses animaux de compagnie" , 
    "J'ai un zèbre" , 
    "Tu n'as pas de zèbre, Timmy"
 ] 

corpus = [c.split() for c in corpus_unsplit] #on split chaque document en mots
target_word = "chien"
print("----------------------------------------------------------------------------------------------")
print("--------------------------------------TEST VERSION 1 TF-IDF------------------------------------")
print("----------------------------------------------------------------------------------------------")
print("VERSION DE TEST SUR UN PETIT CORPUS -- UN PETIT TEXTE DE TEST")
print ( "recherche du mot '%s'" %target_word) 
for i, document in enumerate(corpus):  #on utilise un enumerate pour faciliter l'affichage de l'index du doc + son contenu
    tf_score = tf(target_word, document)
    idf_score = idf(target_word, corpus)
    tf_idf_score = tf_idf(target_word, document, corpus)
    print ( "document %s: '%s'\n score tf: %s\n score idf: %s\n score tf_idf:%s" %(i, document, tf_score, idf_score, tf_idf_score)) 
    print ( "-" * 30 )