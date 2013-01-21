import os
import sys

def post(cookies=None,update=None):
	msg = "Status: 302 See Other\r\n"
	if update == None:
		msg += "Location: /\r\n"
	else:
		msg += "Location: /?update=" + update + "\r\n"
	if cookies is not None:
		msg += str(cookies) + "\r\n"
	msg += "\r\n"
	sys.stdout.write(msg)
	sys.exit(0)
