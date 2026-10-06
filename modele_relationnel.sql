
CREATE TABLE Mot (
Id_MOT VARCHAR(50) PRIMARY KEY,
libellé  VARCHAR(50) NOT NULL
); 

create TABLE Serie (
ID_Serie VARCHAR(50) PRIMARY KEY,
annee DATE DEFAULT (CURRENT_DATE()),
nb_saison INT NOT NULL DEFAULT 1,
Titre VARCHAR(50) NOT NULL,
nb_episode INT NOT NULL
);

CREATE table utilisateur (
Id_utilisateur VARCHAR(50) primary key,
pseudo VARCHAR (30),
email VARCHAR(50),
mot_de_passe VARCHAR(50),
date_creation DATE  DEFAULT (CURRENT_DATE())
);

CREATE TABLE apparait(
poids FLOAT,
frequence INT,
fk_MOT VARCHAR(50),
fk_serie VARCHAR(50),
PRIMARY KEY (fk_MOT, fk_serie),
foreign KEY (fk_MOT) REFERENCES mot(Id_MOT),
FOREIGN KEY(fk_serie) REFERENCES serie(ID_Serie)
);


CREATE TABLE Noter(
note int,
date_notation DATE  DEFAULT (CURRENT_DATE()),
fk_serie VARCHAR(50),
fk_utilisateur VARCHAR(50),
PRIMARY KEY (fk_utilisateur, fk_serie),
FOREIGN KEY(fk_utilisateur) REFERENCES mot(Id_utilisateur),
FOREIGN KEY(fk_serie) REFERENCES serie(ID_Serie)
);