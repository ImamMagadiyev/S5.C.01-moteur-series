import codecs
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

# Mots-outils tres frequents qui n'existent que dans une des deux langues 
# ils servent a reconnaitre la langue d'un fichier en lisant son texte
MOTS_FRANCAIS = {
    "le", "la", "les", "et", "est", "je", "tu", "vous", "pas", "une",
    "des", "que", "qui", "ce", "il", "elle", "nous", "pour", "dans", "mais",
    "avec", "suis", "oui", "non", "sur",
}

MOTS_ANGLAIS = {
    "the", "and", "you", "is", "to", "of", "it", "that", "what", "this",
    "with", "for", "are", "was", "have", "not", "just", "my", "your", "he",
    "she", "we", "yes", "no", "do",
}

def lire_fichier(chemin_fichier):
    """
    Lit un fichier de sous-titres quel que soit son encodage
    Le corpus melange trois encodages : UTF-16, UTF-8 et cp1252
    """
    contenu = open(chemin_fichier, 'rb').read()

    # UTF-16 le fichier commence par une marque speciale (BOM)
    if contenu.startswith(codecs.BOM_UTF16_LE) or contenu.startswith(codecs.BOM_UTF16_BE):
        return contenu.decode("utf-16", errors="ignore")

    # UTF-8 en premier un fichier cp1252 avec des accents est refuse
    # par le decodage UTF-8 donc on ne peut pas se tromper
    # l'inverse est faux cp1252 accepte presque tout et transformerait
    # "été" (UTF-8) en caractere illisible
    try:
        return contenu.decode("utf-8-sig")
    except UnicodeDecodeError:
        return contenu.decode("cp1252", errors="ignore")

def detecter_langue(texte):
    """
    Devine la langue d'un episode en lisant son texte
    renvoie "vf", "vo", ou None si on peut pas decider
    (texte trop court, autre langue comme le croate ou le grec...)
    """
    mots = re.findall(r"[a-z]+", texte.lower())
    if len(mots) < 100:
        return None

    nb_francais = 0
    nb_anglais = 0
    for mot in mots:
        if mot in MOTS_FRANCAIS:
            nb_francais = nb_francais + 1
        if mot in MOTS_ANGLAIS:
            nb_anglais = nb_anglais + 1

    # Dans un vrai texte ces mots-outils representent 20 a 30 % des mots
    # On exige au moins 10 % et deux fois plus que l'autre langue
    if nb_francais > 0.10 * len(mots) and nb_francais > 2 * nb_anglais:
        return "vf"
    if nb_anglais > 0.10 * len(mots) and nb_anglais > 2 * nb_francais:
        return "vo"
    return None

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
fichiers_ignores = []

for serie in sorted(os.listdir(CORPUS)):

    dossier_serie = os.path.join(CORPUS, serie)
    if not os.path.isdir(dossier_serie):
        continue

    mots_vf = []
    mots_vo = []
    # Un ensemble (set) plutot qu'une liste le test "in" est immediat    
    episodes_deja_lus = set()

    # Parcourir tous les sous_dossiers de la serie 
    for chemin, dossiers, fichiers in os.walk(dossier_serie):
        for fichier in fichiers:

            if not fichier.lower().endswith(".srt"):
                continue

            # Lire le fichier (UTF-16, UTF-8 ou cp1252 selon les fichiers)
            chemin_fichier = os.path.join(chemin, fichier)
            try: 
                contenu = lire_fichier(chemin_fichier)
            except Exception as erreur:
                print("  ERREUR lecture", chemin_fichier, ":", erreur)
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

            # La langue se lit dans le TEXTE, pas dans le nom du dossier :
            # les noms de dossiers et de fichiers sont souvent faux
            # (fichiers anglais dans des dossiers VF, et inversement).
            langue = detecter_langue(texte_episode)
            if langue is None:
                fichiers_ignores.append(chemin_fichier)
                continue

            # Meme episode en plusieurs versions : on n'en garde qu'une.
            # La cle contient la langue pour ne pas jeter la VO d'un
            # episode parce que sa VF porte le meme nom de fichier.
            cle = (langue, fichier.lower())
            if cle in episodes_deja_lus:
                continue
            episodes_deja_lus.add(cle)

            mots_episode = nettoyer_texte(texte_episode)

            # extend ajoute a la fin de la liste existante.
            # "mots_vf = mots_vf + mots_episode" recopiait toute la liste
            # a chaque episode, ce qui devenait tres lent.
            if langue == "vf":
                mots_vf.extend(mots_episode)
            else:
                mots_vo.extend(mots_episode)

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

print()
print(len(fichiers_ignores), "fichiers ignores (langue non reconnue ou texte trop court) :")
for chemin_fichier in fichiers_ignores:
    print("   ", os.path.relpath(chemin_fichier, CORPUS))