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
        master.configure(bg="#2e975d")  # Updated light green background

        # Style
        self.style = Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12), background="#2e975d")
        self.style.configure("TEntry", font=("Arial", 12))

        # Entry List
        self.entry_list = tk.Listbox(master, width=30, height=25, bg="white")
        self.entry_list.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.entry_list.bind("<<ListboxSelect>>", self.load_entry)

        # Entry Details
        self.details_frame = tk.Frame(master, bg="#2e975d")
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.details_frame, text="Date (YYYY-MM-DD):", bg="#2e975d").pack()
        self.date_entry = Entry(self.details_frame)
        self.date_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Title:", bg="#2e975d").pack()
        self.title_entry = Entry(self.details_frame)
        self.title_entry.pack(fill=tk.X)

        tk.Label(self.details_frame, text="Content:", bg="#2e975d").pack()
        self.content_text = scrolledtext.ScrolledText(self.details_frame, wrap=tk.WORD, height=10, bg="white")
        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        self.button_frame = tk.Frame(master, bg="#2e975d")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        Button(self.button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Update Entry", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Search", command=self.search_entries).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(master, text="Welcome to Dan's Diary!", relief=tk.SUNKEN, bg="#2e975d")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.load_entries()

    def draw_gradient(self, canvas, color1, color2, color3):
        width = 700
        height = 500
        limit = height // 2
        for i in range(limit):
            r1, g1, b1 = self.hex_to_rgb(color1)
            r2, g2, b2 = self.hex_to_rgb(color2)
            r3, g3, b3 = self.hex_to_rgb(color3)
            r = int(r1 + (r2 - r1) * i / limit)
            g = int(g1 + (g2 - g1) * i / limit)
            b = int(b1 + (b2 - b1) * i / limit)
            color = self.rgb_to_hex(r, g, b)
            canvas.create_rectangle(0, i, width, i + 1, outline=color, fill=color)
            r = int(r2 + (r3 - r2) * i / limit)
            g = int(g2 + (g3 - g2) * i / limit)
            b = int(b2 + (b3 - b2) * i / limit)
            color = self.rgb_to_hex(r, g, b)
            canvas.create_rectangle(0, limit + i, width, limit + i + 1, outline=color, fill=color)

    def hex_to_rgb(self, hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

    # ... rest of the code ...
        
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
        self.db.delete_entry(self.selected_entry_id)
        self.clear_form()
        self.load_entries()
        self.update_status("Entry deleted successfully!")

    def clear_form(self):
        self.selected_entry_id = None
        self.date_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.update_status("Form cleared.")

    def search_entries(self):
        search_term = simpledialog.askstring("Search Entries", "Enter search term:")
        if search_term:
            self.entry_list.delete(0, tk.END)
            entries = self.db.search_entries(search_term)
            for entry in entries:
                self.entry_list.insert(tk.END, f"{entry[1]} - {entry[2]}")
            self.update_status(f"Found {len(entries)} entries matching '{search_term}'.")

    def update_status(self, message):
        self.status_label.config(text=message)