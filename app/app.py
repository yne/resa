#!/usr/bin/env python3
import db, types, jwt, time, datetime
from flask import Flask, request, g, send_from_directory, abort, make_response, jsonify
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

@app.before_request
def before_request():
	if "text/html" in request.accept_mimetypes.values():
		return send_from_directory('static', 'index.html')

@api.resource('/event/', '/event/<event_id>')
class Event(Resource):
	def is_queue(self, event, pos, total):
		if event['min'] and total < event['min']: return True
		if event['max'] and pos   > event['max']: return True
		if event['step'] and (pos > total - (total % event['step'])): return True
		return False
	def hydrate(self, event, parts):
		for i,p in enumerate(parts):
			p['queue'] = self.is_queue(event, i + 1, len(parts))
		event['parts'] = parts
	def by(self, **kwargs):
		return db.get('event',kwargs) or abort(404)

	def get(self, event_id=None): # TODO rework using sqlachemy
		events = None
		if event_id == None:
			events = [self.by(id=event_id)]
		else:
			kwargs = {}
			search = dict(request.args)
			if event_id in ['future', 'past']:
				search = {'date': datetime.date.today().strftime('%Y-%m-%d')}
				kwargs = {'op': '>=' if event_id == 'future' else '<'}
				event_id = None
			events = db.all('event', search, **kwargs)
		parts = db.all('participate', {'event':event_id} if event_id else {})
		for e in events:
			self.hydrate(e, [p for p in parts if p['event'] == e['id']])
		return events[0] if event_id else events
	def post(self):
		return db.insert('event', {**request.get_json(True),'owner':g.user["name"]})
	def put(self, event_id):
		return db.update('event', request.get_json(True),	{'id':event_id, 'owner':g.user["name"]})
	def delete(self, event_id):
		db.delete('event', {'id':event_id, 'owner':g.user["name"]}) or abort(403)
		return {}

@api.resource('/event/<int:event_id>/part', '/event/<int:event_id>/part/<int:part_id>')
class EventPart(Resource):
	def get(self, event_id, part_id=None):
		return {"event_id":event_id, "part_id":part_id}
	def post(self, event_id):
		vals = {'event':event_id, 'tick':int(time.time()*1000), 'user':g.user["name"]}
		return db.insert('participate', {**request.get_json(True), **vals})
	def put(self, event_id, part_id):
		vals = request.get_json(True)
		filtered_vals = {k: v for k, v in vals.items() if k not in ('id','event','tick')}
		cond = {'id':part_id, 'event':event_id, 'user':g.user["name"]}
		return db.update('participate', filtered_vals,	cond)
	def delete(self, event_id, part_id):
		where = {'id':part_id, 'event':event_id, 'user':g.user["name"]}
		db.delete('participate', where) or abort(403)
		return {}

@api.resource('/user/', '/user/<string:user_id>')
class User(Resource):
	@staticmethod
	def create(id):
		if not db.update('user',{'id':id}):
			db.insert('user',{'id':id})
	def get(self):
		return 42
	def post(self):
		return 42

@api.resource('/auth/')
class Auth(Resource):
	secret = app.secret_key or "your-256-bit-secret"
	cookies = {'header': (False, 0), 'payload': (False, 1), 'signature': (True, 2)}
	@staticmethod
	@app.before_request
	def auth_required():
		if request.method == 'GET' or request.path == '/auth/':
			return None
		try:
			cookie = [request.cookies.get(name) for name,(http,i) in Auth.cookies.items()]
			cookie = '.'.join(cookie) if all(cookie) else None
			header = request.headers.get('Authorization')
			header = header[len('Bearer '):] if header and header.startswith('Bearer ') else None
			g.user = jwt.decode(cookie or header, Auth.secret)
		except jwt.exceptions.DecodeError:
			abort(403)
	def delete(self):
		response = make_response("{}")
		for name, (http, _) in self.cookies.items():
			response.set_cookie(name, '', httponly=http, expires=0)
		return response
	def post(self):
		user = request.get_json(True) # ... or request.form.to_dict() ?
		#[first,last] = user['username'].split('.')
		#if app.config['LDAP_IP']:
		#	try:
		#		import ldap
		#		ldap.initialize('ldap://%s/'%app.config['LDAP_IP']).simple_bind_s(app.config['LDAP_CMD'] % (first[0]+last), user['password'])
		#	except Exception:
		#		abort(403)
		payload = {'name': user['username'], 'role': ['user','admin']}
		token = jwt.encode(payload, Auth.secret)
		response = make_response(jsonify(token))
		for name, (http, i) in self.cookies.items():
			response.set_cookie(name, token.split(b'.')[i], httponly=http)
		return response

db.setup("db.sql")
if __name__ == '__main__':
	app.run()