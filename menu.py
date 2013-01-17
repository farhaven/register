from __future__ import print_function

import os
import cgi
import html
import urllib

def header():
	s  = "<div class=\"header\">"
	s += "<a href=\"/\">EH13</a>"
	s += " <a href=\"/admin\">Admin</a>"
	s += "</div>"
	return s + "<hr>"

def admin(conf, conn):
	form = cgi.FieldStorage()
	cursor = conn.cursor()

	if form.getfirst("action") == "delete":
		cursor.execute("DELETE FROM users WHERE name = %s", (form.getfirst("user", ""), ))
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
	cursor.execute("SELECT name, paid, there FROM users");
	for x in cursor.fetchall():
		user = {
				"name": x[0],
				"has_paid": bool(x[1]),
				"is_there": bool(x[2])
		}
		tbl_del = "<a href=\"?action=delete&user=" + urllib.quote(user["name"]) + "\">Delete</a>"
		tbl_paid = "<a href=\"?action=setpaid&user=" + urllib.quote(user["name"]) + "&value="
		if user["has_paid"]:
			tbl_paid += "no\">has paid</a>"
		else:
			tbl_paid += "yes\">has not paid</a>"
		tbl_there = "<a href=\"?action=setthere&user=" + urllib.quote(user["name"]) + "&value="
		if user["is_there"]:
			tbl_there += "no\">is there</a>"
		else:
			tbl_there += "yes\">is not there</a>"
		print(html.tb_row(user["name"], tbl_del, tbl_paid, tbl_there))
	print("</table></div>")

	# debug foo, can be removed once we are "stable"
	print("<h1>Environment</h1>")
	print("<div><pre>")
	for x in os.environ:
		print(x + "=" + cgi.escape(os.environ[x]))
	print("</pre></div>")
	print("<h1>Form data</h1>")
	print("<div><pre>")
	for x in form.keys():
		print(x + "=" + form[x].value)
	print("</pre></div>")

def main(login):
	print("<h1>EH13 Registration</h1>")
	# new user
	if not login.valid():
		print("<div><h2>Log in</h2>")
		print("<form method=\"POST\">")
		print(html.f_hidden("action", "login"))
		print("<table>")
		print(html.tb_row("Name", html.f_input("username")))
		print(html.tb_row("Password", html.f_input("password", True)))
		print(html.tb_row(None, html.f_submit()))
		print("</table>")
		print("</form></div>")

		print("<div><h2>New user</h2>")
		print("<form method=\"POST\">")
		print(html.f_hidden("action", "add_user"))
		print("<table>")
		print(html.tb_row("Name", html.f_input("username")))
		print(html.tb_row("Mail", html.f_input("email")))
		print(html.tb_row("Password", html.f_input("password", True)))
		print(html.tb_row("Password (again)", html.f_input("password_again", True)))
		print(html.tb_row(None, html.f_submit()))
		print("</table>")
		print("</form></div>")
		return

	user = login.as_dict()

	print("<div><h2>User status for " + user["name"] + "</h2>")
	print("<table>")
	print(html.tb_row("Payment received", ("Yes" if user["has_paid"] else "No")))
	print(html.tb_row("Is there", ("Yes" if user["is_there"] else "No")))
	print(html.tb_row("Email", user["email"]))
	print(html.tb_row("Shirts", str(user["shirts"])))
	print("</table>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "logout"))
	print(html.f_submit("Log out"))
	print("</form>")
	print("</div>")

	def order_row(size):
		items = [ size ]
		if size in user["shirts"]:
			items.append("<a href=\"?order=sub_" + size + "\">-</a>")
		else:
			items.append("-")
		items.append("<a href=\"?order=add_" + size + "\">+</a>")
		return html.tb_row(*items)

	print("<div><h2>Order shirts</h2>")
	print("<form method=\"POST\">")
	print(html.f_hidden("order", "clear_all"))
	print(html.f_submit("Clear order"))
	print("</form>")
	print("<table>")
	print(order_row("S"))
	print(order_row("M"))
	print(order_row("L"))
	print(order_row("XL"))
	print(order_row("XXL"))
	print("</table>")
	print("</div>")
