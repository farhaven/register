import os
import cgi
import html
import userlist

def header():
	s  = "<div class=\"header\">"
	s += "<a href=\"/\">EH13</a>"
	s += " <a href=\"/admin\">Admin interface</a>"
	s += "</div>"
	return s + "<hr>"

def admin(conf):
	print(header())

	print("<h1>Users</h1>")
	users = userlist.UserList(conf.get("users"))
	print("<div><ul>")
	for x in users.as_list():
		print("<li>" + str(x) + "</li>")
	print("</ul></div>")

	print("<h1>Debug</h1>")
	print("<div><pre>")
	for x in os.environ:
		print(x + "=" + cgi.escape(os.environ[x]))
	print("</pre></div>")

def main():
	print(header())

	print("<h1>EH13</h1>")
	# new user
	print("<div>New user")
	print("<form method=\"POST\">")
	print(html.f_hidden("action", "add_user"))
	print("<table>")
	print(html.tb_row("Name", html.f_input("username")))
	print(html.tb_row("Mail", html.f_input("email")))
	print(html.tb_row("Password", html.f_input("password", True)))
	print(html.tb_row("Password (again)", html.f_input("password_again", True)))
	print(html.tb_row(None, html.f_submit()))
	print("</form>")
	print("</table></div>")
