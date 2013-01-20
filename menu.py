from __future__ import print_function

import os
import os.path
import cgi
import html
import urllib

def header(login, active="home"):
	s  = "<div class=\"navbar navbar-inverse navbar-fixed-top\">"
	s +=   "<div class=\"navbar-inner\"><div class=\"container\">"
	s +=     "<a class=\"btn btn-navbar\" data-toggle=\"collapse\" data-target=\".nav-collapse\">"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=     "</a>"
	s +=     "<a class=\"brand\" href=\"/\">EasterHegg 2013</a>"
	s +=     "<div class=\"nav-collapse collapse\">"
	s +=       "<ul class=\"nav\">"
	s +=         "<li class=\"\"><a href=\"http://eh13.c3pb.de/\" target=\"_blank\">Webseite</a></li>"
	if (active != "ADMIN"):
		if (login.valid()):
			s += "<li class=\"" 
			s += "active" if active == "home" else ""
			s += "\"><a href=\"#\">Home</a></li>"

			#s += "<li><a href=\"#about\">About</a></li>"
			#s += "<li><a href=\"#contact\">Contact</a></li>"

			s += "<li class=\""
			s += "active" if active == "logout" else ""
			s += "\"><a href=\"/?action=logout\">Logout</a></li>"
		else:
			s += "<li class=\"active\"><a href=\"#\">Login</a></li>"
		s += "<li class=\"\"><a href=\"/admin\">Admin</a></li>"
	else:
		s += "<li class=\"\"><a href=\"/\">User-Mode</a></li>"
		s += "<li class=\"active\"><a href=\"/admin\">Admin</a></li>"
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
	elif form.getfirst("action") == "setpaid":
		val = True if form.getfirst("value") == "yes" else False
		cursor.execute("UPDATE users SET paid = %s WHERE name = %s", (val, form.getfirst("user", "")))
		conn.commit()

	cursor.execute("SELECT count(*), sum(paid), sum(there) FROM users")
	print("<h1>%d Benutzer (%d haben bezahlt, %d sind da)</h1>" % cursor.fetchone())
	print("<div><table>")
	print(html.tb_row(["Name", "eMail", "L&ouml;schen", "Hat bezahlt", "Ist da", "Shirts"], head=True))
	cursor.execute("SELECT u_id, name, email, paid, there FROM users");
	for x in cursor.fetchall():
		user = {
				"name": x[1],
				"email": x[2],
				"has_paid": bool(x[3]),
				"is_there": bool(x[4]),
				"shirts": []
		}
		cursor.execute("SELECT size FROM shirts WHERE u_id = %s", (x[0], ))
		for s in cursor.fetchall():
			user["shirts"].append(s[0])
		tbl_del = "<a href=\"?action=delete&user=" + urllib.quote(user["name"]) + "\">Delete</a>"
		tbl_paid = "<a href=\"?action=setpaid&user=" + urllib.quote(user["name"]) + "&value="
		if user["has_paid"]:
			tbl_paid += "no\">ja</a>"
		else:
			tbl_paid += "yes\">nein</a>"
		tbl_there = "<a href=\"?action=setthere&user=" + urllib.quote(user["name"]) + "&value="
		if user["is_there"]:
			tbl_there += "no\">ja</a>"
		else:
			tbl_there += "yes\">nein</a>"
		print(html.tb_row([user["name"], user["email"], tbl_del, tbl_paid, tbl_there, user["shirts"]]))
	print("</table></div>")

	print("<h1>Frystyck</h1>")
	print("<div><table>")
	print(html.tb_row(["Br&ouml;tchen", "Wurscht", "K&auml;se", "Marmelade", "Cornflakes"], head=True))
	cursor.execute("SELECT sum(buns), sum(baloney), sum(cheese), sum(jam), sum(cornflakes) FROM lunch")
	print(html.tb_row(cursor.fetchone()))
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
	print("<h1>EH13 Registration</h1>")
	# new user
	if not login.valid():
		print("<div class=\"well\"><h2>Log in</h2>")
		print(html.form_start(box=False))
		print(html.f_hidden("action", "login"))
		print(html.form_input("login_name", "Name", "username"))
		print(html.form_password("login_pass", "Password", "password"))
		print(html.form_submit())
		print(html.form_end(box=False))
		print("</div>")

		c = conn.cursor()
		c.execute("SELECT count(*) FROM users")
		if c.fetchone()[0] < conf.get("maxusers"):
			print("<div class=\"well\"><h2>Neuer Benutzer</h2>")
			print(html.form_start(box=False))
			print(html.f_hidden("action", "add_user"))
			print(html.form_input("new_name", "Name", "username"))
			print(html.form_input("new_mail", "E-Mail", "email", icon="envelope"))
			print(html.form_password("new_pass", "Passwort", "password"))
			print(html.form_password("new_pass2", "Passwort (nochmal)", "password_again"))
			print(html.form_submit())
			print(html.form_end(box=False))
			print("</div>")
		else:
			print("<div><h2>Registrierung geschlossen</h2>")
			print("Die Registrierung ist geschlossen. Es sind schon " + str(conf.get("maxusers")) + " Wesen registriert. Sorry :(")
			print("</div>")
		return

	user = login.as_dict()

	print("<div><h2>Status f&uuml;r " + cgi.escape(user["name"]) + "</h2>")
	print("<table>")
	print(html.tb_row(["Bezahlt", ("Yes" if user["has_paid"] else "No")]))
	print(html.tb_row(["Anwesend", ("Yes" if user["is_there"] else "No")]))
	print(html.tb_row(["Email", user["email"]]))
	print("</table>")
	print("</div>")

	def shirt_order_row(size):
		items = [ size ]
		if size in user["shirts"]:
			items.append("<a href=\"?order=sub_" + size + "\">-</a>")
		else:
			items.append("-")
		items.append(user["shirts"].count(size))
		items.append("<a href=\"?order=add_" + size + "\">+</a>")
		return html.tb_row(items)

	print("<div><h2>Shirts</h2>")
	print("<table>")
	print(shirt_order_row("S"))
	print(shirt_order_row("M"))
	print(shirt_order_row("L"))
	print(shirt_order_row("XL"))
	print(shirt_order_row("XXL"))
	print("</table>")
	print("<form method=\"POST\">")
	print(html.f_hidden("order", "clear_all"))
	print(html.f_submit("Zur&uuml;cksetzen"))
	print("</form>")
	print("</div>")

	print("<div><h2>Frystyck (pro Tag)</h2>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "update_lunch"))
	print("<table>")
	print(html.tb_row(["Br&ouml;tchen", html.f_input("replaceme", "buns", value=user["lunch"]["buns"], size=10)]))
	print(html.tb_row(["Wurst", html.f_checkbox("food", "baloney", user["lunch"]["baloney"])]))
	print(html.tb_row(["K&auml;se", html.f_checkbox("food", "cheese", user["lunch"]["cheese"])]))
	print(html.tb_row(["Marmelade", html.f_checkbox("food", "jam", user["lunch"]["jam"])]))
	print(html.tb_row(["Cornflakes", html.f_checkbox("food", "cornflakes", user["lunch"]["cornflakes"])]))
	print("</table>")
	print(html.f_submit("Aktualisieren"))
	print("</form>")
	print("</div>")
