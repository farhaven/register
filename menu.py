from __future__ import print_function

import os
import os.path
import cgi
import html
import urllib

def header():
	s  = "<div class=\"navbar navbar-inverse navbar-fixed-top\">"
	s +=   "<div class=\"navbar-inner\"><div class=\"container\">"
	s +=     "<a class=\"btn btn-navbar\" data-toggle=\"collapse\" data-target=\".nav-collapse\">"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=       "<span class=\"icon-bar\"></span>"
	s +=     "</a>"
	s +=     "<a class=\"brand\" href=\"#\">EasterHegg 2013</a>"
	s +=     "<div class=\"nav-collapse collapse\">"
        s +=       "<ul class=\"nav\">"
        s +=         "<li class=\"active\"><a href=\"#\">Home</a></li>"
        s +=         "<li><a href=\"#about\">About</a></li>"
        s +=         "<li><a href=\"#contact\">Contact</a></li>"
        s +=       "</ul>"
        s +=     "</div>"
        s +=   "</div></div>"
        s += "</div>"
 
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

	print("<h1>Users</h1>")
	print("<div><table>")
	print(html.tb_row(["Name", "eMail", "Delete", "Paid", "Is there", "Shirts"], head=True))
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
			tbl_paid += "no\">yes</a>"
		else:
			tbl_paid += "yes\">no</a>"
		tbl_there = "<a href=\"?action=setthere&user=" + urllib.quote(user["name"]) + "&value="
		if user["is_there"]:
			tbl_there += "no\">yes</a>"
		else:
			tbl_there += "yes\">no</a>"
		print(html.tb_row([user["name"], user["email"], tbl_del, tbl_paid, tbl_there, user["shirts"]]))
	print("</table></div>")

	print("<h1>Lunch orders</h1>")
	print("<div><table>")
	print(html.tb_row(["Buns", "Baloney", "Cheese", "Jam", "Cornflakes"], head=True))
	cursor.execute("SELECT sum(buns), sum(baloney), sum(cheese), sum(jam), sum(cornflakes) FROM lunch");
	print(html.tb_row(cursor.fetchone()))
	print("</table></div>")

	print("<h1>Admins</h1>")
	print("<div><ul>")
	try:
		fh = open("../passwd", "r")
		for l in fh.readlines():
			print("<li>" + cgi.escape(l.split(":")[0]) + "</li>")
		fh.close()
	except:
		pass
	print("</ul></div>")

	print("<div><h1>Misc info</h1>")
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

def main(login):
	print("<h1>EH13 Registration</h1>")
	# new user
	if not login.valid():
		print("<div><h2>Log in</h2>")
		print("<form method=\"POST\" class=\"form-horizontal\">")
		print(html.f_hidden("action", "login"))
		print(html.form_input("login_name", "Name", "username"))
		print(html.form_password("login_pass", "Password", "password"))
		print(html.form_submit())
		print("</form></div>")

		print("<div><h2>New user</h2>")
		print("<form method=\"POST\" class=\"form-horizontal\">")
		print(html.f_hidden("action", "add_user"))
		print(html.form_input("new_name", "Name", "username"))
		print(html.form_input("new_mail", "E-Mail", "email"))
		print(html.form_password("new_pass", "Password", "password"))
		print(html.form_password("new_pass2", "Password (again)", "password_again"))
		print(html.form_submit())
		print("</form></div>")
		return

	user = login.as_dict()

	print("<div><h2>User status for " + user["name"] + "</h2>")
	print("<table>")
	print(html.tb_row(["Payment received", ("Yes" if user["has_paid"] else "No")]))
	print(html.tb_row(["Is there", ("Yes" if user["is_there"] else "No")]))
	print(html.tb_row(["Email", user["email"]]))
	print("</table>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "logout"))
	print(html.f_submit("Log out"))
	print("</form>")
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

	print("<div><h2>Shirt order</h2>")
	print("<table>")
	print(shirt_order_row("S"))
	print(shirt_order_row("M"))
	print(shirt_order_row("L"))
	print(shirt_order_row("XL"))
	print(shirt_order_row("XXL"))
	print("</table>")
	print("<form method=\"POST\">")
	print(html.f_hidden("order", "clear_all"))
	print(html.f_submit("Clear order"))
	print("</form>")
	print("</div>")

	print("<div><h2>Lunch order (per day)</h2>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "update_lunch"))
	print("<table>")
	print(html.tb_row(["Buns", html.f_input("buns", value=user["lunch"]["buns"], size=10)]))
	print(html.tb_row(["Baloney", html.f_checkbox("food", "baloney", user["lunch"]["baloney"])]))
	print(html.tb_row(["Cheese", html.f_checkbox("food", "cheese", user["lunch"]["cheese"])]))
	print(html.tb_row(["Jam", html.f_checkbox("food", "jam", user["lunch"]["jam"])]))
	print(html.tb_row(["Cornflakes", html.f_checkbox("food", "cornflakes", user["lunch"]["cornflakes"])]))
	print("</table>")
	print(html.f_submit("Update"))
	print("</form>")
	print("</div>")
