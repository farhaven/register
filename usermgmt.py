# coding=utf-8

import cgi
import random
import hashlib
import smtplib

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
				"ticket": str(result[7]),
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
		return "<ul>" + failures + "</ul>"

	salt = str(random.random())
	m = hashlib.sha1()
	m.update(passwd)
	m.update(salt)
	rv = cursor.execute("INSERT INTO users (name, email, salt, pwhash) VALUES (%s, %s, %s, %s)",
				(name, email, salt, m.hexdigest()))
	conn.commit()
	#print("<h1>User created</h1>")

	msg  = "To: " + str(email) + "\n"
	msg += "Subject: Willkommen\n"
	msg += "Content-type: text/plain; charset=utf-8\n"
	msg += "Content-Transfer-Encoding: 8bit\n"
	msg += "\nHallo " + str(name) + ",\n\n"
	msg += "deine Registrierung war erfolgreich. Du kannst auf\n"
	msg += "https://register.eh13.c3pb.de deinen Bezahlstatus einsehen\n"
	msg += "und deine Frühstücks- und Shirtbestellung verwalten.\n\n"
	msg += "Überweise bitte die 42 Euro für das Ticket an das folgende Konto:\n\n"
	msg += "\tInhaber: C3PB e.V.\n"
	msg += "\tKto-Nr : 8744126200\n"
	msg += "\tBLZ    : 47260121 (Volksbank Paderborn)\n"
	msg += "\tZweck  : EasterHegg 2013 Teilnehmer " + str(name) + "\n\n"
	msg += "Du kannst auch vor Ort in bar bezahlen, allerdings gibt es nur ein limitiertes Kontingent an Tickets.\n\n"
	msg += "Deine eh13-Orga\n\n"
	msg += "P.S: Wenn du dich nicht registriert hast, melde dich bitte bei\n"
	msg += "root@eh13.c3pb.de, damit wir dich aus der Datenbank austragen können."

	try:
		s = smtplib.SMTP()
		s.connect()
		s.sendmail("register@eh13.c3pb.de", [ email ], msg)
		s.quit()
	except Exception as err:
		return str(err)
	return None
