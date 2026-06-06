import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
class Database:
    def get_db(self):
        connection = sqlite3.connect("data/database.db")
        return connection

    def create_db(self):
        with self.get_db() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
                                                        name TEXT UNIQUE,
                                                        password_hash TEXT,
                                                        role TEXT,
                                                        token TEXT)""")

    def check_user(self, name):
        with self.get_db() as con:
            user = con.execute("""SELECT * FROM users WHERE name = ?""", (name, )).fetchone()
            if user:
                return True
            else:
                return False
        
    def create_new_user(self, name, password):
        password_hash = generate_password_hash(password)
        with self.get_db() as con:
            con.execute("""INSERT INTO users (name, password_hash, role) VALUES (?, ?, ?)""", (name, password_hash, "user"))
    
    def token_gen(self):
        token = secrets.token_urlsafe(16)
        return token
    
    def set_token(self, token, name):
        con = self.get_db()
        con.execute("""UPDATE users SET token = ? WHERE name = ?""", (token, name))
        con.commit()
        con.close()

    def select_user(self, name):
        con = self.get_db()
        user = con.execute("""SELECT * FROM USERS WHERE name = ?""", (name, )).fetchone()
        con.close()
        return user
    
    def get_profile(self, session):
        con = self.get_db()
        user_data = con.execute("""SELECT * FROM users WHERE id = ?""", (session["user_id"], )).fetchone()
        user_data_dict = {
            "name": user_data[1],
            "id": user_data[0],
            "role": user_data[3],
            "token": user_data[4]
        }
        return user_data_dict
    
    def get_all_users(self):
        con = self.get_db()
        result = con.execute("""SELECT * FROM users""").fetchall()
        return result
    
    def change_name(self, user_id, new_name):
        con = self.get_db()
        con.execute("""UPDATE users SET name = ? WHERE id = ?""", (new_name, user_id))
        con.commit()

    def change_password(self, user_id, new_password):
        con = self.get_db()
        password = generate_password_hash(new_password)
        con.execute("""UPDATE users SET password_hash = ? WHERE id = ?""", (password, user_id))
        con.commit()

    def change_role(self, user_id, new_role):
        con = self.get_db()
        con.execute("""UPDATE users SET role = ? WHERE id = ?""", (new_role, user_id))
        con.commit()

    def get_role(self, user_id):
        con = self.get_db()
        result = con.execute("""SELECT role FROM users WHERE id=?""", (user_id,)).fetchall()
        return result


products = {
    1: {
        "name": "AMD Ryzen 9 9800x3D",
        "type": "Процессор",
        "price": 49500,
        "author": "AMD",
    },
    2: {
        "name": "Nvidia GeForce RTX 5060",
        "type": "Видеокарта",
        "price": 53000,
        "author": "Palit",
    },
    3: {
        "name": "Samsung Odessey G5",
        "type": "Монитор",
        "price": 20990,
        "author": "Samsung",
    },
}