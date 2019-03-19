CREATE TABLE event (id INTEGER PRIMARY KEY, owner TEXT, date TEXT, time TEXT, title TEXT, min INTEGER, max INTEGER, step INTEGER);
--INSERT INTO  event VALUES (null, 'rfontayne', '2001-01-01','01:01' ,'tenis', 4, 8, 2);

CREATE TABLE participate (id INTEGER PRIMARY KEY, tick INTEGER, event INTEGER, user text, message text, FOREIGN KEY(event) REFERENCES event(id) ON DELETE CASCADE);
--INSERT INTO  participate VALUES (1552776565150, 1, 'rfontayne', "J'ai 2 raquettes");
