#!/usr/local/bin/python2.7

from __future__ import print_function

import os
import os.path
import cgi
import cgitb
import pickle

conf = {
		# "logdir": "/tmp",
		"title" : "EH13 - Ticketsystem",
		"users" : os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/users.pickle")
}

# Data to store
# - (Nick)name
# - Password
# - Number and size of shirts
# - Status of payment

class User(object):
	def __str__(self):
		return "&lt;nick=" + str(self.name) + "; admin=" + str(self.is_admin) + "&gt;"

	def __init__(self, name, password, shirts):
		self.is_admin = False
		self.name = name
		self.password = password # TODO
		self.shirts = shirts

def f_input(name, password=False):
	return "<input name=\"" + str(name) + "\" type=\"" + ("password" if password else "text") + "\"/>"

def f_hidden(name, value):
	return "<input type=\"hidden\" name=\"" + str(name) + "\" value=\"" + str(value) + "\"/>"

def f_submit():
	return "<input type=\"submit\"/>"

def tb_row(*fields):
	s = "<tr>"
	for f in fields:
		if f is None:
			s += "<td/>"
		else:
			s += "<td>" + str(f) + "</td>"
	return s + "</tr>"

def user_list():
	fh = None
	try:
		fh = open(conf["users"], "r")
	except:
		return []
	users = pickle.load(fh)
	fh.close()
	return users

def user_list_append(user):
	users = user_list()
	fh = open(conf["users"], "w")
	users.append(user)
	pickle.dump(users, fh)
	fh.close()

def user_list_find(name):
	users = user_list()
	for x in users:
		if x.name == name:
			return x
	return None

def user_new(formdata):
	if formdata is None:
		s  = "<p><form method=\"POST\" action=\"/\">\n<table>"
		s += tb_row("(Nick)name", f_input("user"))
		s += tb_row("Password", f_input("passwd", True))
		s += tb_row("Password (again)", f_input("passwd_again", True))
		s += tb_row(None, f_submit())
		s += "</table>"
		s += f_hidden("action", "create_user")
		s += "</form></p>"
		return s
	if "user" not in formdata:
		return ("(Nick)name missing!", False)
	if "passwd" not in formdata:
		return ("Password missing!", False)
	if "passwd_again" not in formdata:
		return ("Password not repeated!", False)
	if formdata["passwd"].value != formdata["passwd_again"].value:
		return ("Passwords do not match!", False)
	if user_list_find(formdata["user"].value) is not None:
		return ("A user with that name already exists!", False)
	u = User(formdata["user"].value, formdata["passwd"].value, [])
	user_list_append(u)
	return ("User created :) " + str(u), True)

if __name__ == "__main__":
	if "logdir" in conf:
		cgitb.enable(display=0, logdir=conf["logdir"])
	else:
		cgitb.enable()

	form = cgi.FieldStorage()

	print("<!DOCTYPE html>")
	print("<html><head><title>" + conf["title"] + "</title></head>")
	print("<h1>" + conf["title"] + "</h1>")

	if "action" not in form:
		print("<p><ul>")
		print("<li><a href=\"/?action=new_user\">Create new user</a></li>")
		print("</ul></p>")
	elif form["action"].value == "new_user":
		print(user_new(None))
	elif form["action"].value == "create_user":
		res = user_new(form)
		print("<p>" + str(res[0]) + "</p>")
		if res[1] != True:
			print(user_new(None))

	print("<p>")
	for k in form:
		print(str(k) + ": " + str(form[k].value) + "<br/>\n")
	print("</p>")

	print("</body></html>")
