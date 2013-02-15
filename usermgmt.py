# coding=utf-8

import os
import Cookie
import cgi
import random
import hashlib
import smtplib
import email.mime.text
import email.mime.multipart
import email.mime.application

import menu
import ticket
import html

class Login(object):
	def __init__(self, cookies=None, db=None, form=None, name=None):
		self.db = db
		if name is None:
			self.cookies = cookies
			try:
				self.cookies["USERNAME"] = form["username"].value
				self.cookies["PASSWORD"] = form["password"].value
			except:
				pass
		else:
			self.cookies = Cookie.SimpleCookie()
			self.cookies["USERNAME"] = name

	def __getitem__(self, item):
		c = self.db.cursor()
		if item in ["u_id", "name", "email", "salt", "pwhash", "paid", "there", "ticket", "note", "note_done"]:
			if self.name() is None:
				return None
			if c.execute("SELECT " + item + " FROM users WHERE name = %s", (self.name(),)) == 1L:
				return c.fetchone()[0]
			return None
		if item == "shirts":
			c.execute("SELECT size, girly FROM shirts WHERE u_id = %s", (self["u_id"], ))
			rv = {}
			for x in c.fetchall():
				if x[0] not in rv:
					rv[x[0]] = []
				rv[x[0]].append(x[1] == True)
			return rv
		if item == "lunch":
			l = (0, 0, "", False, False, False, False)
			if c.execute("SELECT * FROM lunch WHERE u_id = %s", (self["u_id"], )) != 0L:
				l = c.fetchone()
			return { "buns": l[2], "baloney": l[3], "cheese": l[4], "jam": l[5], "cornflakes": l[6] }
		raise KeyError("unknown key: %s" % str(item))

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
		if self["pwhash"] is None:
			return False
		m = hashlib.sha1()
		m.update(self.cookies["PASSWORD"].value)
		m.update(self["salt"])
		return self["pwhash"] == m.hexdigest()

	def setPass(self, password):
		salt = str(random.random())
		m = hashlib.sha1()
		m.update(password)
		m.update(salt)

		if self["u_id"] is not None:
			c = self.db.cursor()
			c.execute("UPDATE users SET salt = %s, pwhash = %s WHERE u_id = %s",
				(salt, m.hexdigest(), self["u_id"]))
			self.db.commit()
		return (salt, m.hexdigest())

	def changePass(self, form, conn):
		if not self.valid():
			print("<div class=\"alert alert-warning\">You need to be logged in!</div>")
			return
		error = False
		if form.getfirst("password") != form.getfirst("password_again"):
			print("<div class=\"alert alert-error\">Passwords don't match!</div>")
			error = True
		if form.getfirst("password") is None or error:
			print("<div class=\"row\">")
			print("<div class=\"span6\"><div class=\"well well-small\"><h2>Change Password</h2>")
			print(html.form_start(box=False))
			print(html.f_hidden("action", "changepass"))
			print(html.form_password("pass", "New Password", "password", "New Password"))
			print(html.form_password("pass2", "New Password (again)", "password_again", "New Password (again)"))
			print(html.form_submit())
			print(html.form_end(box=False))
			print("</div></div></div>")
			return
		c = conn.cursor()
		c.execute("SELECT u_id FROM users WHERE name = %s", self.name())
		uid = c.fetchone()[0]
		print("<div class=\"alert alert-info\">Password changed!</div>")
		self.setPass(form.getfirst("password"))

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
	pdf.add_header("Content-Disposition", "attachment", filename="ticket-" + ticket_no + ".pdf")
	pdf.replace_header("Content-Type", "application/pdf")

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

	login = Login(None, conn, None)
	(salt, digest) = login.setPass(passwd)
	rv = cursor.execute("INSERT INTO users (name, email, salt, pwhash) VALUES (%s, %s, %s, %s)",
				(name, email, salt, digest))
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
