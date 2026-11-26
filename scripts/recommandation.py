# SAE S5.C.01
# Séries similaires en ligne de commande on tape une série,
# le programme affiche les séries les plus proches
# Prerequis base remplie (uv run scripts/indexation/main.py)
# Usage uv run scripts/recommandation.py

import os 
import re
import time

from moteur_series.config import BASE
from moteur_series.recommandation import charger_vecteurs, series_similaires

if not os.path.exists(BASE):
    print("ERREUR : base introuvable :", BASE)
    print("Lancer d'abord : uv run scripts/create_base.py puis uv run scripts/indexation/main.py")
    raise SystemExit(1)

# Chargement des vecteurs une seule fois au demarrage
print("Chargement des vecteurs...")
debut = time.time()
vecteurs = charger_vecteurs()
print(len(vecteurs), "series chargées en", round(time.time() - debut, 1), "s")
print("Tapez le nom d'une serie (ligne vide pour quitter)")

while True:
    try:
        saisie = input("\nSérie : ")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou Ctrl+z on quitte proprement sans trace d'erreur
        print()
        break
    if saisie.strip() == "":
        break

    # Les titres de la base sont colles en minuscules
    titre = re.sub(r"[^a-z0-9]", "", saisie.lower())
    if titre == "":
        print("Serie inconnue")
        continue

    if titre not in vecteurs:
        # On propose les series dont le titre contient ce qui a ete tape
        proposition = []
        for titre_connu in sorted(vecteurs):
            if titre in titre_connu:
                proposition.append(titre_connu)
        if len(proposition) > 0:
            print("Serie inconnue. Voulez-vous dire :", ", ".join(proposition))
        else:
            print("Serie inconnue")
        continue

    debut = time.time()
    resultats = series_similaires(titre, vecteurs)
    duree = (time.time() - debut) * 1000

    rang = 1
    for titre_proche, similarite in resultats:
        print(f"{rang:2}. {titre_proche:30} {similarite:.3f}")
        rang = rang + 1
    print(f"({duree:.0f} ms)")