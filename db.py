import MySQLdb

def create_table(conn, name, values, constraints):
	s = "CREATE TABLE IF NOT EXISTS " + str(name) + " ("
	for v in values[:-1]:
		s += v + " NOT NULL, "
	try:
		s += values[-1] + " NOT NULL"
	except:
		pass
	if (len(constraints)) != 0:
		s += ", "
	for c in constraints[:-1]:
		s += c + ", "
	try:
		s += constraints[-1]
	except:
		pass
	s += ")"

	c = conn.cursor()
	c.execute(s)
	conn.commit()

def init(conf):
	conn = MySQLdb.connect(user=conf.get("db_user"), passwd=conf.get("db_pass"), db=conf.get("db_database"))
	create_table(conn, "users", [
			"u_id INT PRIMARY KEY AUTO_INCREMENT",
			"name TEXT",
			"email TEXT",
			"salt TEXT",
			"pwhash TEXT",
			"paid BOOLEAN",
			"there BOOLEAN",
			], [ "UNIQUE(name(128))" ]
		)

	create_table(conn, "shirts", [
			"s_id INT PRIMARY KEY AUTO_INCREMENT",
			"u_id INT",
			"size TEXT" ],
			[ "FOREIGN KEY (u_id) REFERENCES users(u_id)" ]
		)

	create_table(conn, "lunch", [
			"l_id INT PRIMARY KEY AUTO_INCREMENT",
			"u_id INT",
			"buns INT",
			"baloney BOOLEAN",
			"cheese BOOLEAN",
			"jam BOOLEAN",
			"cornflakes BOOLEAN" ],
			[ "FOREIGN KEY (u_id) REFERENCES users(u_id)" ]
		)

	return conn
