#!/usr/bin/env python3
import flask, db, jwt, functools, os, datetime, threading, time

app = flask.Flask(__name__)
ldap_cmd_default = ['uid=%s','ou=Users'] + ['dc='+d for d in os.environ.get('LDAP_DC','').split('.')]
app.config['MAIL_URL'] = os.environ.get('MAIL_URL','http://event.example.com') # event.example.com
app.config['MAIL_SRV'] = os.environ.get('MAIL_SRV') # corporate.fr
app.config['MAIL_TIME'] = os.environ.get('MAIL_TIME')
app.config['LDAP_IP'] = os.environ.get('LDAP_IP') # ldap.corporate.prive
app.config['LDAP_DC'] = os.environ.get('LDAP_DC') # corporate.prive
app.config['LDAP_CMD'] = os.environ.get('LDAP_CMD', ','.join(ldap_cmd_default))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')

def sendmail(users, subject, content='', sender="bot", domain=app.config['MAIL_SRV']):
	print("%s@%s > %s : %s -- %s"%(sender, domain, users, subject, content))
	if not domain: return
	import smtplib, email
	msg = email.message.EmailMessage()
	msg.set_content(content)
	msg['Subject'] = subject
	msg['From'] = sender+'@'+domain
	msg['To'] = ','.join([u+'@'+domain for u in users])
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()
def reminder_thread(at):
	if not at: return
	import schedule
	def reminder():
		tick = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
		part = db.all('participate', {'tick': tick })
		print("Starting Reminder for %i events [%s]" % (len(part), tick))
		for p in part:
			sendmail(part, "Get ready for tomorrow !", f"See {app.config['MAIL_URL']}/e/{p.event}")
	schedule.every().day.at(at).do(reminder)
	while True:
		schedule.run_pending()
		time.sleep(5)

def strip(d, rem):
	for k in rem:d.pop(k, None)
	return d
def secure(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs):
		bearer = flask.request.headers.get('Authorization','Bearer ..')[len('Bearer '):]
		try:
			payload = jwt.decode(bearer, app.secret_key)
		except jwt.exceptions.DecodeError as e:
			flask.abort(403, e)
		return f(*args, **kwargs, auth=payload)
	return decorated
def queue(event, pos, total):
	if event['min'] and total < event['min']: return True
	if event['max'] and pos   > event['max']: return True
	if event['step'] and (pos > total - (total % event['step'])): return True
	return False
def json(obj, code=404):
	return ('', code) if obj is None else flask.jsonify(obj)
def getEvent(id):
	event = db.get('event', {'id':id})
	if not event: return None
	part = db.all('participate', {'event':id}, ('tick','ASC'))
	for i,p in enumerate(part):
		p['queue'] = queue(event, i + 1, len(part))
	return {**event,'part': part}

@app.route('/event/')
def event_list():
	return json(db.all('event', dict(flask.request.args)))

@app.route('/event/<id>', methods=['GET'])
def event_get(id):
	return json(getEvent(id))

@app.route('/event/', methods=['POST'])
@secure
def event_create(auth):
	return json(db.insert('event', {**flask.request.get_json(),'owner':auth["user"]}))

@app.route('/event/<id>', methods=['PUT'])
@secure
def event_update(id, auth):
	newval = strip(flask.request.get_json(),('id','owner'))
	users = [p['user'] for p in db.all('participate', {'event':id})]
	sendmail(users, f"Event {id} updated by "+auth["user"], f"Updated values are {newval}",auth["user"])
	return json(db.update('event', newval, {'id':id, 'owner':auth["user"]}))

@app.route('/event/<id>', methods=['DELETE'])
@secure
def event_delete(id, auth):
	users = [p['user'] for p in db.all('participate', {'event':id})]
	sendmail(users, f"Event {id} deleted by "+auth["user"], f"See %s/e/{id}"%app.config['MAIL_URL'], auth["user"])
	return json(db.delete('event', {'id':id, 'owner':auth["user"]}))

# Join
@app.route('/join/', methods=['GET'])
def join_list():
	return json(db.all('event,participate', {**flask.request.args, 'event.id':b'participate.event'}))

@app.route('/join/', methods=['POST'])
@secure
def event_join(auth):
	#if db.get('participate', {**strip(request.get_json(),('time')),'user':auth["user"]}): return '',409
	return json(db.insert('participate', {**flask.request.get_json(), 'tick':int(time.time()*1000), 'user':auth["user"]}))

@app.route('/join/<id>', methods=['DELETE'])
@secure
def event_leave(id, auth):
	res = db.get('event,participate',{'participate.id':id, 'event.id':b'participate.event'})
	if not res or auth["user"] not in [res['owner'], res['user']]:
		return '',404
	sendmail([res['owner']], auth["user"]+" Joined your event", f"See %s/e/{id}"%app.config['MAIL_URL'], auth["user"])
	return json(db.delete('participate', {'id':id}))

# Token
@app.route('/token', methods=['POST'])
def token_get():
	body = flask.request.get_json()
	if app.config['LDAP_IP']:
		try:
			import ldap
			print('ldap://%s/'%app.config['LDAP_IP'])
			print(app.config['LDAP_CMD'] % body['user'])
			ldap.initialize('ldap://%s/'%app.config['LDAP_IP']).simple_bind_s(app.config['LDAP_CMD'] % body['user'], body['pass'])
		except Exception as e:
			return str(e),"403 " + str(e)
	return json(jwt.encode({'user': body['user']}, app.secret_key))

@app.errorhandler(404)
def send_index(path):
	return flask.send_from_directory('static', 'index.html')

db.setup('db.sql')
threading.Thread(target = reminder_thread, args = (app.config['MAIL_TIME'],)).start()
if __name__ == "__main__":
	app.run(host='0.0.0.0')
