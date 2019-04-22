CREATE TABLE event (
  id INTEGER PRIMARY KEY, owner TEXT,
  date TEXT,
  time TEXT,
  title TEXT,
  detail TEXT,
  min INTEGER,
  max INTEGER,
  step INTEGER
);

CREATE TABLE participate (
  id INTEGER PRIMARY KEY,
  tick INTEGER,
  event INTEGER,
  user TEXT,
  message TEXT,
  FOREIGN KEY(event) REFERENCES event(id) ON DELETE CASCADE
);

