import os
import zipfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RACINE, "data", "sous-titres")

print("Corpus :", CORPUS)

total = 0
erreurs = []

for passe in range(1, 6):

    # Chercher tous les fichiers .zip du corpus
    archives = []
    for chemin, dossiers, fichiers in os.walk(CORPUS):
        for fichier in fichiers:
            if fichier.lower().endswith(".zip"):
                archives.append(os.path.join(chemin, fichier))

    # Extraire celles qui ne l'ont pas encore ete
    extraites = 0
    for archive in archives:

        destination = archive[:-4]          # le meme nom, sans le ".zip"

        if os.path.exists(destination):     # deja extraite, on passe
            continue

        try:
            zipfile.ZipFile(archive).extractall(destination)
            extraites = extraites + 1
        except Exception:
            if archive not in erreurs:
                erreurs.append(archive)

    print("Passe", passe, ":", extraites, "archives extraites")
    total = total + extraites

    # Plus rien a extraire, on arrete
    if extraites == 0:
        break

print()
print("Total :", total, "archives extraites")
print("Archives illisibles :", len(erreurs))
for archive in erreurs:
    print("   ", archive)