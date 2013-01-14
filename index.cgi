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

	if os.environ["REQUEST_METHOD"] == "POST":
		print(header(302))
		print(login.cookies)
		if os.environ["SERVER_PORT"] == "80":
			print("Location: http://" + os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"])
		else:
			print("Location: https://" + os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"])
		print()
		sys.exit(0)

	print(header(200))
	print("Content-Type: text/html; charset=utf8")
	print(login.cookies)
	print()

	print("<!DOCTYPE html>")
	print("<html><head><title>" + cgi.escape(conf.get("title")) + "</title></head>")
	print("<body>")

	if not login.valid():
		print("<p><form method=\"POST\" action=\"/\"><table>")
		print(html.tb_row("User", html.f_input("username")))
		print(html.tb_row("Pass", html.f_input("password", True)))
		print(html.tb_row(None, html.f_submit()))
		print("</table>")
		print("</form></p>")
	else:
		print("Hello " + login.name())

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
	print("Users:")
	for x in users.as_list():
		print(cgi.escape(str(x)))
	print(str(os.environ["REQUEST_METHOD"]))
	print(str(os.environ["SERVER_PORT"]))
	print("</pre></p>")

	print("</body></html>")
