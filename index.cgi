#!/usr/bin/python

from __future__ import print_function

import cgitb; cgitb.enable()
import cgi
import Cookie
import os
import os.path
import sys

import db
import menu
import usermgmt

class Config(object):
	def __init__(self, d):
		self.dict = d

	def get(self, n):
		if n in self.dict:
			return self.dict[n]
		return None

def redirect_https():
	if "HTTPS" not in os.environ:
		print("Status: 302 See Other")
		print("Location: https://" + os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"])
		print()
		sys.exit(0)

conf = Config({
	"db_user": "register",
	"db_pass": "Ohy9chohvoo1epee"
})

if __name__ == "__main__":
	redirect_https()
	conn = db.init(conf)

	if "REQUEST_URI" in os.environ:
		q = os.environ["REQUEST_URI"].split('?', 2)
		if len(q) == 2:
			os.environ["QUERY_STRING"] = q[1]
	form = cgi.FieldStorage()
	cookies = Cookie.SimpleCookie()
	if "HTTP_COOKIE" in os.environ:
		cookies = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	login = usermgmt.Login(cookies, conn, form)

	if form.getfirst("action") == "logout":
		login.clear()
	elif form.getfirst("action") == "login":
		if login.validate(form):
			print("Status: 302 See Other")
			print(login.cookies)
			print("Location: /")
			print()
			sys.exit(0)

	print("Status: 200 OK")
	print("Content-Type: text/html; encoding=utf-8")
	print(login.cookies)
	print()

	print("<!DOCTYPE html>")
	print("<head>")
	# print("<style type=\"text/css\" src=\"/style.css\"/>")
	print("<link rel=\"stylesheet\" type=\"text/css\" href=\"/style.css\">")
	print("<title>")
	print("EH13")
	print("</title></head>")
	print("<body>")

	print(menu.header())
	if "REDIRECT_URL" in os.environ and os.environ["REDIRECT_URL"].startswith("/admin"):
		menu.admin(conf, conn)
	elif form.getfirst("action", "logout") == "logout":
		menu.main(login, conf)
	elif form.getfirst("action") == "add_user":
		usermgmt.addUser(form, conn)
	elif form.getfirst("action") == "login":
		if not login.valid():
			print("<h1>Login failed!</h1>")
	else:
		print("<pre>Unknown action: " + cgi.escape(form.getfirst("action", "")) + "</pre>")

	print("</body></html>")
