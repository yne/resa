import flask, db, jwt, functools, os, datetime, time
__app__ = None
def configure(app):
	ldap_cmd_default = ['uid=%s','ou=Users'] + ['dc='+d for d in os.environ.get('LDAP_DC','').split('.')]
	app.config['MAIL_URL'] = os.environ.get('MAIL_URL','http://event.example.com') # event.example.com
	app.config['MAIL_SRV'] = os.environ.get('MAIL_SRV') # corporate.fr
	app.config['MAIL_TIME'] = os.environ.get('MAIL_TIME')
	app.config['LDAP_IP'] = os.environ.get('LDAP_IP') # ldap.corporate.prive
	app.config['LDAP_DC'] = os.environ.get('LDAP_DC') # corporate.prive
	app.config['LDAP_CMD'] = os.environ.get('LDAP_CMD', ','.join(ldap_cmd_default))
	app.config['DATABASE'] = os.environ.get('DATABASE', 'db.sql')
	app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
	global __app__
	__app__ = app
	

def sendmail(From, To, subject='', content=''):
	domain=__app__.config['MAIL_SRV']
	if not domain or not To: return
	print("%s@%s > %s : %s -- %s"%(From, domain, To, subject, content))
	import smtplib, email
	msg = email.message.EmailMessage()
	msg.set_content(content)
	msg['Subject'] = '📅 '+subject
	msg['From'] = From+'@'+domain
	msg['To'] = ','.join([u+'@'+domain for u in To])
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()
def reminder_thread(at):
	if not at: return
	import schedule
	def reminder():
		date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
		parts = db.all('participate,event', {'date': date, 'participate.event':b'event.id'})
		print("[%s] Starting Reminder for %s" % (date, [part['user'] for part in parts]))
		for part in parts:
			sendmail(part['owner'], [part['user']], f"{part['title']} is tomorrow !", f"See {__app__.config['MAIL_URL']}/e/{part['event']}")
	t = schedule.every().day.at(at).do(reminder)
	print(t)
	while True:
		schedule.run_pending()
		time.sleep(10)

def strip(d, rem):
	for k in rem:d.pop(k, None)
	return d
def secure(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs):
		bearer = flask.request.headers.get('Authorization','Bearer ..')[len('Bearer '):]
		try:
			payload = jwt.decode(bearer, __app__.secret_key)
		except jwt.exceptions.DecodeError as e:
			flask.abort(403, e)
		return f(*args, **kwargs, auth=payload)
	return decorated
def queue(event, pos, total):
	if event['min'] and total < event['min']: return True
	if event['max'] and pos   > event['max']: return True
	if event['step'] and (pos > total - (total % event['step'])): return True
	return False
def getEvent(id):
	event = db.get('event', {'id':id})
	if not event: return None
	part = db.all('participate', {'event':id}, ('tick','ASC'))
	for i,p in enumerate(part):
		p['queue'] = queue(event, i + 1, len(part))
	return {**event,'part': part}
