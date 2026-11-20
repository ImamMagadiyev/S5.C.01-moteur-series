import os

# scripts/indexation/config.py -> 3 dirname() pour remonter à la racine
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CORPUS_CHEMIN = os.path.join(RACINE, "data", "corpus_propre")  # adapte si ce n'est pas le bon chemin chez toi
CHEMIN_BASE = os.path.join(RACINE, "data", "series.db")