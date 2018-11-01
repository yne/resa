#!/usr/bin/env python3
from flask import Flask
app = Flask(__name__)

@app.route('/api/<path:path>')
def api(path):
    return "hello"
# Media{Name, version<VO,VF,VOST> }
# User{pseudo}
# Join
# Event{creator:User, pendings:User, accepteds:User, media:Media, address:string, geo:LngLat}
#
#

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def fallback(path):
    return app.send_static_file("index.html")

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run()