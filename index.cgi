#!/usr/bin/python

from __future__ import print_function

import cgitb; cgitb.enable()
import cgi
import Cookie
import os
import os.path
import sys
import json

import db
import menu
import usermgmt

class Config(object):
	def __init__(self):
		fh = None
		if os.path.exists("settings.json"):
			fh = open("settings.json")
		else:
			fh = open("settings.default.json")
		self.dict = json.load(fh)
		fh.close()

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

if __name__ == "__main__":
	conf = Config()
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
	elif form.getfirst("order") is not None:
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT u_id FROM users WHERE name = %s", (login.name()))
			u_id = cursor.fetchone()[0]
			order = form.getfirst("order")
			(op, size) = order.split("_", 2)
			if op == "sub":
				cursor.execute("DELETE FROM shirts WHERE (u_id = %s AND size = %s) LIMIT 1", (int(u_id), size))
			elif op == "add":
				cursor.execute("INSERT INTO shirts (u_id, size) VALUES (%s, %s)", (int(u_id), size))
			elif op == "clear":
				cursor.execute("DELETE FROM shirts WHERE u_id = %s", (int(u_id), ))
			conn.commit()
		except:
			pass
		print("Status: 302 See Other")
		print("Location: /")
		print()
		sys.exit(0)

	print("Status: 200 OK")
	print("Content-Type: text/html; charset=utf-8")
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
		menu.main(login)
	elif form.getfirst("action") == "add_user":
		usermgmt.addUser(form, conn)
	elif form.getfirst("action") == "login":
		if not login.valid():
			print("<h1>Login failed!</h1>")
	else:
		print("<pre>Unknown action: " + cgi.escape(form.getfirst("action", "")) + "</pre>")

	print("</body></html>")
