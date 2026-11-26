import os

def charger_corpus(chemin, suffixe):
    """Charge les fichiers finissant par `suffixe` (ex: 'vf.txt') -> {nom_serie: liste_de_mots}."""
    corpus = {}
    for fichier in os.listdir(chemin):
        if fichier.lower().endswith(suffixe):
            nom = fichier.split(".")[0]
            with open(os.path.join(chemin, fichier), "r", encoding="utf-8") as f:
                corpus[nom] = f.read().split()
    return corpus