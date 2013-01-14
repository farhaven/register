#!/usr/local/bin/python2.7

from __future__ import print_function

import cgi
import cgitb

conf = {
		"logdir": "/tmp",
		"title" : "EH13 - Ticketsystem"
}

# Data to store
# - (Nick)name
# - Password
# - Number and size of shirts
# - Status of payment

if __name__ == "__main__":
	cgitb.enable(display=0, logdir=conf["logdir"])
	form = cgi.FieldStorage()
	print("<!DOCTYPE html>")
	print("<html><head><title>" + conf["title"] + "</title></head>")
	print("<h1>" + conf["title"] + "</h1>")
	print("<p>Wheee</p>")
	print("</body></html>")
