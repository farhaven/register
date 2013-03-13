# coding=utf-8

from __future__ import print_function

import os
import os.path
import cgi
import html
import urllib
import email.mime.text
import smtplib
import uuid
import sys
import random

import traceback

import usermgmt

def header(login, active="home"):
	s  = "<div class=\"navbar navbar-inverse navbar-fixed-top\">"
	s +=   "<div class=\"navbar-inner\"><div class=\"container\">"
	s +=     "<a class=\"btn btn-navbar\" data-toggle=\"collapse\" data-target=\".nav-collapse\">"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=     "</a>"
	s +=     "<a class=\"brand\" href=\"/\">EasterHegg 2013 - Registration</a>"
	s +=     "<div class=\"nav-collapse collapse\">"
	s +=       "<ul class=\"nav\">"
	if (active != "ADMIN"):
		if (login.valid()):
			s += "<li class=\"" 
			s += "active" if active == "home" else ""
			s += "\"><a href=\"/\">Home</a></li>"

			s += "<li class=\"\"><a href=\"http://eh13.c3pb.de/\" target=\"_blank\">Webseite</a></li>"
			#s += "<li><a href=\"#about\">About</a></li>"
			#s += "<li><a href=\"#contact\">Contact</a></li>"

			s += "<li class=\"\"><a href=\"?action=changepass\">Change password</a></li>"
			s += "<li class=\""
			s += "active" if active == "logout" else ""
			s += "\"><a href=\"/?action=logout\">Logout</a></li>"
		else:
			s += "<li class=\"active\"><a href=\"/\">Login</a></li>"
			s += "<li class=\"\"><a href=\"http://eh13.c3pb.de/\" target=\"_blank\">Webseite</a></li>"
	else:
		s += "<li class=\"\"><a href=\"/\">User-Mode</a></li>"
	s +=       "</ul>"
	s +=       "<ul class=\"nav pull-right\">"
	s +=         "<li class=\"" + ("active" if active == "ADMIN" else "") + "\"><a href=\"/admin\">Admin</a></li>"
	s +=       "</ul>"
	s +=     "</div>"
	s +=   "</div></div>"
	s += "</div>\n"
	s += "<div class=\"container\">"
 
	return s

def footer():
	s  = "</div>"
	return s

def admin(conf, conn):
	form = cgi.FieldStorage()
	cursor = conn.cursor()

	if form.getfirst("action") == "delete":
		if cursor.execute("SELECT u_id FROM users WHERE name = %s", (form.getfirst("user", ""), )) == 1L:
			uid = cursor.fetchone()[0]
			cursor.execute("DELETE FROM shirts WHERE u_id = %s", (uid, ))
			cursor.execute("DELETE FROM lunch WHERE u_id = %s", (uid, ))
			cursor.execute("DELETE FROM users WHERE u_id = %s", (uid, ))
			conn.commit()
	elif form.getfirst("action") == "setthere":
		val = True if form.getfirst("value") == "yes" else False
		rv = cursor.execute("UPDATE users SET there = %s WHERE name = %s", (val, form.getfirst("user", "")))
		conn.commit()
	elif form.getfirst("action") == "resetpw":
		user = usermgmt.Login(db=conn, name=form.getfirst("user", ""))
		print("<div class=\"alert alert-info\">PW reset for " + str(user.name()) + " requested</div>")
		passwd = str(random.random())
		user.setPass(passwd)
		txt  = "Hallo " + str(user.name()) + "!\n\n"
		txt += "Dein Passwort für https://register.eh13.c3pb.de wurde auf\n\n"
		txt += "\t" + passwd + "\n\n"
		txt += "gesetzt. Bitte ändere dein Passwort so schnell wie möglich.\n\n"
		txt += "\tDeine eh13-Orga"
		txt  = email.mime.text.MIMEText(txt)
		txt.set_charset("utf-8")
		txt["From"] = "register@eh13.c3pb.de"
		txt["Subject"] = "Passwort-Reset"
		txt["To"] = user["email"]
		s = smtplib.SMTP()
		s.connect()
		s.sendmail("register@eh13.c3pb.de", [ user["email"] ], txt.as_string())
		s.quit()
	elif form.getfirst("action") == "setpaid":
		try:
			cursor.execute("SELECT u_id FROM users WHERE name = %s", (form.getfirst("user", ""), ))
			uid = int(cursor.fetchone()[0])
			val = True if form.getfirst("value") == "yes" else False
			cursor.execute("UPDATE users SET paid = %s WHERE u_id = %s", (val, uid))
			cursor.execute("SELECT ticket FROM users WHERE u_id = %s", (uid, ))
			if val and cursor.fetchone()[0] is None:
				ticket = str(uuid.uuid4())
				cursor.execute("UPDATE users SET ticket = %s WHERE u_id = %s", (ticket, uid))
				cursor.execute("SELECT email FROM users WHERE u_id = %s", (uid, ))
				usermgmt.sendTicket(form.getfirst("user", ""), ticket, cursor.fetchone()[0])
			elif not val:
				cursor.execute("UPDATE users SET ticket = NULL WHERE u_id = %s", (uid, ))
		except Exception as err:
			print("<div class=\"alert alert-error\"><pre>")
			traceback.print_exc(file=sys.stdout)
			print("</pre></div>")
		finally:
			conn.commit()
	elif form.getfirst("action") == "mark_done":
		try:
			u_id = int(form.getfirst("user"))
			val = True if form.getfirst("value") == "yes" else False
			cursor.execute("UPDATE users SET note_done = %s WHERE u_id = %s", (val, u_id))
		except Excetion as err:
			print("<div class=\"alert alert-error\"><pre>")
			traceback.print_exc(file=sys.stdout)
			print("</pre></div>")
		finally:
			conn.commit()


	cursor.execute("SELECT count(*), COALESCE(sum(paid), 0), COALESCE(sum(there), 0) FROM users")
	print("<h1>%d Benutzer (%d haben bezahlt, %d sind da)</h1>" % cursor.fetchone())
	print("<div><table class=\"table table-bordered table-hover\">")
	print(html.tb_row(["Name<br/>(Klick f&uuml;r PW-Reset)", "L&ouml;schen", "Hat bezahlt", "Ist da", "Shirts", "Ticket"], head=True))
	cursor.execute("SELECT u_id, name, email, paid, there, ticket FROM users");
	for x in sorted(cursor.fetchall(), key=lambda x: str(x[1]).lower()):
		user = {
			"name": x[1],
			"email": x[2],
			"has_paid": bool(x[3]),
			"is_there": bool(x[4]),
			"ticket": str(x[5]),
			"shirts": []
		}
		cursor.execute("SELECT size, girly FROM shirts WHERE u_id = %s", (x[0], ))
		for s in cursor.fetchall():
			user["shirts"].append(("G" if s[1] == True else "R") + "_" + s[0])
		tbl_user  = "<span title=\"" + cgi.escape(user["email"]) + "\">"
		tbl_user += "<a href=\"?action=resetpw&user=" + urllib.quote(user["name"]) + "\" onclick=\"return confirm('Sure?');\">"
		tbl_user += cgi.escape(user["name"])
		tbl_user += "</a>"
		tbl_user += "</span>"

		tbl_del = "<a class=\"btn btn-warning\" href=\"?action=delete&user=" + urllib.quote(user["name"]) + "\" onclick=\"return confirm('Are you serious, bro?');\"><i class=\"icon-trash\"></i></a>"
		tbl_paid = "<a href=\"?action=setpaid&user=" + urllib.quote(user["name"]) + "&value="
		if user["has_paid"]:
			tbl_paid += "no\" class=\"btn btn-success\"><i class=\"icon-ok\"></i></a>"
		else:
			tbl_paid += "yes\" class=\"btn btn-danger\"><i class=\"icon-remove\"></i></a>"
		tbl_there = "<a href=\"?action=setthere&user=" + urllib.quote(user["name"]) + "&value="
		if user["is_there"]:
			tbl_there += "no\" class=\"btn btn-success\"><i class=\"icon-ok\"></i></a>"
		else:
			tbl_there += "yes\" class=\"btn btn-danger\"><i class=\"icon-remove\"></i></a>"
		print(html.tb_row([tbl_user, tbl_del, tbl_paid, tbl_there, user["shirts"], user["ticket"]]))
	print("</table></div>")

	print("<h1>Frystyck</h1>")
	print("<div><table class=\"table table-bordered\">")
	print(html.tb_row(["Br&ouml;tchen", "Wurscht", "K&auml;se", "Marmelade", "Cornflakes"], head=True))
	cursor.execute("SELECT sum(buns), sum(baloney), sum(cheese), sum(jam), sum(cornflakes) FROM lunch")
	print(html.tb_row(cursor.fetchone()))
	print("</table></div>")

	print("<h1>Shirts</h1>")
	print("<div><table class=\"table table-bordered\">")
	print(html.tb_row(["Gr&ouml;&szlig;e", "Anzahl gesamt", "Anzahl Girlies"], head=True))
	for s in [ "S", "M", "L", "XL", "XXL", "XXXL", "4XL" ]:
		row = [s]
		cursor.execute("SELECT count(*), COALESCE(sum(girly), 0) FROM shirts WHERE size = %s", (s, ))
		row.extend(cursor.fetchone())
		print(html.tb_row(row))
	print("</table></div>")

	print("<h1>Bemerkungen an die Orga</h1>")
	print("<div><table class=\"table table-bordered\">")
	print(html.tb_row(["Benutzer", "Bemerkung", "Done"], head=True))
	cursor.execute("SELECT u_id, name, email, note, note_done FROM users WHERE note IS NOT NULL AND note <> \"\"")
	for (u_id, name, email, note, note_done) in sorted(cursor.fetchall(), key=lambda x: str(x[1]).lower()):
		note = note.replace("\n", "<br/>")
		done = "<a class=\"btn btn-%s\" href=\"?action=mark_done&value=%s&user=%s\"><i class=\"icon-%s\"></i></a>"
		done = done % ("success" if note_done else "danger", "no" if note_done else "yes", str(u_id), "ok" if note_done else "remove")
		print(html.tb_row(["<span title=\"" + cgi.escape(email) + "\">" + name + "</span>", note, done]))
	print("</table></div>")

	print("<h1>Admins</h1>")
	print("<h2>Registrierte Admins</h2>")
	print("<div><ul>")
	try:
		fh = open("../passwd", "r")
		for l in fh.readlines():
			print("<li>" + cgi.escape(l.split(":")[0]) + "</li>")
		fh.close()
	except:
		pass
	print("</ul></div>")

	print("<div><h2>Neuen Admin hinzuf&uuml;gen</h2>")
	print("<p>Ich bin zu faul das zu &uuml;bersetzen... (gbe)</p>")
	print("<p>Admins are registerd in <code>/www/register/passwd</code>, which is a htpasswd file. To add a new admin do the following:")
	print("<pre>")
	print("$ ssh root@eh13.c3pb.de")
	print("# cd /www/register")
	print("# htpasswd passwd &lt;user&gt;")
	print("New password: &lt;foo&gt;")
	print("Re-type new password: &lt;foo&gt;")
	print("Adding password for user &lt;user&gt;")
	print("# ^D")
	print("</pre></p>")
	print("</div>")

def main(login, conf, conn):
	# new user
	if not login.valid():
		print("<div class=\"row\">")

		print("<div class=\"span6\"><div class=\"well well-small\"><h2>Log in</h2>")
		print(html.form_start(box=False))
		print(html.f_hidden("action", "login"))
		print(html.form_input("login_name", "Name", "username"))
		print(html.form_password("login_pass", "Password", "password"))
		print(html.form_submit())
		print(html.form_end(box=False))
		print("</div></div>")

		c = conn.cursor()
		c.execute("SELECT count(*) FROM users")
		if c.fetchone()[0] < conf.get("maxusers"):
			print("<div class=\"span6\"><div class=\"well well-small\"><h2>Neuer Benutzer</h2>")
			print(html.form_start(box=False))
			print(html.f_hidden("action", "add_user"))
			print(html.form_input("new_name", "Name", "username", placeholder="bernd"))
			print(html.form_input("new_mail", "E-Mail", "email", placeholder="user@chaos.hack"))
			print(html.form_password("new_pass", "Passwort", "password", placeholder="fefe123"))
			print(html.form_password("new_pass2", "Passwort (nochmal)", "password_again"))
			print(html.form_submit())
			print(html.form_end(box=False))
			print("</div></div>")
		else:
			print("<div class=\"span6\"><h2>Registrierung geschlossen</h2>")
			print("Die Registrierung ist geschlossen. Es sind schon min. " + str(conf.get("maxusers")) + " Wesen registriert. Sorry :(")
			print("</div>")

		print("</div>")
		return

	print("<div class=\"row\"><div class=\"span12\">")
	print("<table class=\"table table-bordered userstatus\">")
	print("<thead><tr><th colspan=\"2\">Status f&uuml;r " + cgi.escape(login["name"]) + " &lt;" + cgi.escape(login["email"]) + "&gt;</th></tr></thead>");
	print("<tbody>");
	print("<tr class=\"" + ("success" if login["paid"] else "error") + "\"><td>Bezahlt</td><td>" + html.bool_icon(login["paid"]))
	if login["paid"]:
		if login["ticket"] is not None and login["ticket"] != "" and login["ticket"] != "None":
			print("<span class=\"ticket\">Ticket: " + cgi.escape(login["ticket"]) + "</span>")
		print(" (<a href=\"#kontoinfo\" role=\"button\" data-toggle=\"modal\" title=\"Konto-Information erneut einblenden\">Konto-Info</a>)")
	else:
		print("&Uuml;berweise 42&euro; auf das Konto des <a href=\"#kontoinfo\" role=\"button\" data-toggle=\"modal\" title=\"Konto-Information einblenden\">C3PB e.V.</a>")
	print("</td></tr>")
	print("<tr class=\"" + ("success" if login["there"] else "error") + "\"><td>Anwesend</td><td>" + html.bool_icon(login["there"]) + "</td></tr>")
	print("</tbody></table>")
	print("</div></div>")

	print("<div class=\"row\">")

	print("<div class=\"span6\"><div class=\"well well-small\">")

	shirts = login["shirts"]
	def shirt_order_row(size):
		if size not in shirts:
			shirts[size] = []

		items = [ size ]

		if shirts[size].count(False) == 0 or not conf.get("shirt_order"):
			items.append("<a class=\"btn\"><i class=\"icon-minus-sign\"></i></a>")
		else:
			items.append("<a class=\"btn btn-danger\" href=\"?order=sub_R" + size + "\"><i class=\"icon-minus-sign\"></i></a>")
		items.append(str(shirts[size].count(False)))
		if conf.get("shirt_order"):
			items.append("<a class=\"btn btn-success\" href=\"?order=add_R" + size + "\"><i class=\"icon-plus-sign\"></i></a>")
		else:
			items.append("<a class=\"btn\"><i class=\"icon-plus-sign\"></i></a>")

		if shirts[size].count(True) == 0 or not conf.get("shirt_order"):
			items.append("<a class=\"btn\"><i class=\"icon-minus-sign\"></i></a>")
		else:
			items.append("<a class=\"btn btn-danger\" href=\"?order=sub_G" + size + "\"><i class=\"icon-minus-sign\"></i></a>")
		items.append(str(shirts[size].count(True)))
		if conf.get("shirt_order"):
			items.append("<a class=\"btn btn-success\" href=\"?order=add_G" + size + "\"><i class=\"icon-plus-sign\"></i></a>")
		else:
			items.append("<a class=\"btn\"><i class=\"icon-plus-sign\"></i></a>")

		return html.tb_row(items)

	print("<h2>Shirts</h2>")
	if not conf.get("shirt_order"):
		print("<div>Die Shirtbestellung ist abgeschlossen!</div>")
	print("<table class=\"table\">")
	print("<thead><tr><th>Gr&ouml;&szlig;e</th><th colspan=\"3\">Regular</th><th colspan=\"3\">Girlyshirts</th></tr></thead>")
	print("<tbody>")
	print(shirt_order_row("S"))
	print(shirt_order_row("M"))
	print(shirt_order_row("L"))
	print(shirt_order_row("XL"))
	print(shirt_order_row("XXL"))
	print(shirt_order_row("XXXL"))
	print(shirt_order_row("4XL"))
	print("</tbody></table>")
	if conf.get("shirt_order"):
		print("<form method=\"POST\">")
		print(html.f_hidden("order", "clear_all"))
		print(html.f_submit("Zur&uuml;cksetzen"))
		print("</form>")
	print("</div></div>")

	print("<div class=\"span6\"><div class=\"well well-small\">")
	print("<h2>Frystyck (pro Tag)</h2>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "update_lunch"))
	print("<table class=\"table\">")
	print("<thead><tr><th>Material</th><th>Menge</th></tr></thead>")
	print("<tbody>")
	print(html.tb_row(["Br&ouml;tchen", html.f_input("replaceme", "buns", value=login["lunch"]["buns"], size=10)]))
	print(html.tb_row(["Wurst", html.f_checkbox("food", "baloney", login["lunch"]["baloney"])]))
	print(html.tb_row(["K&auml;se", html.f_checkbox("food", "cheese", login["lunch"]["cheese"])]))
	print(html.tb_row(["Marmelade", html.f_checkbox("food", "jam", login["lunch"]["jam"])]))
	print(html.tb_row(["Cornflakes", html.f_checkbox("food", "cornflakes", login["lunch"]["cornflakes"])]))
	print("</tbody></table>")
	print(html.f_submit("Aktualisieren"))
	print("</form>")
	print("</div></div>")

	print("</div>")

	print("<div class=\"well well-small\">")
	print("<h2>Bemerkungen</h2>")
	print("<table class=\"table\">")
	print("<tbody>")
	print("<tr class=\"" + ("success" if login["note_done"] else "error") + "\">")
	print("<td>" + html.bool_icon(login["note_done"]) + "</td>")
	print("<td>" + ("Jemand" if login["note_done"] else "(Noch) Niemand") + " hat diese Bemerkung bearbeitet")
	print("</td></tr></tbody></table>")
	print(html.form_start(box=False))
	print(html.f_hidden("action", "update_note"))
	print(html.form_textarea("note", login["note"] if login["note"] is not None else "",
		placeholder="Bin allergisch auf Sauerstoff, Kohlenstoff und Stickstoff.\nHab ne Sonnenlichtunverträglichkeit."))
	print(html.f_submit("Speichern"))
	print(html.form_end(box=False))
	print("</div>")

	print("<div id=\"kontoinfo\" class=\"modal hide fade\" role=\"dialog\" aria-hidden=\"True\" aria-labelledby=\"kontoinfoDlgCaption\">")
	print(  "<div class=\"modal-header\">")
	print(    "<button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">×</button>")
	print(    "<h3 id=\"kontoinfoDlgCaption\">Kontoinformation</h3>")
	print(  "</div>")
	print(  "<div class=\"modal-body\">")
	print(    "<p>Bitte überweise die 42€ Teilnehmerbeitrag auf folgendes Konto. Im Preis enthalten sind eine Tasse sowie das erweiterte Frühstück.</p>")
	print(    "<table class=\"table\"><thead><tr><th colspan=\"2\">Konto-Daten</th></tr></thead><tbody>")
	print(      "<tr><td>Konto-Inhaber</td><td>C3PB e.V.</td></tr>")
	print(      "<tr><td>Konto-Nummer</td><td>8744126200</td></tr>")
	print(      "<tr><td>Bank</td><td>Volksbank Paderborn (BLZ 47260121)</td></tr>")
	print(      "<tr><td>Verwendungszweck</td><td>EasterHegg 2013 Teilnehmer \"" + login["name"] + "\"</td></tr>")
	print(    "</tbody></table>")
	print(  "</div>")
	print(  "<div class=\"modal-footer\"><button class=\"btn btn-primary\" data-dismiss=\"modal\" aria-hidden=\"true\">OK</button></div>")
	print("</div>")
