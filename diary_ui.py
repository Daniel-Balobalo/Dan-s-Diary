import contextlib
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, font as tkfont
from tkinter.ttk import Style, Button, Entry, Frame
from diary_database import is_valid_date

class DiaryUI:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.selected_entry_id = None

        # Paper-like theme settings
        self.paper_bg = "#f5f5dc"  # Beige paper color
        self.paper_fg = "#333333"  # Dark text
        self.paper_shadow = "#d0d0c0"  # Subtle shadow
        self.paper_highlight = "#fffff0"  # Brighter paper areas
        self.font = self.get_nice_font()
        
        master.title("Dan's Diary")
        master.geometry("750x550")
        master.configure(bg=self.paper_shadow)
        
        # Main paper area
        self.main_paper = Frame(master)
        self.main_paper.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create texture canvas
        self.texture_canvas = tk.Canvas(
            self.main_paper,
            bg=self.paper_bg,
            highlightthickness=0,
            bd=0
        )
        self.texture_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind canvas resize to update texture
        self.texture_canvas.bind("<Configure>", self.draw_paper_texture)
        
        # Style configuration
        self.style = Style()
        self.style.configure("TFrame", background=self.paper_bg)
        self.style.configure("TButton", 
                           font=self.font,
                           background=self.paper_highlight,
                           relief=tk.RAISED,
                           borderwidth=1)
        self.style.configure("TLabel", 
                           font=self.font,
                           background=self.paper_bg,
                           foreground=self.paper_fg)
        self.style.configure("TEntry", 
                           font=self.font,
                           fieldbackground="white",
                           relief=tk.FLAT,
                           borderwidth=1)
        
        # Main content frame (on top of texture)
        self.content_frame = Frame(self.texture_canvas)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Entry List Frame with shadow effect
        self.entry_list_frame = Frame(self.content_frame)
        self.entry_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=10)
        
        # Shadow effect for listbox
        self.listbox_shadow = tk.Canvas(
            self.entry_list_frame,
            bg=self.paper_shadow,
            highlightthickness=0,
            height=450,
            width=220
        )
        self.listbox_shadow.pack(padx=(0, 3), pady=(0, 3))
        
        self.entry_list = tk.Listbox(
            self.listbox_shadow,
            width=30,
            height=25,
            bg="white",
            font=self.font,
            bd=0,
            highlightthickness=0,
            selectbackground="#e0e0c0",
            activestyle="none"
        )
        self.entry_list.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.entry_list.bind("<<ListboxSelect>>", self.load_entry)
        
        # Entry Details Frame
        self.details_frame = Frame(self.content_frame)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Date Entry
        date_frame = Frame(self.details_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(date_frame, text="Date (YYYY-MM-DD):").pack(anchor=tk.W)
        self.date_entry = Entry(date_frame)
        self.date_entry.pack(fill=tk.X, ipady=3)
        
        # Title Entry
        title_frame = Frame(self.details_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(title_frame, text="Title:").pack(anchor=tk.W)
        self.title_entry = Entry(title_frame)
        self.title_entry.pack(fill=tk.X, ipady=3)
        
        # Content Text
        content_frame = Frame(self.details_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(content_frame, text="Content:").pack(anchor=tk.W)
        
        # Shadow for text area
        text_shadow = tk.Canvas(
            content_frame,
            bg=self.paper_shadow,
            highlightthickness=0
        )
        text_shadow.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))
        
        self.content_text = scrolledtext.ScrolledText(
            text_shadow,
            wrap=tk.WORD,
            height=10,
            bg="white",
            font=self.font,
            bd=0,
            highlightthickness=0,
            padx=5,
            pady=5
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Buttons Frame
        self.button_frame = Frame(self.content_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        Button(self.button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Update Entry", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        Button(self.button_frame, text="Search", command=self.search_entries).pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status_frame = Frame(self.content_frame, relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.status_label = tk.Label(
            self.status_frame,
            text="Welcome to Dan's Diary!",
            bg=self.paper_highlight,
            font=self.font
        )
        self.status_label.pack(fill=tk.X, padx=2, pady=2)
        
        self.load_entries()

    def get_nice_font(self):
        """Try to find a nice handwriting-style font"""
        preferred_fonts = ["Segoe Print", "Comic Sans MS", "Arial"]
        available_fonts = tkfont.families()
        
        for font in preferred_fonts:
            if font in available_fonts:
                return (font, 11)
        return ("Arial", 11)

    def draw_paper_texture(self, event=None):
        """Draw subtle paper texture lines on the canvas"""
        width = self.texture_canvas.winfo_width()
        height = self.texture_canvas.winfo_height()
        
        self.texture_canvas.delete("texture")
        
        # Draw subtle horizontal lines like paper
        for y in range(0, height, 4):
            # Vary the color slightly for organic feel
            shade = 240 - (y % 10)
            color = f"#{shade:02x}{shade:02x}{shade-10:02x}"
            self.texture_canvas.create_line(
                0, y, width, y,
                fill=color,
                tags="texture",
                width=1
            )
        
        # Add some random "imperfections" to make it look more like paper
        for _ in range(20):
            x = tk.randint(0, width)
            y = tk.randint(0, height)
            size = tk.randint(1, 3)
            shade = tk.randint(220, 240)
            color = f"#{shade:02x}{shade:02x}{shade-20:02x}"
            self.texture_canvas.create_oval(
                x, y, x+size, y+size,
                fill=color,
                outline="",
                tags="texture"
            )

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
            self.load_entries()
            self.update_status("Entry added successfully!")
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
            self.load_entries()
            self.update_status("Entry updated successfully!")
        else:
            self.update_status("All fields are required.")

    def delete_entry(self):
        if self.selected_entry_id is None:
            messagebox.showwarning("Error", "No entry selected.")
            return
        if messagebox.askyesno("Confirm", "Delete this entry?"):
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