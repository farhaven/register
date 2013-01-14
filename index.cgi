#!/usr/local/bin/python2.7

from __future__ import print_function

import cgi
import cgitb

conf = {
		# "logdir": "/tmp",
		"title" : "EH13 - Ticketsystem"
}

# Data to store
# - (Nick)name
# - Password
# - Number and size of shirts
# - Status of payment

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

def user_new():
	s  = "<p>"
	s += "<form method=\"POST\" action=\"/\">\n<table>"
	s += tb_row("(Nick)name", f_input("user"))
	s += tb_row("Password", f_input("passwd", True))
	s += tb_row("Password (again)", f_input("passwd_again", True))
	s += tb_row(None, f_submit())
	s += "</table>"
	s += f_hidden("debug", "yes" if flags["debug"] else "no")
	s += "</form></p>"
	return s

if __name__ == "__main__":
	if "logdir" in conf:
		cgitb.enable(display=0, logdir=conf["logdir"])
	else:
		cgitb.enable()

	form = cgi.FieldStorage()
	flags = dict()
	if "debug" in form and form["debug"].value == "yes":
		flags["debug"] = True
	else:
		flags["debug"] = False

	print("<!DOCTYPE html>")
	print("<html><head><title>" + conf["title"] + "</title></head>")
	print("<h1>" + conf["title"] + "</h1>")

	print(user_new())

	if flags["debug"]:
		print("<p>")
		for k in form:
			print(str(k) + ": " + str(form[k].value) + "<br/>\n")
		print("</p>")

	print("</body></html>")
