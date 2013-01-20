import cgi

def f_input(id, name, value="", size=None, password=False):
	s  = "<input id=\"" + str(id) + "\" name=\"" + str(name) + \
	     "\" type=\"" + ("password" if password else "text")
	if size != None:
		s += "\" size=\"" + str(size) 
	s += "\" value=\"" + str(value)
	s += "\"/>"
	return s

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

def form_row(id, label, controls):
	s  = "<div class=\"control-group\">"
	if label != None:
		s +=   "<label class=\"control-label\""
	if id != None:
		s += "for=\"" + id + "\""
		s += ">" + label + "</label>"
	s +=   "<div class=\"controls\">" + controls + "</div>"
	s += "</div>"
	return s

def form_input(id, label, name):
	return form_row(id, label, f_input(id, name))

def form_password(id, label, name):
	return form_row(id, label, f_input(id, name, password=True))

def form_submit(value=None):
	return form_row(None, None, f_submit(value))
