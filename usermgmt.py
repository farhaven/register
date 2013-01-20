import cgi
import random
import hashlib

import menu

class Login(object):
	def __init__(self, cookies, db, form):
		self.cookies = cookies
		self.db = db
		try:
			self.cookies["USERNAME"] = form["username"].value
			self.cookies["PASSWORD"] = form["password"].value
		except:
			pass

	def as_dict(self):
		cursor = self.db.cursor()
		if cursor.execute("SELECT * FROM users WHERE name = %s", (self.name(), )) != 1L:
			return {}
		result = cursor.fetchone()
		rv = {
				"name": result[1],
				"email": result[2],
				"salt": result[3],
				"pwhash": result[4],
				"has_paid": bool(result[5]),
				"is_there": bool(result[6]),
				"shirts": [],
				"lunch": {}
		}
		cursor.execute("SELECT size FROM shirts WHERE u_id = %s", (result[0], ))
		for x in cursor.fetchall():
			rv["shirts"].append(x[0])
		if cursor.execute("SELECT buns, baloney, cheese, jam, cornflakes FROM lunch WHERE u_id = %s", (result[0], )) != 1L:
			rv["lunch"]["buns"] = ""
			rv["lunch"]["baloney"] = False
			rv["lunch"]["cheese"] = False
			rv["lunch"]["jam"] = False
			rv["lunch"]["cornflakes"] = False
		else:
			l = cursor.fetchone()
			rv["lunch"]["buns"] = l[0]
			rv["lunch"]["baloney"] = l[1]
			rv["lunch"]["cheese"] = l[2]
			rv["lunch"]["jam"] = l[3]
			rv["lunch"]["cornflakes"] = l[4]
		return rv

	def name(self):
		try:
			return self.cookies["USERNAME"].value
		except:
			return None

	def clear(self):
		self.cookies["USERNAME"] = None
		self.cookies["PASSWORD"] = None

	def validate(self, data):
		self.cookies["USERNAME"] = data.getfirst("username")
		self.cookies["PASSWORD"] = data.getfirst("password")
		return self.valid()

	def valid(self):
		user = self.as_dict()
		if "pwhash" not in user:
			return False
		m = hashlib.sha1()
		m.update(self.cookies["PASSWORD"].value)
		m.update(user["salt"])
		return user["pwhash"] == m.hexdigest()

def addUser(data, conf, conn):
	name = cgi.escape(data.getfirst("username", ""))
	email = cgi.escape(data.getfirst("email", ""))
	passwd = cgi.escape(data.getfirst("password", ""))
	passwd_again = cgi.escape(data.getfirst("password_again", ""))

	failures = ""
	if name == "":
		failures += "<li>No username specified!</li>"
	if email == "":
		failures += "<li>No email specified!</li>"
	if passwd == "":
		failures += "<li>Password empty!</li>"
	if passwd != passwd_again:
		failures += "<li>Passwords do not match!</li>"
	cursor = conn.cursor()
	if cursor.execute("SELECT u_id FROM users WHERE name = %s", (name, )) != 0L:
		failures += "<li>Username already taken!</li>"
	cursor.execute("SELECT count(*) FROM users")
	if cursor.fetchone()[0] >= conf.get("maxusers"):
		failures += "<li>There are already " + str(conf.get("maxusers")) + " registered users, registration is closed. Sorry :(</li>"
	if failures != "":
		#print("<h1>Creating user failed</h1>")
		print("<div class=\"alert alert-error\">Failed to create user:<ul>")
		print(failures)
		print("</ul></div>")
		return

	salt = str(random.random())
	m = hashlib.sha1()
	m.update(passwd)
	m.update(salt)
	rv = cursor.execute("INSERT INTO users (name, email, salt, pwhash) VALUES (%s, %s, %s, %s)",
				(name, email, salt, m.hexdigest()))
	conn.commit()
	#print("<h1>User created</h1>")
	print("<div class=\"alert alert-success\">Creation of user " + name + " was successful.</div>")
