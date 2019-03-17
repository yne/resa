CREATE TABLE event (id INTEGER PRIMARY KEY, owner TEXT, date TEXT, time TEXT, title TEXT, total INTEGER DEFAULT 0);
--INSERT INTO  event VALUES (null, 'rfontayne', '2001-01-01','01:01' ,'tenis', 4);

CREATE TABLE participate (id INTEGER PRIMARY KEY, event INTEGER, user text, message text, FOREIGN KEY(event) REFERENCES event(id) ON DELETE CASCADE);
--INSERT INTO  participate VALUES (1552776565150, 1, 'rfontayne', "J'ai 2 raquettes");
