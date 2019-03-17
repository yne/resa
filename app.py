#!/usr/bin/env python3
from flask import jsonify, request
import flask, db, jwt, functools, os

app = flask.Flask(__name__)
app.config['LDAP_URI'] = os.environ.get('LDAP_URI')
app.config['LDAP_CMD'] = os.environ.get('LDAP_CMD')
app.config['MAIL_SRV'] = os.environ.get('MAIL_SRV')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')

def sendmail(users, subject, content='', sender="bot", domain=app.config['MAIL_SRV']):
	print("%s@%s > %s : %s -- %s"%(sender, domain, users, subject, content))
	if not domain: return
	import smtplib, email
	msg = email.message.EmailMessage()
	msg.set_content(content)
	msg['Subject'] = subject
	msg['From'] = sender+'@'+domain
	msg['To'] = ','.join([u+domain for u in users])
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()
def strip(d, rem):
	for k in rem:d.pop(k, None)
	return d
def secure(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs):
		bearer = request.headers.get('Authorization','Bearer ..')[len('Bearer '):]
		try:
			payload = jwt.decode(bearer, app.secret_key)
		except jwt.exceptions.DecodeError as e:
			flask.abort(403, e)
		return f(*args, **kwargs, auth=payload)
	return decorated

@app.route('/event/')
def event_list():
	return jsonify(db.all('event', dict(request.args)))

@app.route('/event/<id>', methods=['GET'])
def event_get(id):
	event = db.get('event', {'id':id})
	if not event: return ('',404)
	return jsonify({**event, 'part':db.all('participate', {'event':id}) })

@app.route('/event/', methods=['POST'])
@secure
def event_create(auth):
	return jsonify(db.insert('event', {**request.get_json(),'owner':auth["user"]}))

@app.route('/event/<id>', methods=['PUT'])
@secure
def event_update(id, auth):
	newval = strip(request.get_json(),('id','owner'))
	users = [p['user'] for p in db.all('participate', {'event':id})]
	sendmail(users, f"Event {id} updated by "+auth["user"], f"Updated values are {newval}",auth["user"])
	return jsonify(db.update('event', newval, {'id':id, 'owner':auth["user"]}))

@app.route('/event/<id>', methods=['DELETE'])
@secure
def event_delete(id, auth):
	users = [p['user'] for p in db.all('participate', {'event':id})]
	sendmail(users, f"Event {id} deleted by "+auth["user"], f"You received this mail because you joined the event",auth["user"])
	return jsonify(db.delete('event', {'id':id, 'owner':auth["user"]}))

# Join
@app.route('/join/', methods=['GET'])
def join_list():
	return jsonify(db.all('event,participate', {**request.args, 'event.id':b'participate.event'}))

@app.route('/join/', methods=['POST'])
@secure
def event_join(auth):
	#if db.get('participate', {**strip(request.get_json(),('time')),'user':auth["user"]}): return '',409
	return jsonify(db.insert('participate', {**request.get_json(), 'user':auth["user"]}))

@app.route('/join/<id>', methods=['DELETE'])
@secure
def event_leave(id, auth):
	res = db.get('event,participate',{'participate.id':id, 'event.id':b'participate.event'})
	if not res or auth["user"] not in [res['owner'], res['user']]:
		return '',404
	return jsonify(db.delete('participate', {'id':id}))

# Token
@app.route('/token', methods=['POST'])
def token_get():
	body = request.get_json()
	if app.config['LDAP_URI'] and app.config['LDAP_CMD']:
		try:
			import ldap
			ldap.initialize(app.config['LDAP_URI']).simple_bind_s(app.config['LDAP_CMD'] % body['user'], body['pass'])
		except Exception as e:
			return str(e),"403 " + str(e)
	return jsonify(jwt.encode({'user': body['user']}, app.secret_key))

@app.errorhandler(404)
def send_index(path):
	return flask.send_from_directory('static', 'index.html')

db.setup('db.sql')
if __name__ == "__main__":
	app.run(host='0.0.0.0')
