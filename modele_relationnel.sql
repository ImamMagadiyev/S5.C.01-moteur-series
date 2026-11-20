-- =====================================================================
-- SAE S5.C.01
-- Creation de la base de donnees
-- SQLite. Le fichier produit est data/series.db
-- Lancer avec sqlite3 data/series.db < scripts/creation_base.sql
 
-- SQLite desactive les cles etrangeres par defaut.
-- Chaque connexion Python doit executer PRAGMA foreign_keys = ON.
-- Sans cela les ON DELETE CASCADE sont ignores.
-- =====================================================================

PRAGMA foreign_keys = ON;
 
-- On supprime dans l'ordre inverse des dependances
DROP TABLE IF EXISTS Noter;
DROP TABLE IF EXISTS apparait;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS Serie;
DROP TABLE IF EXISTS Mot;

-- ---------------------------------------------------------------------
-- Vocabulaire du corpus.
-- Environ 239000 mots distincts apres nettoyage.
-- L idf est stocke ici car il depend du mot et du corpus.
-- Il ne depend jamais de la serie.
-- ---------------------------------------------------------------------

CREATE TABLE Mot (
Id_MOT INTEGER PRIMARY KEY AUTOINCREMENT,
libelle  VARCHAR(50) NOT NULL UNIQUE,
idf REAL NOT NULL

); 

-- ---------------------------------------------------------------------
-- Les series du corpus.
-- 126 series sont indexables sur les 128 fournies.
-- annee et nb_saison restent vides car ils ne sont pas dans les sous-titres.
-- nb_episode se deduit du corpus apres dedoublonnage.
-- ---------------------------------------------------------------------

create TABLE Serie (
ID_Serie INTEGER PRIMARY KEY AUTOINCREMENT,
Titre VARCHAR(150) NOT NULL,
annee INTEGER,
nb_saison INTEGER,
nb_episode INT NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------
-- Comptes utilisateurs.
-- Le sujet exige la creation la modification et la suppression d un compte.
-- mot_de_passe contient un hash et jamais le mot de passe en clair.
-- 255 caracteres car un hash bcrypt en fait 60 et un SHA-256 en fait 64.
-- ---------------------------------------------------------------------

CREATE table utilisateur (
Id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
pseudo VARCHAR (255) NOT NULL UNIQUE,
email VARCHAR(150) NOT NULL UNIQUE,
mot_de_passe VARCHAR(255) NOT NULL,
date_creation DATE NOT NULL DEFAULT (CURRENT_DATE)
);

-- ---------------------------------------------------------------------
-- Index inverse du moteur de recherche.
-- Une ligne represente un couple mot serie et non une occurrence.
-- Si avion apparait 266 fois dans Lost cela donne une ligne avec frequence 266.
-- Environ 1300000 lignes pour la VF seule.
-- La cle primaire est composee de deux colonnes donc pas d AUTOINCREMENT.
-- WITHOUT ROWID fait servir la cle primaire d index et economise de la place.
-- ---------------------------------------------------------------------

CREATE TABLE apparait(
fk_MOT INTEGER NOT NULL,
fk_serie INTEGER NOT NULL,
langue TEXT NOT NULL CHECK (langue IN ('vf', 'vo')),
poids FLOAT NOT NULL,
frequence INT NOT NULL,
PRIMARY KEY (fk_MOT, fk_serie, langue),
FOREIGN KEY (fk_MOT) REFERENCES mot(Id_MOT) ON DELETE CASCADE,
FOREIGN KEY (fk_serie) REFERENCES serie(ID_Serie) ON DELETE CASCADE
) WITHOUT ROWID;

-- Permet de retrouver tous les mots d une serie.
-- Sert a la recommandation.
CREATE INDEX idx_apparait_serie ON apparait (fk_serie);

-- ---------------------------------------------------------------------
-- Notes de 1 a 5 donnees par un utilisateur a une serie.
-- La cle primaire composee garantit une seule note par utilisateur et par serie.
-- Renoter met a jour la ligne au lieu d en ajouter une.
-- ON DELETE CASCADE supprime les notes en meme temps que le compte.
-- ---------------------------------------------------------------------

CREATE TABLE Noter(
fk_serie INTEGER NOT NULL,
fk_utilisateur INTEGER NOT NULL,
note INT NOT NULL CHECK (note BETWEEN 1 AND 5),
date_notation DATE NOT NULL DEFAULT (CURRENT_DATE),
PRIMARY KEY (fk_utilisateur, fk_serie),
FOREIGN KEY (fk_utilisateur) REFERENCES utilisateur(Id_utilisateur) ON DELETE CASCADE,
FOREIGN KEY (fk_serie) REFERENCES serie(ID_Serie) ON DELETE CASCADE
);

-- Permet de retrouver qui a note une serie.
CREATE INDEX idx_noter_serie ON Noter (fk_serie);