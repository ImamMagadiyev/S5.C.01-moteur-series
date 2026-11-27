# SAE S5.C.01
# Ecrans des notes (utilisateur connecte) : noter une serie, mes recommandations

from moteur_series.interface.saisies import demander_note, demander_titre, proposer_de_noter
from moteur_series.interface.terminal import (
    GRIS, JAUNE, VERT, afficher_entete, afficher_resultats, couleur, saisir,
)
from moteur_series.moteurs.recommandation import charger_notes, noter_serie, recommander_selon_notes


def afficher_notes(notes):
    """
    Affiche les notes {titre: note} avec des etoiles, de la meilleure a la moins bonne
    """
    if len(notes) == 0:
        print(couleur(" Vous n'avez encore noté aucune série.", GRIS))
        return
    print(" Vos notes :")
    classement = sorted(notes.items(), key=lambda paire: paire[1], reverse=True)
    for titre, note in classement:
        etoiles = "★" * note + "☆" * (5 - note)
        print("   " + titre.ljust(30) + couleur(etoiles, JAUNE))


def ecran_noter(conn, similarites, utilisateur):
    afficher_entete("NOTER UNE SÉRIE", utilisateur)
    id_utilisateur = utilisateur[0]
    afficher_notes(charger_notes(id_utilisateur))
    print()
    print(couleur(" Tapez le nom d'une série (ligne vide pour revenir au menu).", GRIS))
    print(couleur(" Si elle est déjà notée, la nouvelle note remplace l'ancienne.", GRIS))
    while True:
        print()
        titre = demander_titre(similarites, " Série : ")
        if titre is None:
            return "menu"
        note = demander_note()
        if note is None:
            print(couleur(" Note annulée.", GRIS))
            continue
        noter_serie(conn, id_utilisateur, titre, note)
        print(" " + couleur("Note enregistrée : " + titre + " " + str(note) + "/5", VERT))


def ecran_mes_recommandations(conn, similarites, utilisateur):
    afficher_entete("MES RECOMMANDATIONS", utilisateur)
    notes = charger_notes(utilisateur[0])
    afficher_notes(notes)
    print()

    if len(notes) == 0:
        print(couleur(" Notez quelques séries (menu, option 3) pour recevoir des recommandations.", GRIS))
    else:
        resultats = recommander_selon_notes(notes, similarites)
        if len(resultats) == 0:
            # recommander_selon_notes ignore les notes de 3 (poids note - 3 = 0)
            print(couleur(" Toutes vos notes valent 3 (neutre) : notez des séries que vous", GRIS))
            print(couleur(" aimez (4 ou 5) ou que vous n'aimez pas (1 ou 2).", GRIS))
        else:
            print(" Séries recommandées pour vous :")
            afficher_resultats(resultats)
            print()
            # Une nouvelle note change les recommandations : on reaffiche l'ecran
            if proposer_de_noter(conn, utilisateur, resultats):
                return "recommandations"
            return "menu"

    print()
    saisir(couleur(" Appuyez sur Entrée ou Échap pour revenir au menu.", GRIS))
    return "menu"
