import sqlite3
class Database:
    def get_db(self):
        connection = sqlite3.connect("database.db")
        return connection

    def create_db(self):
        con = self.get_db()
        con.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
                                                        name TEXT UNIQUE,
                                                        password_hash TEXT)""")
        con.commit()
        con.close()

    def check_user(self, name):
        con = self.get_db()
        user = con.execute("""SELECT * FROM users WHERE name = ?""", (name, )).fetchone()
        if user:
            con.close()
            return True
        else:
            con.close()
            return False

products = {
    1: {
        "name": "AMD Ryzen 9 9800x3D",
        "type": "Процессор",
        "price": "49500",
        "author": "AMD",
    },
    2: {
        "name": "Nvidia GeForce RTX 5060",
        "type": "Видеокарта",
        "price": "53000",
        "author": "Palit",
    },
    3: {
        "name": "Samsung Odessey G5",
        "type": "Монитор",
        "price": "20990",
        "author": "Samsung",
    },
}