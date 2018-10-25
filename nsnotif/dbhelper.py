import sqlite3


class DBHelper:

    def __init__(self, dbname="nsnotif.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS users (username text , cid text, PRIMARY KEY(username))"
        tblstmt1 = "CREATE TABLE IF NOT EXISTS teams (username text , team text, PRIMARY KEY(username,team))"
        self.conn.execute(tblstmt)
        self.conn.execute(tblstmt1)
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

    def add_team(self,username,team):
        stmt = "INSERT INTO teams (username, team) VALUES (?, ?)"
        args = (username, team)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_team(self, username,team):
        stmt = "DELETE FROM teams WHERE username = (?) AND team = (?)"
        args = (username,team)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_teams(self,username):
        stmt = "SELECT * FROM teams WHERE username = (?)"
        args = (username,)
        return [x[1] for x in self.conn.execute(stmt,args)]

    
            



