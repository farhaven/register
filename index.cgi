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
import redirect

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

if __name__ == "__main__":
	conf = Config()
	conn = db.init(conf)
	errors = None

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
			redirect.post(str(login.cookies))
	elif form.getfirst("action") == "update_note":
		note = cgi.escape(form.getfirst("note", ""))
		c = conn.cursor()
		c.execute("UPDATE users SET note = %s WHERE u_id = %s", (note, login["u_id"]))
		c.execute("UPDATE users SET note_done = False WHERE u_id = %s", (login["u_id"], ))
		conn.commit()
		redirect.post(update="note")
	elif form.getfirst("action") == "update_lunch":
		cursor = conn.cursor()
		try:
			items = form.getlist("food")
			if cursor.execute("SELECT * FROM lunch WHERE u_id = %s", (login["u_id"], )) == 0L:
				cursor.execute("INSERT INTO lunch (u_id, buns, baloney, cheese, jam, cornflakes) " +
									"VALUES (%s, %s, %s, %s, %s, %s)", (
						login["u_id"],
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
						login["u_id"]
					))
			conn.commit()
		except Exception as err:
			print("Status: 200 OK")
			print("Content-Type: text/plain\r\n\r\n")
			print(str(err))
			sys.exit(0)
		redirect.post(update="lunch")
	elif form.getfirst("action") == "add_user":
		errors = usermgmt.addUser(form, conf, conn)
		if errors is None:
			redirect.post(update="newuser")
	elif form.getfirst("order") is not None and conf.get("shirt_config"):
		cursor = conn.cursor()
		try:
			order = form.getfirst("order")
			(op, size) = order.split("_", 2)
			girlyshirt = size[0] == "G"
			size = size[1:]
			if op == "sub":
				cursor.execute("DELETE FROM shirts WHERE (u_id = %s AND size = %s AND girly = %s) LIMIT 1", (login["u_id"], size, girlyshirt))
			elif op == "add":
				cursor.execute("INSERT INTO shirts (u_id, size, girly) VALUES (%s, %s, %s)", (login["u_id"], size, girlyshirt))
			elif op == "clear":
				cursor.execute("DELETE FROM shirts WHERE u_id = %s", (login["u_id"], ))
			conn.commit()
		except:
			pass
		redirect.post(update="shirts")

	print("Status: 200 OK")

	if 'REDIRECT_URL' in os.environ and os.environ['REDIRECT_URL'].startswith("/info"):
		print("Content-Type: application/json")
		print()
		cursor = conn.cursor()
		cursor.execute("SELECT count(*), COALESCE(sum(there), 0) FROM users")
		(total, present) = cursor.fetchone()
		status = {
				"total": int(total),
				"present": int(present)
		}
		print(json.dumps(status, indent=4))
		sys.exit(0)

	print("Content-Type: text/html; charset=utf-8")
	print(login.cookies)
	print()

	custom_script = ""
	print("<!DOCTYPE html>")
	print("<html>")
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
	update_message = ""

	if update == "shirts":
		update_message = "Your shirt order has been updated."
	elif update == "lunch":
		update_message = "Your lunch order has been updated."
	elif update == "newuser":
		update_message = "User account created successfully :-)"
	elif update == "note":
		update_message = "Your note has been updated."

	if update_message != "":
		print("<div id=\"update-alert\" class=\"alert alert-info\">" + update_message + "</div>")
		custom_script += "window.setTimeout(function() { $(\"div#update-alert\").fadeTo(500, 0).slideUp(500, function(){ $(this).remove(); }); }, 5000);";

	if errors is not None:
		print("<div class=\"alert alert-error\">")
		print(str(errors))
		print("</div>")
	elif is_admin:
		menu.admin(conf, conn)
	elif form.getfirst("action") == "changepass":
		login.changePass(form, conn)
	elif form.getfirst("action", "logout") == "logout":
		menu.main(login, conf, conn)
	elif form.getfirst("action") == "login":
		if not login.valid():
			print("<div class=\"alert alert-error\">Login failed!</div>")
	else:
		print("<div class=\"alert alert-warning\">Unknown action: " + cgi.escape(form.getfirst("action", "")) + "</div>")

	print(menu.footer())

	print("<script language=\"javascript\" src=\"/js/jquery.min.js\"></script>")
        print("<script language=\"javascript\" src=\"/js/bootstrap.min.js\"></script>")
	if custom_script != "":
		print ("<script language=\"javascript\"><!-- \n$().ready(function() { " + custom_script + " });\n// --></script>");
	print("</body></html>")
