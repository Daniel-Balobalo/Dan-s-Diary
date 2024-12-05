import sqlite3

class DiaryDatabase:
    def __init__(self, db_name="diary.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
        ''')
        self.conn.commit()

    def add_entry(self, date, title, content):
        self.cursor.execute("INSERT INTO journal (date, title, content) VALUES (?, ?, ?)", (date, title, content))
        self.conn.commit()

    def get_entries(self):
        self.cursor.execute("SELECT id, date, title FROM journal ORDER BY date DESC")
        return self.cursor.fetchall()

    def get_entry_by_id(self, entry_id):
        self.cursor.execute("SELECT date, title, content FROM journal WHERE id=?", (entry_id,))
        return self.cursor.fetchone()

    def update_entry(self, entry_id, date, title, content):
        self.cursor.execute("UPDATE journal SET date=?, title=?, content=? WHERE id=?", (date, title, content, entry_id))
        self.conn.commit()

    def delete_entry(self, entry_id):
        self.cursor.execute("DELETE FROM journal WHERE id=?", (entry_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
