#!/usr/local/bin/python2.7

from __future__ import print_function

import os
import os.path
import cgi
import cgitb
import Cookie
import sys

import user
import html

cgitb.enable(logdir="/tmp")

class Config(object):
	def __init__(self, values):
		self.values = values

	def get(self, name):
		if name not in self.values:
			return None
		return self.values[name]

conf = Config({
	"title": "EH13",
	"users": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "users.pickle")
})

def header(code):
	s = "HTTP/1.0 " + str(code) + " "
	if code == 200:
		s += "OK"
	elif code == 302:
		s += "See Other"
	elif code == 100:
		s += "Continue"
	return s

if __name__ == "__main__":
	form = cgi.FieldStorage()
	cookies = Cookie.SimpleCookie()
	if "HTTP_COOKIE" in os.environ:
		cookies = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	users = user.UserList(conf.get("users"))
	login = user.Login(cookies, users, form)

	if form.getfirst("action") == "logout":
		login.clear()
	print(header(200))
	print("Content-Type: text/html; charset=utf8")
	print(login.cookies)
	print()

	print("<!DOCTYPE html>")
	print("<html><head><title>" + cgi.escape(conf.get("title")) + "</title></head>")
	print("<body>")

	if not login.valid():
		if "username" in form or "password" in form:
			print("<p>Login failed!</p>")
		print("<p><form method=\"POST\" action=\"/\"><table>")
		print(html.tb_row("User", html.f_input("username")))
		print(html.tb_row("Pass", html.f_input("password", True)))
		if "action" not in form:
			print(html.tb_row(None, html.f_submit()))
			print("</table>")
			print("</form></p>")
			print("<p><a href=\"?action=new_user\">New user</a></p>")
		elif form.getfirst("action") == "new_user":
			print(html.tb_row("Pass (again)", html.f_input("password_again", True)))
			print(html.tb_row(None, html.f_submit()))
			print("</table>")
			print(html.f_hidden("action", "new_user_2"))
			print("</form></p>")
		elif form.getfirst("action") == "new_user_2":
			name = form.getfirst("username")
			passwd = form.getfirst("password", "")
			if name is None or (passwd != form.getfirst("password")):
				print("<p>Something was amiss!</p>")
			else:
				u = user.User(name, passwd, [])
				users.append(u)
	else:
		print("<p>Hello " + login.name() + "!</p>")
		print("<p><a href=\"?action=logout\">Log out</a></p>")

	print("<p><h1>Form data</h1><pre>")
	for x in form:
		print(cgi.escape(x) + "=" + cgi.escape(form[x].value))
	print("</pre></p>")

	print("<p><h1>Env</h1><pre>")
	for x in os.environ:
		print(x + "=" + os.environ[x])
	print("</pre></p>")

	print("<p><h1>Cookies</h1><pre>")
	print(login.cookies)
	print("</pre></p>")

	print("<p><h1>Misc test data</h1><pre>")
	print("Login: " + ("valid" if login.valid() else "invalid"))
	print(str(os.environ["REQUEST_METHOD"]))
	print(str(os.environ["SERVER_PORT"]))
	print("</pre></p>")

	print("</body></html>")
