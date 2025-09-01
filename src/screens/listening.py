from datetime import date
from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox

import storage
from ui.timer import TimerWidget
from ui.scrollable import ScrollableFrame


class ListeningRow(ttk.Frame):
    def __init__(self, parent: tk.Widget, item: Dict, on_save, on_delete):
        super().__init__(parent)
        self.item = item
        self.on_save = on_save
        self.on_delete = on_delete

        # Columns: Link Number | Questions Link | Right Answers | Day | Save | Delete
        self.lbl_id = ttk.Label(self, text=str(item["id"]))
        self.ent_url = ttk.Entry(self, width=48)
        self.ent_url.insert(0, item.get("url", ""))
        self.ent_right = ttk.Spinbox(self, from_=0, to=999, width=6)
        self.ent_right.set(str(item.get("right_answers", 0)))
        self.ent_day = ttk.Entry(self, width=12)
        self.ent_day.insert(0, item.get("day", ""))
        self.btn_save = ttk.Button(self, text="Save", command=self._save)
        self.btn_delete = ttk.Button(self, text="Delete", command=self._delete)

        self.lbl_id.grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.ent_url.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.ent_right.grid(row=0, column=2, padx=6, pady=6)
        self.ent_day.grid(row=0, column=3, padx=6, pady=6)
        self.btn_save.grid(row=0, column=4, padx=6, pady=6)
        self.btn_delete.grid(row=0, column=5, padx=6, pady=6)

        self.grid_columnconfigure(1, weight=1)

    def _save(self):
        url = self.ent_url.get().strip()
        day_str = self.ent_day.get().strip()
        try:
            right = int(self.ent_right.get())
            if right < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid value", "Right Answers must be a non-negative integer.")
            return

        if not day_str:
            messagebox.showerror("Missing value", "Day cannot be empty. Use YYYY-MM-DD.")
            return

        if not url:
            messagebox.showerror("Missing value", "Questions Link cannot be empty.")
            return

        updated = {
            "id": self.item["id"],
            "url": url,
            "right_answers": right,
            "day": day_str,
        }
        self.on_save(updated)

    def _delete(self):
        if messagebox.askyesno("Delete", f"Delete item {self.item['id']}?"):
            self.on_delete(self.item["id"]) 


class ListeningScreen(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_back):
        super().__init__(parent, padding=6)
        self.on_back = on_back
        self.items: List[Dict] = []

        # Layout: top bar (back + title + timer), center table, bottom add button
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top bar
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(2, 8))
        top.grid_columnconfigure(1, weight=1)

        left_actions = ttk.Frame(top)
        left_actions.grid(row=0, column=0, sticky="w")
        back_btn = ttk.Button(left_actions, text="← Back", command=self.on_back)
        back_btn.grid(row=0, column=0, sticky="w", padx=(0, 6))
        tips_btn = ttk.Button(left_actions, text="Listening Tips", command=self._show_tips)
        tips_btn.grid(row=0, column=1, sticky="w")

        title = ttk.Label(top, text="Listening", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=1)

        timer = TimerWidget(top)
        timer.grid(row=0, column=2, sticky="e")

        # Table header + rows inside a centered block
        center = ttk.Frame(self)
        center.grid(row=1, column=0, sticky="nsew")
        for i in range(3):
            center.grid_columnconfigure(i, weight=1)
            center.grid_rowconfigure(i, weight=1)

        table_block = ttk.Frame(center)
        table_block.grid(row=1, column=1, sticky="nsew")
        table_block.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(table_block)
        header.grid(row=0, column=0, sticky="ew")
        labels = ["Link Number", "Questions Link", "Right Answers", "Day", "Save", "Delete"]
        widths = [12, 48, 12, 12, 8, 8]
        for i, (txt, w) in enumerate(zip(labels, widths)):
            lbl = ttk.Label(header, text=txt, font=("Segoe UI", 10, "bold"))
            lbl.grid(row=0, column=i, padx=6, pady=(0, 6), sticky="w")
            header.grid_columnconfigure(i, weight=1 if i == 1 else 0)

        self.scroll = ScrollableFrame(table_block)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        table_block.grid_rowconfigure(1, weight=1)

        # Bottom controls
        bottom = ttk.Frame(self)
        bottom.grid(row=2, column=0, pady=8)
        self.add_btn = ttk.Button(bottom, text="+ Add new item", command=self.add_item)
        self.add_btn.grid(row=0, column=0)

        # Load existing
        self._load_items()

    # Data handling
    def _load_items(self):
        try:
            self.items = storage.load_listening_items()
        except Exception as e:
            messagebox.showwarning("Load failed", f"Could not load items: {e}")
            self.items = []
        self._render_rows()

    def _render_rows(self):
        # Clear existing rows
        for child in list(self.scroll.inner.winfo_children()):
            child.destroy()
        for idx, item in enumerate(self.items):
            row = ListeningRow(self.scroll.inner, item=item, on_save=self._save_item, on_delete=self._delete_item)
            row.grid(row=idx, column=0, sticky="ew")
            self.scroll.inner.grid_columnconfigure(0, weight=1)

    def _save_all(self):
        try:
            storage.save_listening_items(self.items)
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save items: {e}")

    def _save_item(self, updated: Dict):
        # Update in-memory list
        found = False
        for i, it in enumerate(self.items):
            if it["id"] == updated["id"]:
                self.items[i] = updated
                found = True
                break
        if not found:
            self.items.append(updated)
        self._save_all()
        messagebox.showinfo("Saved", f"Item {updated['id']} saved.")

    def _delete_item(self, item_id: int):
        # update local state and persist
        self.items = [it for it in self.items if it.get("id") != item_id]
        try:
            storage.delete_listening_item(item_id)
        except Exception as e:
            messagebox.showerror("Delete failed", f"Could not delete item: {e}")
            return
        self._render_rows()

    def add_item(self):
        new_id = storage.next_id(self.items)
        new_item = {
            "id": new_id,
            "url": "",
            "right_answers": 0,
            "day": date.today().isoformat(),
        }
        self.items.append(new_item)
        self._render_rows()

    def _show_tips(self):
        tips_text = (
            "The TOEFL Listening Section measures your ability to understand spoken English in academic environments. "
            "You'll listen to audio clips and then answer questions about them. The clips are typically:\n\n"
            "- Lectures: 3-5 minutes long, featuring a professor lecturing, sometimes with student questions.\n\n"
            "- Conversations: About 3 minutes long, involving two speakers in a university setting (e.g., a student and a librarian or professor).\n\n"
            "You will hear each audio clip only once. You are allowed to take notes while you listen, which is a crucial skill for this section. "
            "You'll have about 41 to 57 minutes to complete the entire section.\n\n"
            "Tips: \n"
            "1. Take Effective Notes: This is the most important skill. Don't try to write everything. Instead, focus on capturing the main ideas, key terms, examples, and the relationships between concepts (e.g., cause/effect, steps in a process). Use abbreviations and symbols to save time.\n\n"
            "2. Listen for the Main Idea: The first few sentences of a lecture or conversation usually introduce the main topic or purpose. Pay close attention to the beginning to understand the \"gist\" of the audio.\n\n"
            "3. Understand the Speaker's Purpose and Attitude: Some questions ask why the speaker says something. Listen to their tone of voice and intonation. Are they certain, doubtful, surprised? This will help you answer questions about attitude and function.\n\n"
            "4. Pay Attention to Signposts: Speakers use transition words and phrases like \"First\", \"However\", \"Now let's turn to...\", or \"To sum up...\" to organize their ideas. These \"signposts\" help you follow the structure of the talk and understand how ideas are connected."
        )

        win = tk.Toplevel(self)
        win.title("Listening Tips")
        win.minsize(500, 400)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)

        text = tk.Text(win, wrap="word")
        text.grid(row=0, column=0, sticky="nsew")
        text.insert("1.0", tips_text)
        text.configure(state="disabled")

        btn_close = ttk.Button(win, text="Close", command=win.destroy)
        btn_close.grid(row=1, column=0, pady=8)
