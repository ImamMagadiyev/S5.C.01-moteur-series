# SAE S5.C.01
# Ecrans des comptes : accueil, connexion, creation de compte
# Chaque ecran renvoie le nom de l'ecran suivant

from moteur_series.donnees.comptes import creer_compte, se_connecter
from moteur_series.interface.terminal import (
    GRIS, ROUGE, VERT, afficher_entete, annoncer, choisir, couleur, saisir,
)


def ecran_accueil():
    afficher_entete("ACCUEIL", None)
    choix = choisir([
        ("1", "Se connecter"),
        ("2", "Créer un compte"),
        ("3", "Continuer sans compte"),
        ("0", "Quitter"),
    ])
    if choix == "1":
        return "connexion"
    if choix == "2":
        return "inscription"
    if choix == "3":
        return "menu"
    if choix == "0":
        return "quitter"
    return "accueil"   # Echap sur l'accueil : rien avant, on reste


def ecran_connexion(conn):
    """
    Renvoie (ecran suivant, utilisateur) ; utilisateur = (id, pseudo) ou None
    """
    afficher_entete("CONNEXION", None)
    print(couleur(" Laissez le pseudo vide pour revenir à l'accueil.", GRIS))
    print()
    pseudo = saisir(" Pseudo       : ")
    if pseudo is None or pseudo == "":
        return ("accueil", None)
    mdp = saisir(" Mot de passe : ", masque=True)
    if mdp is None:
        return ("accueil", None)

    resultat, id_utilisateur = se_connecter(conn, pseudo, mdp)
    if resultat == "ok":
        annoncer("Bienvenue " + pseudo + " !", VERT)
        return ("menu", (id_utilisateur, pseudo))
    if resultat == "mauvais_mdp":
        annoncer("Mot de passe incorrect, réessayez.", ROUGE)
        return ("connexion", None)

    # resultat == "inconnu"
    print()
    print(" " + couleur("Le pseudo « " + pseudo + " » n'existe pas.", ROUGE))
    print()
    choix = choisir([
        ("1", "Créer un compte"),
        ("2", "Continuer sans compte"),
        ("0", "Retour à l'accueil"),
    ])
    if choix == "1":
        return ("inscription", None)
    if choix == "2":
        return ("menu", None)
    return ("accueil", None)


def ecran_creer_compte(conn):
    afficher_entete("CRÉER UN COMPTE", None)
    print(couleur(" Laissez le pseudo vide pour revenir à l'accueil.", GRIS))
    print()
    pseudo = saisir(" Pseudo       : ")
    if pseudo is None or pseudo == "":
        return "accueil"
    email = saisir(" Email        : ")
    if email is None:
        return "accueil"
    mdp = saisir(" Mot de passe : ", masque=True)
    if mdp is None:
        return "accueil"
    confirmation = saisir(" Confirmation : ", masque=True)
    if confirmation is None:
        return "accueil"

    if email == "" or mdp == "":
        annoncer("Tous les champs sont obligatoires.", ROUGE)
        return "inscription"
    if mdp != confirmation:
        annoncer("Les deux mots de passe sont différents.", ROUGE)
        return "inscription"

    if creer_compte(conn, pseudo, email, mdp):
        annoncer("Compte créé, vous pouvez vous connecter.", VERT)
        return "connexion"

    annoncer("Ce pseudo ou cet email est déjà utilisé.", ROUGE)
    return "inscription"
