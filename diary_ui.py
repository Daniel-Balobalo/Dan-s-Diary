import contextlib
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from tkinter.ttk import Style, Button, Entry

from diary_database import is_valid_date

class DiaryUI:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.selected_entry_id = None

        master.title("Dan's Diary")
        master.geometry("700x500")
        master.configure(bg="#ccffcc")  # Light green background

        # Style
        self.style = Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12), background="#ccffcc")
        self.style.configure("TEntry", font=("Arial", 12))

        # Entry List
        self.entry_list = tk.Listbox(master, width=30, height=25, bg="white")
        self.entry_list.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.entry_list.bind("<<ListboxSelect>>", self.load_entry)

        # Entry Details
        self.details_frame = tk.Frame(master, bg="#ccffcc")
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.details_frame, text="Date (YYYY-MM-DD):", bg="#ccffcc").pack()
        self.date_entry = Entry(self.details_frame)
        self.date_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Title:", bg="#ccffcc").pack()
        self.title_entry = Entry(self.details_frame)
        self.title_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Content:", bg="#ccffcc").pack()
        self.content_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=10, bg="white")
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.button_frame = tk.Frame(master, bg="#ccffcc")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        Button(self.button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Update Entry", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Search", command=self.search_entries).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(master, text="Welcome to Dan's Diary!", relief=tk.SUNKEN, bg="#ccffcc")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_entries()
        
    def load_entries(self):
        self.entry_list.delete(0, tk.END)
        entries = self.db.get_entries()
        for entry in entries:
            self.entry_list.insert(tk.END, f"{entry[1]} - {entry[2]}")

    def load_entry(self, event):
        with contextlib.suppress(IndexError):
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

    def add_entry(self):
        date = self.date_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if not is_valid_date(date):
            messagebox.showwarning("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        if date and title and content:
            self.db.add_entry(date, title, content)
            self._extracted_from_delete_entry_10("Entry added successfully!")
        else:
            self.update_status("All fields are required.")

    def update_entry(self):
        if self.selected_entry_id is None:
            messagebox.showwarning("Error", "No entry selected.")
            return
        date = self.date_entry.get()
        title = self.title_entry.get()
        content = self.content_text.get("1.0", tk.END).strip()
        if not is_valid_date(date):
            messagebox.showwarning("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        if date and title and content:
            self.db.update_entry(self.selected_entry_id, date, title, content)
            self._extracted_from_delete_entry_10("Entry updated successfully!")
        else:
            self.update_status("All fields are required.")

    def delete_entry(self):
        if self.selected_entry_id is None:
            messagebox.showwarning("Error", "No entry selected.")
            return
        if confirm := messagebox.askyesno(
            "Confirm", "Are you sure you want to delete this entry?"
        ):
            self.db.delete_entry(self.selected_entry_id)
            self._extracted_from_delete_entry_10("Entry deleted successfully!")

    # TODO Rename this here and in `add_entry`, `update_entry` and `delete_entry`
    def _extracted_from_delete_entry_10(self, arg0):
        self.load_entries()
        self.clear_form()
        self.update_status(arg0)

    def clear_form(self):
        self.selected_entry_id = None
        self.date_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)

    def search_entries(self):
        if search_term := simpledialog.askstring(
            "Search", "Enter title to search:"
        ):
            results = [entry for entry in self.db.get_entries() if search_term.lower() in entry[2].lower()]
            self.entry_list.delete(0, tk.END)
            for entry in results:
                self.entry_list.insert(tk.END, f"{entry[1]} - {entry[2]}")

    def update_status(self, message):
        self.status_label.config(text=message)