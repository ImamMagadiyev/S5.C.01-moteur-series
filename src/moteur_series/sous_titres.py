# SAE S5.C.01
# Lecture des fichiers de sous-titres (.srt) :
# encodage, extraction des repliques, detection de la langue.

import codecs
import re


# Une ligne qui contient un de ces mots est un credit de la team
# de sous-titrage, pas une replique
MOTS_CREDITS = [
    ".com", ".net", ".org", "forom", "presynchro", "relecture",
    "soustitre", "sous-titre", "subtitle", "synchro", "traduction",
    "transcript", "www.",
]

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
    # "rb" = lecture binaire : on recupere les octets bruts,
    # on choisit nous-memes comment les decoder.
    # "with" ferme le fichier automatiquement a la fin du bloc.
    with open(chemin_fichier, "rb") as fichier:
        contenu = fichier.read()

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

def est_un_credit(ligne):
    """
    Renvoie True si la ligne est un credit de sous-titrage
    (adress de site, nom de team...) et non une replique
    """
    ligne_minuscule = ligne.lower()
    for mot in MOTS_CREDITS:
        if mot in ligne_minuscule:
            return True
    return False

def extraire_repliques(contenu):
    """
    Garde uniquement les repliques d'un fichier .srt
    On jette les numeros, les lignes de timecode et les credits
    Renvoie tout le texte de l'episode en une seule chaine
    """
    repliques = []
    for ligne in contenu.splitlines():
        ligne = ligne.strip()
        if ligne == "":
            continue
        if ligne.isdigit():          # numero du sous-titre : 1, 2, 3...
            continue
        if "-->" in ligne:           # timecode : 00:01:02,500 --> 00:01:04,000
            continue
        if est_un_credit(ligne):
            continue
        repliques.append(ligne)

    return " ".join(repliques)

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