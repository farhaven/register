# coding=utf-8

import os
import cgi
import random
import hashlib
import smtplib
import email.mime.text
import email.mime.multipart
import email.mime.application

import menu
import ticket

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
				"shirts": {},
				"lunch": {}
		}
		cursor.execute("SELECT size, girly FROM shirts WHERE u_id = %s", (result[0], ))
		for x in cursor.fetchall():
			if x[0] not in rv["shirts"]:
				rv["shirts"][x[0]] = []
			rv["shirts"][x[0]].append(x[1] == True)
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

def sendTicket(name, ticket_no, address):
	msg = email.mime.multipart.MIMEMultipart()
	msg["From"] = "register@eh13.c3pb.de"
	msg["Subject"] = "Dein Easterhegg 2013 Ticket"
	msg["To"] = address

	txt  = "Hallo " + str(name) + "!\n\n"
	txt += "Dein Ticket ist\n\n\t" + str(ticket_no) + "\n\n"
	txt += "Bitte druck dein Ticket im Anhang dieser Mail aus und bring den\n"
	txt += "Ausdruck zum Easterhegg mit, oder speicher diese Nachricht auf dem\n"
	txt += "Mobilkommunikationsgerät deiner Wahl, um sie bei der Ankunft\n"
	txt += "vorzeigen zu können.\n\n"
	txt += "\tDeine eh13-Orga"
	txt = email.mime.text.MIMEText(txt)
	txt.set_charset("utf-8")

	fname = ticket.build_ticket(ticket_no, name)
	fh = open(fname[1], "r")
	pdf = email.mime.application.MIMEApplication(fh.read())
	fh.close()
	os.unlink(fname[1])

	msg.attach(txt)
	msg.attach(pdf)

	s = smtplib.SMTP()
	s.connect()
	s.sendmail("register@eh13.c3pb.de", [ address ], msg.as_string())
	s.quit()

	return msg.as_string()

def addUser(data, conf, conn):
	name = cgi.escape(data.getfirst("username", ""))
	email = cgi.escape(data.getfirst("email", ""))
	passwd = cgi.escape(data.getfirst("password", ""))
	passwd_again = cgi.escape(data.getfirst("password_again", ""))

	failures = ""
	if name == "":
		failures += "<li>No username specified!</li>"
	if email == "" or email.count("@") != 1:
		failures += "<li>Invalid email specified!</li>"
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
	msg += "\tZweck  : EasterHegg 2013\n"
	msg += "\t         Teilnehmer " + str(name) + "\n\n"
	msg += "Alternativ geht auch:\n\n"
	msg += "\tZweck  : " + str(name) + "\"; DROP TABLE transactions;\"\n\n"
	msg += "Du kannst auch vor Ort in bar bezahlen, allerdings gibt es nur ein\n"
	msg += "limitiertes Kontingent an Tickets.\n\n"
	msg += "Deine eh13-Orga\n\n"
	msg += "P.S: Wenn du dich nicht registriert hast, melde dich bitte bei\n"
	msg += "orga@eh13.c3pb.de, damit wir dich aus der Datenbank austragen können."

	try:
		s = smtplib.SMTP()
		s.connect()
		s.sendmail("register@eh13.c3pb.de", [ email ], msg)
		s.quit()
	except Exception as err:
		return str(err)
	return None

if __name__ == "__main__":
	x = sendTicket("gbe", "foobar", "gbe@unobtanium.de")
	print(str(x))
