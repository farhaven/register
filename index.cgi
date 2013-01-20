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

def redirect_post(cookies=None,update=None):
	print("Status: 302 See Other")
	if cookies is not None:
		print(str(cookies))
	if update == None:
		print("Location: /")
	else
		print("Location: /?update=" + update)
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
			redirect_post(str(login.cookies))
	elif form.getfirst("action") == "update_lunch":
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT u_id FROM users WHERE name = %s", (login.name(), ))
			u_id = cursor.fetchone()[0]
			items = form.getlist("food")
			if cursor.execute("SELECT * FROM lunch WHERE u_id = %s", (u_id, )) == 0L:
				cursor.execute("INSERT INTO lunch (u_id, buns, baloney, cheese, jam, cornflakes) " +
									"VALUES (%s, %s, %s, %s, %s, %s)", (
						u_id,
						form.getfirst("buns", ""),
						"baloney" in items,
						"cheese" in items,
						"jam" in items,
						"cornflakes" in items
					))
			else:
				cursor.execute("UPDATE lunch SET " +
						"buns = %s, baloney = %s, cheese = %s, jam = %s, cornflakes = %s WHERE u_id = %s",
					(
						form.getfirst("buns", ""),
						"baloney" in items,
						"cheese" in items,
						"jam" in items,
						"cornflakes" in items,
						u_id
					))
			conn.commit()
		except Exception as err:
			print("Status: 200 OK")
			print("Content-Type: text/plain\r\n\r\n")
			print(str(err))
			sys.exit(0)
		redirect_post()
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
		redirect_post(update="shirts")

	print("Status: 200 OK")
	print("Content-Type: text/html; charset=utf-8")
	print(login.cookies)
	print()

	print("<!DOCTYPE html>")
	print("<head>")
	print("<link rel=\"stylesheet\" type=\"text/css\" href=\"/css/bootstrap.min.css\">")
	print("<link rel=\"stylesheet\" type=\"text/css\" href=\"/css/eh13.css\">")
	print("<title>")
	print("EH13")
	print("</title></head>")
	print("<body>\n")

	is_admin = "REDIRECT_URL" in os.environ and os.environ["REDIRECT_URL"].startswith("/admin")
	print(menu.header(login, form.getfirst("action") if not is_admin else "ADMIN"))

	update = form.getfirst("update", "")
	if update != "":
		print("<div class=\"alert alert-info\">Your shirt order has been updated.</div>")

	if is_admin:
		menu.admin(conf, conn)
	elif form.getfirst("action", "logout") == "logout":
		menu.main(login)
	elif form.getfirst("action") == "add_user":
		usermgmt.addUser(form, conn)
	elif form.getfirst("action") == "login":
		if not login.valid():
			print("<div class=\"alert alert-error\">Login failed!</div>")
	else:
		print("<div class=\"alert alert-warning\">Unknown action: " + cgi.escape(form.getfirst("action", "")) + "</div>")

	print(menu.footer())

        print("<script language=\"javascript\" src=\"/js/bootstrap.min.js\"></script>")
	print("</body></html>")
