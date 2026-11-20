# SAE S5.C.01
# Cree la base de donnees a partir de data/modele_relationnel.sql
# USage : uv run scripts/creation_base.py

import os 
import sqlite3

# Chemins relatifs au projet Jamais de C:\Users\.. en dur
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_DATA = os.path.join(RACINE, "data")
BASe = os.path.join(DOSSIER_DATA, "series.db")
SCRIPT_SQL = os.path.join(RACINE, "modele_relationnel.sql")

print("Script SQL :", SCRIPT_SQL)
print("Base     :", BASe)
print()

# On verifie que le fichier SQL est bien avant de continuer
if not os.path.exists(SCRIPT_SQL):
    print("ERREUR : fichier SQL introuvable")
    print("Il doit se trouver dans data/ ")
    raise SystemExit(1)

# Le dossier data n est pas versionne. Il peut ne pas exister
if not os.path.exists(DOSSIER_DATA):
    os.makedirs(DOSSIER_DATA)
    print("Dossier data cree")

# On lit le fichier SQL
fichier = open(SCRIPT_SQL, encoding="utf-8")
sql = fichier.read()
fichier.close()

# On execute tout le script d'un coup
connexion = sqlite3.connect(BASe)
connexion.execute("PRAGMA foreign_keys = ON")
connexion.executescript(sql)
connexion.commit()

# Verification =. On liste ce qui a vraiment ete cree 
tables = connexion.execute(
    "SELECT name FROM sqlite_master WHERE type = 'table'"
    " AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()

index = connexion.execute(
    "SELECT name FROM sqlite_master WHERE type = 'index'"
    " AND name NOT LIKE 'sqlite_%' ORDER BY name"
).fetchall()

print(len(tables), "tables creees :")
for table in tables:
    print("  ", table[0])

print()
print(len(index), "index crees :")
for i in index:
    print("  ", i[0])

connexion.close()

print()
print("Base prete.")