#!/usr/bin/env python3
import flask, db, jwt, threading, srv, time, os

app = flask.Flask(__name__)
srv.configure(app)

def json(obj):
	return ('', 404) if obj is None else flask.jsonify(obj)

@app.route('/event/')
def event_list():
	return json(db.all('event', dict(flask.request.args)))

@app.route('/event/<id>', methods=['GET'])
def event_get(id):
	return json(srv.getEvent(id))

@app.route('/event/', methods=['POST'])
@srv.secure
def event_create(auth):
	return json(db.insert('event', {**flask.request.get_json(),'owner':auth["user"]}))

@app.route('/event/<id>', methods=['PUT'])
@srv.secure
def event_update(id, auth):
	newval = srv.strip(flask.request.get_json(),('id','owner'))
	oldval = srv.strip(db.get('event', {'id':id}),('id','owner'))
	change = newval.items() - oldval.items()
	if not change: return ('',304)
	users = [p['user'] for p in db.all('participate', {'event':id})]
	update = db.update('event', newval, {'id':id, 'owner':auth["user"]})
	srv.sendmail(auth["user"], users, f"Event {oldval['title']} updated by {auth['user']}", f"Updated values are {change}")
	return json(update)

@app.route('/event/<id>', methods=['DELETE'])
@srv.secure
def event_delete(id, auth):
	users = [p['user'] for p in db.all('participate', {'event':id})]
	event = db.get('event',{'id':id})
	if not event: return ('',404)
	rows = db.delete('event', {'id':id, 'owner':auth["user"]})
	if rows: srv.sendmail(auth["user"], users, f"Event %s [%s %s] deleted by %s"%(event['title'], event['date'], event['time'], auth["user"]), f"")
	return json(rows)

# Join
@app.route('/join/', methods=['GET'])
def join_list():
	return json(db.all('event,participate', {**flask.request.args, 'event.id':b'participate.event'}))

@app.route('/join/', methods=['POST'])
@srv.secure
def event_join(auth):
	#if db.get('participate', {**strip(request.get_json(),('time')),'user':auth["user"]}): return '',409
	return json(db.insert('participate', {**flask.request.get_json(), 'tick':int(time.time()*1000), 'user':auth["user"]}))

@app.route('/join/<id>', methods=['DELETE'])
@srv.secure
def event_leave(id, auth):
	res = db.get('event,participate',{'participate.id':id, 'event.id':b'participate.event'})
	if not res or auth["user"] not in [res['owner'], res['user']]:
		return '',404
	srv.sendmail(auth["user"], [res['owner']], auth["user"]+" Joined your event", f"See %s/e/{id}"%app.config['MAIL_URL'])
	return json(db.delete('participate', {'id':id}))

# Token
@app.route('/token', methods=['POST'])
def token_get():
	body = flask.request.get_json()
	if app.config['LDAP_IP']:
		try:
			import ldap
			ldap.initialize('ldap://%s/'%app.config['LDAP_IP']).simple_bind_s(app.config['LDAP_CMD'] % body['user'], body['pass'])
		except Exception as e:
			return str(e),"403 " + str(e)
	return json(jwt.encode({'user': body['user']}, app.secret_key))

@app.errorhandler(404)
def send_index(path):
	return flask.send_from_directory('static', 'index.html')

db.setup(app.config['DATABASE'])
if __name__ == "__main__":
	threading.Thread(target = srv.reminder_thread, args = (app.config['MAIL_TIME'],)).start()
	app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', '5000')))
