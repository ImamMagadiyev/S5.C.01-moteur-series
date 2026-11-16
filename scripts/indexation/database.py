import sqlite3
from config import CHEMIN_BASE

def connexion():
    conn = sqlite3.connect(CHEMIN_BASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def inserer_serie(conn, titre):
    curseur = conn.execute("INSERT INTO Serie (Titre) VALUES (?)", (titre,))
    return curseur.lastrowid

def obtenir_ou_creer_mot(conn, libelle, idf_value):
    ligne = conn.execute("SELECT Id_MOT FROM Mot WHERE libelle = ?", (libelle,)).fetchone()
    if ligne:
        return ligne[0]
    curseur = conn.execute("INSERT INTO Mot (libelle, idf) VALUES (?, ?)", (libelle, idf_value))
    return curseur.lastrowid

def inserer_apparait(conn, id_mot, id_serie, langue, poids, frequence):
    conn.execute(
        "INSERT INTO apparait (fk_MOT, fk_serie, langue, poids, frequence) VALUES (?, ?, ?, ?, ?)",
        (id_mot, id_serie, langue, poids, frequence)
    )