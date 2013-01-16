import menu
import userlist

def addUser(data, conf):
	print(menu.header())
	users = userlist.UserList(conf.get("users"))

	name = data.getfirst("username", "")
	email = data.getfirst("email", "")
	passwd = data.getfirst("password", "")
	passwd_again = data.getfirst("password_again", "")

	failures = ""
	if name == "":
		failures += "<li>No username specified!</li>"
	if email == "":
		failures += "<li>No email specified!</li>"
	if passwd == "":
		failures += "<li>Password empty!</li>"
	if passwd != passwd_again:
		failures += "<li>Passwords do not match!</li>"
	if users.find(name) is not None:
		failures += "<li>Username already taken!</li>"
	if failures != "":
		print("<h1>Creating user failed</h1>")
		print("<div><ul>")
		print(failures)
		print("</ul></div>")
		return

	user = userlist.User(name, email, passwd, [])
	users.append(user)

	print("<h1>User created</h1>")
	print("<div>Creation of user " + name + " was successful.</div>")
