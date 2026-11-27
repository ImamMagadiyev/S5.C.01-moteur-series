# SAE S5.C.01
# Cree la base de donnees a partir de modele_relationnel.sql
# ATTENTION : supprime puis recree toutes les tables (index ET comptes)
# Usage : uv run scripts/preparation/create_base.py

import os
import sqlite3

# Tous les chemins viennent de config.py : jamais de C:\Users\... en dur
from moteur_series.config import BASE, SCRIPT_SQL

print("Script SQL :", SCRIPT_SQL)
print("Base     :", BASE)
print()

# On verifie que le fichier SQL est bien avant de continuer
if not os.path.exists(SCRIPT_SQL):
    print("ERREUR : fichier SQL introuvable")
    print("Il doit se trouver a la racine du projet")
    raise SystemExit(1)

# Le dossier data n est pas versionne : data/db peut ne pas exister
# (os.path.dirname(BASE) = le dossier qui contient la base)
if not os.path.exists(os.path.dirname(BASE)):
    os.makedirs(os.path.dirname(BASE))
    print("Dossier", os.path.dirname(BASE), "cree")

# On lit le fichier SQL
fichier = open(SCRIPT_SQL, encoding="utf-8")
sql = fichier.read()
fichier.close()

# On execute tout le script d'un coup
connexion = sqlite3.connect(BASE)
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