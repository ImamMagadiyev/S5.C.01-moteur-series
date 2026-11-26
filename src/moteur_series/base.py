
import sqlite3
from moteur_series.config import BASE

def connexion():
    conn = sqlite3.connect(BASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn