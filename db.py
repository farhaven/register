import MySQLdb

statements = {
		"table_create_users": "CREATE TABLE IF NOT EXISTS users (u_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, salt TEXT NOT NULL, pwhash TEXT NOT NULL, paid BOOLEAN NOT NULL, there BOOLEAN NOT NULL, UNIQUE(name(128)))",
		"table_create_shirts": "CREATE TABLE IF NOT EXISTS shirts (s_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, u_id INT, size TEXT NOT NULL, FOREIGN KEY (u_id) REFERENCES users(u_id))"

}

def init(conf):
	conn = MySQLdb.connect(user=conf.get("db_user"), passwd=conf.get("db_pass"), db="register")
	c = conn.cursor()
	c.execute(statements["table_create_users"])
	c.execute(statements["table_create_shirts"])
	return conn
