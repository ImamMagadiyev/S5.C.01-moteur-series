import os
import re
import unicodedata


# Chemins, relatifs au projet (jamais de C:\Users\... en dur)
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RACINE, "data", "sous-titres")
SORTIE = os.path.join(RACINE, "data", "corpus_propre")


#-----------------------------------
# Fonction pour enlever les accents 
# ----------------------------------

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

MOTS_CREDITS = [
    ".com", ".net", ".org", "forom", "presynchro", "relecture",
    "soustitre", "sous-titre", "subtitle", "synchro", "traduction",
    "transcript", "www.",
]


STOP_WORDS = STOP_WORDS_FR | STOP_WORDS_EN


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
                        "d'accord", "jusqu'a", "lorsqu'"]:
        texte = texte.replace(mot_compose, " ")

    # Couper les elisions : l'attentat -> attentat
    texte = re.sub(r"\b[ldjnmtscqu]{1,2}'", " ", texte)

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

print("Corpus :", CORPUS)

if not os.path.exists(SORTIE):
    os.makedirs(SORTIE)

nombre_series = 0

for serie in sorted(os.listdir(CORPUS)):

    dossier_serie = os.path.join(CORPUS, serie)
    if not os.path.isdir(dossier_serie):
        continue

    mots_vf = []
    mots_vo = []    
    episodes_deja_lus = []

    # Parcourir tous les sous_dossiers de la serie 
    for chemin, dossiers, fichiers in os.walk(dossier_serie):
        for fichier in fichiers:

            if not fichier.lower().endswith(".srt"):
                continue

            # Meme episode en plusieurs versions : on n'en garde qu'une 
            if fichier.lower() in episodes_deja_lus:
                continue
            episodes_deja_lus.append(fichier.lower())

            # Lire le fichier (les sous-titres sont en cp1252, pas en utf-8)
            chemin_fichier = os.path.join(chemin, fichier)
            try: 
                contenu = open(chemin_fichier, encoding="cp1252").read()
            except Exception:
                try:
                    contenu = open(chemin_fichier, encoding="utf-8", errors="ignore").read()

                except Exception:
                    continue

            # Garder uniquement les repliques :
            # On jette les numeros et les lignes de timecode
            repliques = []
            for ligne in contenu.splitlines():
                ligne = ligne.strip()
                if ligne == "":
                    continue
                if ligne.isdigit():
                    continue
                if "-->" in ligne:
                    continue
                ligne_minuscule = ligne.lower()
                est_un_credit = False
                for mot in MOTS_CREDITS:
                    if mot in ligne_minuscule:
                        est_un_credit = True
                if est_un_credit:
                    continue
                repliques.append(ligne)

            texte_episode = " ".join(repliques)
            mots_episode = nettoyer_texte(texte_episode)

            # La langue se devine dans le chemin ou le nom du fichier 
            if "vo" in (chemin + fichier).lower():
                mots_vo = mots_vo + mots_episode
            else:
                mots_vf = mots_vf + mots_episode

    # Ecrire le resultat
    if len(mots_vf) == 0 and len(mots_vo) == 0:
        print(serie, ": aucun sous-titre exploitable")
        continue

    if len(mots_vf) > 0:
        fichier_vf = os.path.join(SORTIE, serie + ".vf.txt")
        open(fichier_vf, "w", encoding="utf-8").write(" ".join(mots_vf))

    if len(mots_vo) > 0:
        fichier_vo = os.path.join(SORTIE, serie + ".vo.txt")
        open(fichier_vo, "w", encoding="utf-8").write(" ".join(mots_vo))

    nombre_series = nombre_series + 1
    print(serie, ":", len(episodes_deja_lus), "episodes,", 
          len(mots_vf), "mots VF,", len(mots_vo), "mots VO")

print()
print(nombre_series, "series traitees. Sortie :", SORTIE)