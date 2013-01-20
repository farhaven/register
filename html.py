import cgi

def f_input(id, name, value="", size=None, password=False, placeholder=None):
	s  = "<input id=\"" + str(id) + "\" name=\"" + cgi.escape(name) + \
	     "\" class=\"span3" + \
	     "\" type=\"" + ("password" if password else "text")
	if size != None:
		s += "\" size=\"" + str(size) 
	if placeholder != None:
		s += "\" placeholder=\"" + cgi.escape(placeholder)
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
	s  = form_start()
	for x in items:
		s += x
	s += form_end()
	return s

def form_start(box=True):
	s = "<form method=\"POST\" class=\"form-horizontal\">"
	if box:
		s = "<div class=\"well\">" + s
	return s

def form_end(box=True):
	return "</form></div>" if box else "</form>"

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

def form_input(id, label, name, input_value="", icon=None, input_placeholder=None):
	code = f_input(id, name, value=input_value, placeholder=input_placeholder)
	if icon != None:
		code = "<div class=\"input-prepend\"><span class=\"add-on\"><i class=\"icon-" + icon + "\"></i></span>" + code + "</div>"
	return form_row(id, label, code)

def form_password(id, label, name, password_hint=None):
	code = f_input(id, name, password=True, placeholder=password_hint)
	return form_row(id, label, code)

def form_submit(value="OK"):
	code = "<button type=\"submit\" class=\"btn btn-primary\">"
	code += cgi.escape(value)
	code += "</button>"
	return form_row(None, None, code)

def colored_bool(value, yes="Ja", no="Nein"):
	code = yes if value else no
	if value:
		code = "<span class=\"yes\">" + code + "</span>"
	else:
		code = "<span class=\"no\">" + code + "</span>"
	return code

def bool_icon(value):
	icon = "ok" if value else "remove"
	return "<i class=\"icon-" + icon + "\"></i>"

