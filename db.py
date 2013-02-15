import MySQLdb

def create_table(conf, conn, name, values, constraints):
	c = conn.cursor()
	# IF NOT EXISTS causes warnings... stupid mysql
	c.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s and table_name = %s",
			(conf.get("db_database"), name))
	if c.fetchone()[0] != 0L:
		return
	s = "CREATE TABLE " + str(name) + " ("
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

	c.execute(s)
	conn.commit()

def init(conf):
	conn = MySQLdb.connect(user=conf.get("db_user"), passwd=conf.get("db_pass"), db=conf.get("db_database"))
	create_table(conf, conn, "users", [
			"u_id INT PRIMARY KEY AUTO_INCREMENT",
			"name TEXT",
			"email TEXT",
			"salt TEXT",
			"pwhash TEXT",
			"paid BOOLEAN DEFAULT false",
			"there BOOLEAN DEFAULT false",
			"ticket TEXT",
			"note TEXT",
			"note_done BOOLEAN DEFAULT false"
			], [ "UNIQUE(name(128))" ]
		)

	create_table(conf, conn, "shirts", [
			"s_id INT PRIMARY KEY AUTO_INCREMENT",
			"u_id INT",
			"size TEXT",
			"girly BOOLEAN" ],
			[ "FOREIGN KEY (u_id) REFERENCES users(u_id)" ]
		)

	create_table(conf, conn, "lunch", [
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
