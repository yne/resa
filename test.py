#!/usr/bin/env python3
from json import dumps
from bottle import Bottle, HTTPError, get, post, request, response
from bottle.ext import sqlite

app = Bottle()
conn=sqlite.Plugin(dbfile='db');
#conn.row_factory = sqlite3.Row;
#conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
app.install(conn)
"""
CREATE TABLE user  (name VARCHAR(32) PRIMARY KEY NOT NULL, password TEXT NOT NULL, bio TEXT);
CREATE TABLE media (name VARCHAR(96),s INTEGER, e INTEGER, v INTEGER);
CREATE TABLE event (at VARCHAR(20), lng REAL,lat REAL, addr, creator TEXT, media INTEGER, FOREIGN KEY(creator) REFERENCES user(name) , FOREIGN KEY(media) REFERENCES media(rowid));
CREATE TABLE wish  (user TEXT, event INTEGER, granted INTEGER, FOREIGN KEY(user) REFERENCES user(name), FOREIGN KEY(event) REFERENCES event(rowid));
"""
def dict_from_row(row):
    return dict(zip(row.keys(), row))
@app.get('/')
def user_page():
    return """
    <h1>User </h1><form method=POST action=user ><input name=name><input type=password name=password><input type=submit></form>
    <h1>Media</h1><form method=POST action=media><input name=name><input type=submit></form>
    <h1>Event</h1><form method=POST action=event><input name=at><input name=creator><input type=submit></form>
    <h1>Wish </h1><form method=POST action=wish><input name=at><input name=creator><input type=submit></form>
    """

@app.get('/user/:name')
def user_get(name, db):
    row = db.execute('SELECT * from user where name=?', name).fetchone()
    return row if row else HTTPError(404)
@app.get('/user/')
def user_list(db):
    curr = db.execute('SELECT * from user')
    return dumps([dict(zip([i[0] for i in curr.description], i)) for i in curr.fetchall()])
@app.post('/user')
def user_post(db):
    row = db.execute('INSERT INTO user (name, password) VALUES (?,?)', (request.forms.get('name'), request.forms.get('password')) ).fetchone()
    #return "<a href=/user/%s>%s</a>"%(row,row)

app.run(host='localhost', port=8080, debug=True, reloader=True)