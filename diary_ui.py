import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

class DiaryUI:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.selected_entry_id = None

        master.title("Diary Application")
        master.geometry("600x400")

        # Entry List
        self.entry_list = tk.Listbox(master, width=30)
        self.entry_list.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.entry_list.bind("<<ListboxSelect>>", self.load_entry)

        # Entry Details
        self.details_frame = tk.Frame(master)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.details_frame, text="Date (YYYY-MM-DD):").pack()
        self.date_entry = tk.Entry(self.details_frame)
        self.date_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Title:").pack()
        self.title_entry = tk.Entry(self.details_frame)
        self.title_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Content:").pack()
        self.content_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=10)
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(self.button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Update Entry", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        self.load_entries()

    def load_entries(self):
        self.entry_list.delete(0, tk.END)
        entries = self.db.get_entries()
        for entry in entries:
            self.entry_list.insert(tk.END, f"{entry[1]} - {entry[2]}")

    def load_entry(self, event):
        try:
            selected_index = self.entry_list.curselection()[0]
            entry_id = self.db.get_entries()[selected_index][0]
            entry = self.db.get_entry_by_id(entry_id)

            self.selected_entry_id = entry_id
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, entry[0])
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, entry[1])
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert("1.0", entry[2])
        except IndexError:
            pass

    def add_entry(self):
        date = self.date_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if date and title and content:
            self.db.add_entry(date, title, content)
            self.load_entries()
            self.clear_form()
            messagebox.showinfo("Success", "Entry added successfully!")
        else:
            messagebox.showwarning("Error", "All fields are required.")

    def update_entry(self):
        if self.selected_entry_id is None:
            messagebox.showwarning("Error", "No entry selected.")
            return
        date = self.date_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if date and title and content:
            self.db.update_entry(self.selected_entry_id, date, title, content)
            self.load_entries()
            self.clear_form()
            messagebox.showinfo("Success", "Entry updated successfully!")
        else:
            messagebox.showwarning("Error", "All fields are required.")

    def delete_entry(self):
        if self.selected_entry_id is None:
            messagebox.showwarning("Error", "No entry selected.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
        if confirm:
            self.db.delete_entry(self.selected_entry_id)
            self.load_entries()
            self.clear_form()
            messagebox.showinfo("Success", "Entry deleted successfully!")

    def clear_form(self):
        self.selected_entry_id = None
        self.date_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
