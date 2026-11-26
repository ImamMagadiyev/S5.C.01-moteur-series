# SAE S5.C.01
# Evaluation de la recommandation "series similaires"

import os 
import time

from moteur_series.config import BASE
from moteur_series.recommandation import charger_vecteurs, series_similaires

# series attendue dans ses recommandations
PAIRES_TEST = [
    ("buffy", "angel"),
    ("angel", "buffy"),
    ("greysanatomy", "privatepractice"),
    ("privatepractice", "greysanatomy"),
    ("ncis", "ncislosangeles"),
    ("ncislosangeles", "ncis"),
    ("stargatesg1", "stargateatlantis"),
    ("stargateatlantis", "stargatesg1"),
    ("stargateuniverse", "stargateatlantis"),
    ("battlestargalactica", "caprica"),
    ("caprica", "battlestargalactica"),
    ("prisonbreak", "oz"),
    ("oz", "prisonbreak"),
    ("house", "greysanatomy"),
    ("scrubs", "greysanatomy"),
    ("thesopranos", "theblackdonnellys"),
    ("friends", "howimetyourmother"),
    ("trueblood", "thevampirediaries"),
    ("thevampirediaries", "trueblood"),
    ("90210", "melroseplace"),
]

# Plus grand que le nombre de series on garde le classement complet 
NB_RESULTATS = 200

if not os.path.exists(BASE):
    print("ERREUR : base introuvable :", BASE)
    print("Lancer d'abord : uv run scripts/preparation/create_base.py puis uv run scripts/preparation/indexation/main.py")
    raise SystemExit(1)

print("Chargement des vecteurs...")
vecteurs = charger_vecteurs()
print()

# ---------------------------------------------------------
# 1. Paires attendues
# ---------------------------------------------------------
nb_top1 = 0
nb_top5 = 0

for serie, attendue in PAIRES_TEST:
    resultats = series_similaires(serie, vecteurs, NB_RESULTATS)

    # Rang de la serie attendue, 0 si elle n'apparait pas
    rang = 0
    position = 1
    for titre, similarite in resultats:
        if titre == attendue:
            rang = position
            break
        position = position + 1

    if rang == 1:
        nb_top1 = nb_top1 + 1
    if 1 <= rang <= 5:
        nb_top5 = nb_top5 + 1

    if len(resultats) > 0:
        premier = resultats[0][0]
    else:
        premier = "-"

    if rang == 0:
        rang_texte = "absent"
    else:
        rang_texte = str(rang)

    print(f"{rang_texte:>6}  {serie:22} attendu {attendue:22} 1er {premier}")

nb = len(PAIRES_TEST)
print()
print(f"TOP 1 : {nb_top1}/{nb} ({100 * nb_top1 / nb:.0f} %)")
print(f"TOP 5 : {nb_top5}/{nb} ({100 * nb_top5 / nb:.0f} %)")

# ---------------------------------------------------------
# 2. Series "aimants" : on calcule le top 5 de TOUTES les series
# ---------------------------------------------------------
print()
print("Calcul des recommandations de toutes les series...")
debut = time.time()
apparitions = {}
for titre in vecteurs:
    for titre_proche, similarite in series_similaires(titre, vecteurs, 5):
        if titre_proche not in apparitions:
            apparitions[titre_proche] = 0
        apparitions[titre_proche] = apparitions[titre_proche] + 1
duree = time.time() - debut

classement = sorted(apparitions.items(), key=lambda paire: paire[1], reverse=True)
print(f"Series les plus proposees (nombre de top 5 sur {len(vecteurs)} series) :")
for titre, nb_fois in classement[:5]:
    print(f"   {titre:22} {nb_fois}")
print(len(apparitions), "series differentes proposees au moins une fois")
print(f"Temps moyen par serie : {1000 * duree / len(vecteurs):.0f} ms")