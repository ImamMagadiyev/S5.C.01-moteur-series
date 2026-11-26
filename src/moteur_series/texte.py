# SAE S5.C.01
# Nettoyage du texte transforme un texte brut en liste de mots utiles
# Utilise pour le corpus (scripts/preparation/nettoyage.py) et pour les requetes
# de recherche les deux doivent subir exactement le meme traitement 

import re 
import unicodedata

# Mots trop frequents pour distinguer une serie d'une autre
STOP_WORDS_FR = {
    "accord", "ai", "aller", "allez", "allons", "alors", "apres", "as",
    "assez", "au", "aussi", "aux", "avaient", "avait", "avant", "avec",
    "avez", "avoir", "avons", "bah", "ben", "bien", "bon", "ca",
    "car", "ce", "cela", "celle", "celles", "celui", "ces", "cet",
    "cette", "ceux", "chez", "chose", "comme", "comment", "dans", "de",
    "deja", "depuis", "des", "desole", "devez", "dire", "dis", "dit",
    "dois", "doit", "donc", "dont", "du", "elle", "elles", "encore",
    "entre", "est", "et", "etaient", "etait", "ete", "etes", "etre",
    "euh", "faire", "fais", "fait", "faut", "font", "hein", "ici",
    "il", "ils", "jamais", "je", "juste", "la", "le", "les",
    "leur", "leurs", "lui", "ma", "maintenant", "mais", "me", "meme",
    "merci", "mes", "moi", "mon", "ne", "non", "nos", "notre",
    "nous", "on", "ont", "ou", "ouais", "oui", "par", "parce",
    "pardon", "pas", "personne", "peu", "peut", "peuvent", "peux", "plus",
    "pour", "pourquoi", "pouvez", "pouvoir", "quand", "que", "quelque", "qui",
    "quoi", "rien", "sa", "sais", "sait", "sans", "savez", "savoir",
    "se", "sera", "seront", "ses", "sommes", "son", "sont", "sous",
    "suis", "sur", "ta", "te", "tes", "toi", "ton", "toujours",
    "tous", "tout", "toute", "toutes", "tres", "trop", "tu", "un",
    "une", "va", "vais", "vas", "vers", "veut", "veux", "voir",
    "vois", "vont", "vos", "votre", "voulez", "vouloir", "vous", "vraiment",
    "vu",
}

STOP_WORDS_EN = {
    "a", "about", "after", "again", "all", "am", "an", "and",
    "any", "are", "at", "be", "been", "before", "being", "between",
    "but", "can", "could", "did", "do", "does", "done", "down",
    "during", "each", "every", "for", "from", "gonna", "gotta", "had",
    "has", "have", "he", "her", "here", "hey", "him", "his",
    "hmm", "how", "huh", "i", "in", "into", "is", "it",
    "its", "just", "may", "me", "might", "more", "most", "must",
    "my", "never", "no", "nor", "not", "now", "of", "off",
    "oh", "ok", "okay", "on", "only", "or", "other", "our",
    "out", "over", "shall", "she", "should", "so", "some", "than",
    "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "those", "to", "too", "uh", "under", "up", "us",
    "very", "wanna", "was", "we", "were", "what", "when", "where",
    "which", "who", "whom", "why", "will", "with", "without", "would",
    "yeah", "yep", "yes", "you", "your",
}

STOP_WORDS = STOP_WORDS_FR | STOP_WORDS_EN

# ----------------------------------
# Fonction pour enlever les accents 
# ----------------------------------
def supprimer_accents(texte):
    """
    Transforme les lettres accentuées en lettres simples
    """
    decompose = unicodedata.normalize("NFD", texte)
    resultat = ""
    for caractere in decompose:
        if unicodedata.category(caractere) != "Mn": # Mn = accent
            resultat = resultat + caractere
    return resultat

def nettoyer_texte(texte):
    """
    Transforme un texte brut en une liste de mots utiles
    """

    # Enlever les balises <i>, </i> et {\an8}
    texte = re.sub(r"<[^>]*>", "", texte)
    texte = re.sub(r"\{[^}]*\}", " ", texte)

    # Miniscules, puis suppression des accents
    texte = texte.lower()
    texte = supprimer_accents(texte)

    # Enlever les adresses des teams de sous-titrage
    texte = re.sub(r"[a-z0-9._-]+\.(com|fr|net|org)", " ", texte)

    # Uniformiser les apostrophes
    texte = texte.replace("\u2019", "'").replace("`", "'")

    # Enlever les mots composes AVANT de couper sur l'apostrophe
    # sinon "quelqu'un" donnerait les faut mots "quelqu" et "un"
    for mot_compose in ["aujourd'hui", "quelqu'un", "quelqu'une",
                        "d'accord", "jusqu'a", "lorsqu'", "puisqu'", "quoiqu'"]:
        texte = texte.replace(mot_compose, " ")

    # Couper les elisions : l'attentat -> attentat
    texte = re.sub(r"\b[ldjnmtscqu]{1,2}'", " ", texte)

    # Apostrophes restantes, a l'interieur d'un mot 
    # On garde les morceaux 
    mot_colles = []
    for mot in re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)+", texte):
        mot_colles.append(mot.replace("'", ""))
    texte = texte + " " + " ".join(mot_colles)

    # Ne garder que les lettres et les chiffres
    texte = re.sub(r"[^a-z0-9]", " ", texte)

    # garder les mots utiles
    mots_utiles = []
    for mot in texte.split():

        if mot in STOP_WORDS:
            continue

        if mot.isdigit():
            if len(mot) >= 2:        # on garde 42, 815, 1976
                mots_utiles.append(mot)
        elif len(mot) > 2:
            mots_utiles.append(mot)

    return mots_utiles