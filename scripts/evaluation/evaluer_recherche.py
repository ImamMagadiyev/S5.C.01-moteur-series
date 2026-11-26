# SAE S5.C.01
# Evaluation du moteur de recherche sur des requetes test
# pour chaque requete on connait la serie attendue on regarde a quel rang elle sort
# Prerequis base remplie (uv run scripts/preparation/indexation/main.py)
# Usage uv run scripts/evaluation/evaluer_recherche.py

import os
import time

from moteur_series.config import BASE
from moteur_series.recherche import charger_index, rechercher

# requete, serie attendue 
REQUETES_TEST = [
    ("crash avion ile", "lost"),
    ("sorciere magie soeurs", "charmed"),
    ("mafia famille new jersey", "thesopranos"),
    ("prison evasion frere", "prisonbreak"),
    ("medecin hopital chirurgie", "greysanatomy"),
    ("prison tatouage", "prisonbreak"),
    ("vampire tueuse lycee", "buffy"),
    ("professeur chimie cancer drogue", "breakingbad"),
    ("tueur en serie police scientifique miami", "dexter"),
    ("diagnostic lupus vicodin", "house"),
    ("extraterrestres fbi complot", "xfiles"),
    ("physicien colocataire comics", "thebigbangtheory"),
    ("chasseurs demons freres", "supernatural"),
    ("superman kryptonite", "smallville"),
    ("agence publicite new york", "madmen"),
    ("baltimore drogue ecoutes", "thewire"),
    ("pompes funebres famille", "sixfeetunder"),
    ("terminator robot futur", "thesarahconnorchronicles"),
    ("vaisseau cylons", "battlestargalactica"),
    ("porte etoiles goauld", "stargatesg1"),
]

# Plus grand que le nombre de serie on garde le classement complet
NB_RESULTATS = 200

if not os.path.exists(BASE):
    print("Erreur : base introuvable :", BASE)
    print("Lance d'abord : uv run scripts/preparation/create_base.py puis uv run scripts/preparation/indexation/main.py")
    raise SystemExit(1)

print("Chargement de l'index...")
index = charger_index()
print()

nb_top1 = 0
nb_top3 = 0
duree_totale = 0

for requete, attendue in REQUETES_TEST:
    debut = time.time()
    resultats =rechercher(requete, index, NB_RESULTATS)
    duree_totale = duree_totale + (time.time() - debut)

    # Rang de la serie attendue, 0 si elle n'apparait pas du tout 
    rang = 0
    position = 1
    for titre, score in resultats:
        if titre == attendue:
            rang = position
            break
        position = position + 1

    if rang == 1:
        nb_top1 = nb_top1 + 1
    if 1 <= rang <= 3:
        nb_top3 = nb_top3 + 1

    if len(resultats) > 0:
        premier = resultats[0][0]
    else: 
        premier = "-"
    if rang == 0:
        rang_texte = "absent"
    else: 
        rang_texte = str(rang)

    print(f"{rang_texte:>6} {requete:42} attendu {attendue:25} 1er {premier}")

nb = len(REQUETES_TEST)
print()
print(f"TOP 1 : {nb_top1}/{nb} ({100 * nb_top1 / nb:.0f} %)")
print(f"TOP 3 : {nb_top3}/{nb} ({100 * nb_top3 / nb:.0f} %)")
print(f"Temps moyen par requete : {1000 * duree_totale / nb:.1f} ms")