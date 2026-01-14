import sqlite3

class SqliteDatabase:
    
    def __init__(self, path:str):
        self.path = path

    def execute(self, sql:str, params=()):
        with sqlite3.connect(self.path) as con:
            con.execute(sql, params)

    def fetchone(self, sql:str, params=()):
        with sqlite3.connect(self.path) as con:
            cur = con.execute(sql, params)
            return cur.fetchone()
    
    def fetchall(self, sql:str, params=()):
        with sqlite3.connect(self.path) as con:
            cur = con.execute(sql, params)
            return cur.fetchall()
