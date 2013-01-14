def f_input(name, password=False):
	return "<input name=\"" + str(name) + "\" type=\"" + ("password" if password else "text") + "\"/>"

def f_hidden(name, value):
	return "<input type=\"hidden\" name=\"" + cgi.escape(name) + "\" value=\"" + cgi.escape(value) + "\"/>"

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
