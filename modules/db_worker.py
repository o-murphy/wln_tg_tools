import sqlite3


class DataBase(object):
    def __init__(self, path):
        self.path = path

    def check_db(self):
        try:
            with sqlite3.connect(self.path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE "users" (
                        "id"	INTEGER NOT NULL UNIQUE,
                        "tg_id"	TEXT NOT NULL UNIQUE,
                        "tg_username"	TEXT NOT NULL UNIQUE,
                        "tg_name"	TEXT,
                        "wln_token"	TEXT NOT NULL,
                        "wln_user"	TEXT NOT NULL,
                        "role"	TEXT NOT NULL,
                        PRIMARY KEY("id" AUTOINCREMENT)
                    );
                """)
            print('CREATED NEW DATABASE')
        except:
            print('DATABASE CONNECTED')


    def user_login(self, tg_id, tg_username, wln_token, role, wln_user='', tg_name=''):
        with sqlite3.connect(self.path) as conn:
            row = (tg_id, tg_username, tg_name, wln_token, wln_user, role)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO "main"."users"("tg_id","tg_username","tg_name","wln_token","wln_user","role") 
                VALUES (?,?,?,?,?,?);
            """, row)
            conn.commit()


    def user_logout(self, tg_id):
        with sqlite3.connect(self.path) as conn:
            row = (tg_id, )
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM "main"."users" WHERE "tg_id" = ?;
            """, row)
            conn.commit()


    def search_token(self, tg_id):
        with sqlite3.connect(self.path) as conn:
            row = (tg_id, )
            cur = conn.cursor()
            cur.execute("""
                    SELECT * 
                    FROM "main"."users" 
                    WHERE "tg_id" = ?;
                """, row)
            res = cur.fetchone()
            if res:
                return res[4]
            else:
                return None

    def search_all(self):
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("""
                    SELECT * 
                    FROM "main"."users";
                """)
            res = cur.fetchall()
            if res:
                return res
            else:
                return None


# if __name__ == '__main__':
    # db = DataBase('sqlite3.db')
    # db.user_logout(415715051)
