# Gestion des comptes utilisateurs 
import hashlib
import hmac
import os
import sqlite3

NB_ITERATIONS = 200_000   # plus c'est grand, plus c'est long a casser


def hacher_mot_de_passe(mot_de_passe):
    """
    Renvoie le texte a stocker dans la colonne mot_de_passe : "sel$hash"
    Le sel est aleatoire : deux comptes avec le meme mot de passe
    n'auront jamais le meme hash
    """
    sel = os.urandom(16)
    empreinte = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode("utf-8"), sel, NB_ITERATIONS
    )
    # .hex() transforme les octets en texte pour pouvoir les stocker
    return sel.hex() + "$" + empreinte.hex()


def verifier_mot_de_passe(mot_de_passe, stocke):
    """
    Renvoie True si mot_de_passe correspond a stocke ("sel$hash")
    """
    # 1. Separer stocke en deux morceaux autour du "$"
    # 2. Retransformer le sel en octets (indice : bytes.fromhex)
    # 3. Recalculer l'empreinte avec CE sel, pas un nouveau
    # 4. Comparer avec hmac.compare_digest(...)
    sel_hex, empreinte = stocke.split("$")
    sel = bytes.fromhex(sel_hex)
    nouvelle = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode("utf-8"), sel, NB_ITERATIONS
    )
    return hmac.compare_digest(empreinte, nouvelle.hex())


def creer_compte(conn, pseudo, email, mot_de_passe):
    """
    Ajoute l'utilisateur dans la base
    Renvoie True si le compte est cree, False si le pseudo ou l'email est deja pris
    """
    try:
        conn.execute(
            "INSERT INTO utilisateur (pseudo,email,mot_de_passe) VALUES (?, ?, ?)",
            (pseudo, email,hacher_mot_de_passe(mot_de_passe)),
        )
        conn.commit()
        return True 
    except sqlite3.IntegrityError:
        # mail ou pseudo deja utilise
        return False

def se_connecter(conn, pseudo, mot_de_passe):
    """
    Renvoie ("ok", id_utilisateur), ("mauvais_mdp", None) ou ("inconnu", None)
    """
    # On filtre seulement sur le pseudo : le hash depend du sel stocke en base
    ligne = conn.execute(
        "SELECT Id_utilisateur, mot_de_passe FROM utilisateur WHERE pseudo = ?",
        (pseudo,),
    ).fetchone()

    if ligne is None:
        return ("inconnu", None)

    id_utilisateur, stocke = ligne
    if verifier_mot_de_passe(mot_de_passe, stocke):
        return ("ok", id_utilisateur)
    return ("mauvais_mdp", None)

    ##g touché a bsae.py,comptes.py,database.py,main.py
    