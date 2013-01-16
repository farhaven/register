from __future__ import print_function

import os
import cgi
import html
import userlist
import urllib

def header():
	s  = "<div class=\"header\">"
	s += "<a href=\"/\">EH13</a>"
	s += " <a href=\"/admin\">Admin</a>"
	s += "</div>"
	return s + "<hr>"

def admin(conf):
	users = userlist.UserList(conf)
	form = cgi.FieldStorage()

	if form.getfirst("action") == "delete":
		u = users.find(form.getfirst("user", ""))
		if u is not None:
			users.remove(u)
	elif form.getfirst("action") == "setpaid":
		u = users.find(form.getfirst("user", ""))
		if u is not None:
			users.remove(u)
			u.has_paid = True
			users.append(u)

	print("<h1>Users</h1>")
	print("<div><table>")
	for x in users.as_list():
		tbl_del = "<a href=\"?action=delete&user=" + urllib.quote(x.name) + "\">Delete</a>"
		tbl_paid = "Paid"
		if not x.has_paid:
			tbl_paid = "<a href=\"?action=setpaid&user=" + urllib.quote(x.name) + "\">Set as paid</a>"
		print(html.tb_row(x.name, tbl_del, tbl_paid))
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

def main(login, conf):
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

	users = userlist.UserList(conf)
	user = users.find(login.name())

	print("<div>User status for " + user.name)
	print("<table>")
	print(html.tb_row("Paid", ("Yes" if user.has_paid else "No")))
	print(html.tb_row("Email", user.email))
	print(html.tb_row("Shirts", str(user.shirts)))
	print("</table>")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "logout"))
	print(html.f_submit("Log out"))
	print("</form>")
	print("</div>")
