import os, sqlite3
DB_NAME = 'db.sqlite'

class db(object):
	def __init__(self, path, map=False):
		self.path = path
	def __enter__(self):
		self.conn = sqlite3.connect(self.path)
		#self.conn.set_trace_callback(print)
		self.conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
		self.conn.execute('PRAGMA foreign_keys = ON')
		return self.conn.cursor()
	def __exit__(self, exc_class, exc, traceback):
		self.conn.commit()
		self.conn.close()

def _where(keys, action=' WHERE ', j=' AND ',op='='):
	return action + j.join([k+op+(v.decode() if type(v) is bytes else '?') for (k,v) in keys.items()]) if keys else ''
def _values(keys):
	return [v for v in keys.values() if type(v) in (str,int)]
def _order(by):
	return f' ORDER BY {by[0]} {by[1]}' if by else ''

def setup(script):
	if not os.path.isfile(DB_NAME) or not os.path.getsize(DB_NAME):
		with db(DB_NAME) as c:
			with open(script, 'r') as myfile:
				c.executescript(myfile.read())
def update(table, keys=dict(), cond=dict()):
	with db(DB_NAME) as c:
		c.execute(f"UPDATE {table}" + _where(keys, ' SET ', ',') + ' ' + _where(cond), list(keys.values()) + list(cond.values()))
		return c.rowcount
def insert(table, keys=dict()):
	with db(DB_NAME) as c:
		cols = ', '.join(keys.keys())
		vals = ',:'.join(keys.keys())
		c.execute(f'INSERT INTO {table} ({cols}) VALUES (:{vals})', _values(keys))
		return c.lastrowid
def all(table, cond=dict(), order=None, **argp):
	with db(DB_NAME) as c:
		return c.execute(f"SELECT * FROM {table}" + _where(cond,**argp) + _order(order), _values(cond)).fetchall()
def get(table, cond=dict()):
	with db(DB_NAME) as c:
		return c.execute(f"SELECT * FROM {table}" + _where(cond), _values(cond)).fetchone()
def delete(table, cond=dict()):
	with db(DB_NAME) as c:
		c.execute(f"DELETE FROM {table}" + _where(cond), _values(cond))
		return c.rowcount
