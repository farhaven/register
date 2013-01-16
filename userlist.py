import os
import Cookie
import pickle
import random
import hashlib

class Login(object):
	def __init__(self, cookies, userlist, form):
		self.cookies = cookies
		self.userlist = userlist
		try:
			self.cookies["USERNAME"] = form["username"].value
			self.cookies["PASSWORD"] = form["password"].value
		except:
			pass

	def name(self):
		try:
			return self.cookies["USERNAME"].value
		except:
			return None

	def clear(self):
		self.cookies["USERNAME"] = None
		self.cookies["PASSWORD"] = None

	def valid(self):
		try:
			name = self.cookies["USERNAME"].value
			passwd = self.cookies["PASSWORD"].value
			return self.userlist.validate(name, passwd)
		except:
			return False

class User(object):
	def __str__(self):
		return "&lt;nick=" + str(self.name) + "; admin=" + str(self.is_admin) + "&gt;"

	def __init__(self, name, email, password, shirts):
		self.is_admin = False
		self.name = name
		self.email = email
		self.shirts = shirts
		self.salt = str(random.random())
		m = hashlib.sha1()
		m.update(password)
		m.update(self.salt)
		self.password = m.hexdigest()

	def validate(self, password):
		m = hashlib.sha1()
		m.update(password)
		m.update(self.salt)
		return self.password == m.hexdigest()

class UserList(object):
	def __init__(self, path):
		self.path = path

	def as_list(self):
		fh = None
		try:
			fh = open(self.path, "r")
		except:
			return []
		users = pickle.load(fh)
		fh.close()
		return users

	def append(self, user):
		users = self.as_list()
		fh = open(self.path, "w")
		users.append(user)
		pickle.dump(users, fh)
		fh.close()

	def find(self, name):
		users = self.as_list()
		for x in users:
			if x.name == name:
				return x
		return None

	def validate(self, name, passwd):
		u = self.find(name)
		if u is None:
			return False
		return u.validate(passwd)
