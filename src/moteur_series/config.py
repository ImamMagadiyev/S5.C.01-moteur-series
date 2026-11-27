# SAE S5.C.01
# Tous les chemins du projet sont definis ici et seulement ici 
# Les scripts et les modules les iimportent
import os

# Dossier racine du projet 
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Donnes (dossier non versionne, tout y est regenerable)
DOSSIER_DATA = os.path.join(RACINE, "data")
CORPUS = os.path.join(DOSSIER_DATA, "sous-titres")          # corpus brut (.srt)
CORPUS_PROPRE = os.path.join(DOSSIER_DATA, "corpus_propre") # un .txt par serie et par langue
BASE = os.path.join(DOSSIER_DATA, "db", "series.db")              # index TF-IDF + comptes et notes


# Script de creation de la base
SCRIPT_SQL = os.path.join(RACINE, "modele_relationnel.sql")