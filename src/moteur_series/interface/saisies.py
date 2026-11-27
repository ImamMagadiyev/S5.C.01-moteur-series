# SAE S5.C.01
# Questions posees a l'utilisateur, communes a plusieurs ecrans :
# nom d'une serie, note de 1 a 5, noter une serie parmi des resultats

from moteur_series.interface.terminal import GRIS, JAUNE, ROUGE, VERT, couleur, saisir
from moteur_series.moteurs.recommandation import noter_serie, suggerer_titres
from moteur_series.traitement.texte import normaliser_titre


def demander_titre(similarites, invite):
    """
    Demande le nom d'une serie jusqu'a ce qu'il corresponde a une serie connue
    Renvoie le titre tel qu'il est dans la base, ou None si Echap ou ligne vide
    """
    while True:
        saisie = saisir(couleur(invite, JAUNE))
        if saisie is None or saisie == "":
            return None
        titre = normaliser_titre(saisie)
        if titre in similarites:
            return titre

        propositions = suggerer_titres(titre, similarites)
        if len(propositions) > 0:
            print(" " + couleur("Série inconnue. Vouliez-vous dire : " + ", ".join(propositions) + " ?", ROUGE))
        else:
            print(" " + couleur("Série inconnue.", ROUGE))


def demander_note():
    """
    Redemande tant que la saisie n'est pas un entier de 1 a 5
    Renvoie la note, ou None si Echap
    """
    while True:
        saisie = saisir(couleur(" Note de 1 à 5 : ", JAUNE))
        if saisie is None:
            return None
        if saisie in ["1", "2", "3", "4", "5"]:
            return int(saisie)
        print(" " + couleur("La note doit être un nombre entier de 1 à 5.", ROUGE))


def proposer_de_noter(conn, utilisateur, resultats):
    """
    Apres une liste de resultats [(titre, score), ...] : propose de noter les
    series affichees en tapant leur numero (seulement si l'utilisateur est connecte)
    Renvoie True si au moins une note a ete enregistree
    """
    if utilisateur is None or len(resultats) == 0:
        return False
    a_note = False
    while True:
        saisie = saisir(couleur(" Numéro de la série à noter (Entrée pour continuer) : ", JAUNE))
        if saisie is None or saisie == "":
            return a_note
        # isdigit() avant int() : "abc" ou "-1" ne font pas planter le programme
        if not saisie.isdigit() or int(saisie) < 1 or int(saisie) > len(resultats):
            print(" " + couleur("Tapez un numéro entre 1 et " + str(len(resultats)) + ", ou Entrée.", ROUGE))
            continue
        titre = resultats[int(saisie) - 1][0]   # la liste commence a 0, l'affichage a 1
        note = demander_note()
        if note is None:
            print(couleur(" Note annulée.", GRIS))
            continue
        noter_serie(conn, utilisateur[0], titre, note)
        print(" " + couleur("Note enregistrée : " + titre + " " + str(note) + "/5", VERT))
        a_note = True
