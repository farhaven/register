#!/usr/bin/python

from __future__ import print_function

import cgitb; cgitb.enable()
import cgi
import Cookie

import os
import os.path
import sys

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
	"users": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "users.pickle")
	})

if __name__ == "__main__":
	redirect_https()

	form = cgi.FieldStorage()

	print("Content-Type: text/html; encoding=utf-8")
	print()

	print("<!DOCTYPE html>")
	print("<head><title>")
	print("EH13")
	print("</title></head>")
	print("<body>")

	if "REDIRECT_URL" in os.environ and os.environ["REDIRECT_URL"].startswith("/admin"):
		menu.admin(conf)
	elif "action" not in form:
		menu.main()
	elif form.getfirst("action") == "add_user":
		usermgmt.addUser(form, conf)

	print("</body></html>")
