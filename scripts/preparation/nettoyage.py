# SAE S5.C.01
# Nettoie les sous-titres du corpus et ecrit un fichier texte
# par serie et par langue dans data/corpus_propre
# Usage : uv run scripts/preparation/nettoyage.py

import os

from moteur_series.config import CORPUS, CORPUS_PROPRE
from moteur_series.traitement.sous_titres import detecter_langue, extraire_repliques, lire_fichier
from moteur_series.traitement.texte import nettoyer_texte


print("Corpus :", CORPUS)

if not os.path.exists(CORPUS_PROPRE):
    os.makedirs(CORPUS_PROPRE)

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

    # Parcourir tous les sous-dossiers de la serie
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

            # Garder uniquement les repliques
            texte_episode = extraire_repliques(contenu)

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
        fichier_vf = os.path.join(CORPUS_PROPRE, serie + ".vf.txt")
        with open(fichier_vf, "w", encoding="utf-8") as sortie:
            sortie.write(" ".join(mots_vf))

    if len(mots_vo) > 0:
        fichier_vo = os.path.join(CORPUS_PROPRE, serie + ".vo.txt")
        with open(fichier_vo, "w", encoding="utf-8") as sortie:
            sortie.write(" ".join(mots_vo))

    nombre_series = nombre_series + 1
    print(serie, ":", len(episodes_deja_lus), "episodes,",
          len(mots_vf), "mots VF,", len(mots_vo), "mots VO")

print()
print(nombre_series, "series traitees. Sortie :", CORPUS_PROPRE)

print()
print(len(fichiers_ignores), "fichiers ignores (langue non reconnue ou texte trop court) :")
for chemin_fichier in fichiers_ignores:
    print("   ", os.path.relpath(chemin_fichier, CORPUS))
