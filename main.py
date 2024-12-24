from tkinter import Tk
from diary_database import DiaryDatabase
from diary_ui import DiaryUI

if __name__ == "__main__":
    db = DiaryDatabase()
    root = Tk()
    DiaryUI(root, db)
    root.mainloop()
    db.close()