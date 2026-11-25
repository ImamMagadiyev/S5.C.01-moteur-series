# SAE S5.C.01
# Recherche de series par mots-cles en ligne de commande
# Prerequis base remplie (uv run scripts/indexation/main.py)
# Usage uv run scripts/recherche.py

import os
import time

from moteur_series.config import BASE
from moteur_series.recherche import charger_index, rechercher

if not os.path.exists(BASE):
    print("ERREUR : base introuvable :", BASE)
    print("Lancer d'abord : uv run scripts/create_base.py puis uv run scripts/indexation/main.py")
    raise SystemExit(1)

# Chargement de l'index : une seule fois, au démarrage
print("Chargement de l'index...")
debut = time.time()
index = charger_index()
print(len(index), "mots chargés en", round(time.time() - debut, 1), "s")
print("Tapez une recherche (ligne vide pour quitter).")

while True:
    try:
        requete = input("\nRecherche : ")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou Ctrl+Z on quitte proprement sans trace d'erreur
        print()
        break
    if requete.strip() == "":
        break

    debut = time.time()
    resultats = rechercher(requete, index)
    duree = (time.time() - debut) * 1000

    if len(resultats) == 0:
        print("Aucune série trouvée.")
    rang = 1
    for titre, score in resultats:
        print(f"{rang:2}. {titre:30} {score:.5f}")
        rang = rang + 1
    print(f"({duree:.0f} ms)")