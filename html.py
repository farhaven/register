import cgi

def f_input(name, value="", size=20, password=False):
	return "<input name=\"" + str(name) + \
		"\" type=\"" + ("password" if password else "text") + \
		"\" size=\"" + str(size) + \
		"\" value=\"" + str(value) + \
		"\"/>"

def f_checkbox(name, value, checked=False):
	s = "<input name=\"" + str(name) + "\" type=\"checkbox\" value=\"" + value + "\""
	if checked:
		s += " checked=\"checked\""
	return s + "/>"

def f_hidden(name, value):
	return "<input type=\"hidden\" name=\"" + cgi.escape(name) + "\" value=\"" + cgi.escape(value) + "\"/>"

def f_submit(value=None):
	s = "<input type=\"submit\""
	if value is not None:
		s += " value=\"" + value + "\""
	return s + "/>"

def tb_row(fields, head=False):
	word = "td"
	if head:
		word = "th"
	s = "<tr>"
	for f in fields:
		if f is None:
			s += "<" + word + "></" + word + ">"
		else:
			s += "<" + word + ">" + str(f) + "</" + word + ">"
	return s + "</tr>"

def form(*items):
	s  = "<form method=\"POST\">"
	for x in items:
		s += x
	s += "</form>"
	return s
