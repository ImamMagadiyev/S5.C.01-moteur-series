

def vider_index(conn):
    """
    Efface l'ancien index pour pouvoir relancer le script 
    on ne touche pas a la table Serie supprimer une serie effacerait 
    aussi ses notes (ON DELETE CASCADE dans noter)
    """
    conn.execute("DELETE FROM apparait")
    conn.execute("DELETE FROM Mot")

def obtenir_ou_creer_serie(conn, titre):
    """
    Renvoie l'identifiant de la serie en la créant si elle n'existe pas encore
    """
    ligne = conn.execute("SELECT ID_Serie FROM Serie WHERE Titre = ?", (titre,)).fetchone()
    if ligne:
        return ligne[0]
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