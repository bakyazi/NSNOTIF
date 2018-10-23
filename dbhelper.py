import sqlite3


class DBHelper:

    def __init__(self, dbname="nsnotif.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS users (username text , cid text, PRIMARY KEY(username))"
        self.conn.execute(tblstmt)
        self.conn.commit()

    def add_user(self, username, cid):
        stmt = "INSERT INTO users (username, cid) VALUES (?, ?)"
        args = (username, cid)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, username):
        stmt = "DELETE FROM users WHERE username = (?)"
        args = (username,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_users(self):
        stmt = "SELECT * FROM users"
        return [(x[0],x[1]) for x in self.conn.execute(stmt)]

    def get_user(self,user_name):
        stmt = "SELECT * FROM users WHERE username = (?)"
        args = (user_name,)
        return [x for x in self.conn.execute(stmt,args)]

    def get_cid(self,username):
        stmt = "SELECT cid FROM users WHERE username = (?)"
        args = (username,)
        return self.conn.execute(stmt,args)[0]



    
            



