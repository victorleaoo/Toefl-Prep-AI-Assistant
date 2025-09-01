from datetime import date
from typing import List, Dict
import tkinter as tk
from tkinter import ttk, messagebox

import storage
from ui.timer import TimerWidget
from ui.scrollable import ScrollableFrame


class ReadingRow(ttk.Frame):
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


class ReadingScreen(ttk.Frame):
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
        tips_btn = ttk.Button(left_actions, text="Reading Tips", command=self._show_tips)
        tips_btn.grid(row=0, column=1, sticky="w")

        title = ttk.Label(top, text="Reading", font=("Segoe UI", 16, "bold"))
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
            self.items = storage.load_reading_items()
        except Exception as e:
            messagebox.showwarning("Load failed", f"Could not load items: {e}")
            self.items = []
        self._render_rows()

    def _render_rows(self):
        # Clear existing rows
        for child in list(self.scroll.inner.winfo_children()):
            child.destroy()
        for idx, item in enumerate(self.items):
            row = ReadingRow(self.scroll.inner, item=item, on_save=self._save_item, on_delete=self._delete_item)
            row.grid(row=idx, column=0, sticky="ew")
            self.scroll.inner.grid_columnconfigure(0, weight=1)

    def _save_all(self):
        try:
            storage.save_reading_items(self.items)
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
            storage.delete_reading_item(item_id)
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
        # Show tips in a separate top-level window (popup)
        tips_text = (
            "The TOEFL Reading Section is designed to test your ability to understand "
            "university-level academic texts. You'll be given 3 or 4 passages, each "
            "about 700 words long, followed by approximately 10 multiple-choice questions "
            "per passage. The topics cover a wide range of academic subjects, but you don't "
            "need any prior knowledge as all the information needed to answer the questions "
            "is in the text. You will have between 54 and 72 minutes to complete the entire section.\n\n"
            "Tips:\n"
            "1. Manage Your Time Wisely: With a strict time limit, it's crucial to pace yourself. "
            "Aim to spend about 18 minutes on each passage and its questions. If a question is too "
            "difficult, make your best guess and move on.\n\n"
            "2. Focus on the Text: All answers can be found directly in or inferred from the passage. "
            "Do not use your outside knowledge to answer the questions.\n\n"
            "3. Use the Process of Elimination: For challenging questions, try to eliminate the answer "
            "choices that are clearly incorrect. This significantly increases your chances of selecting "
            "the right one.\n\n"
            "4. Follow the Order of the Passage: Most questions (except for the final summary or main idea "
            "questions) follow the chronological order of the information in the text. This means the answer "
            "to question 4 will appear in the passage after the answer to question 3. Use this to help you "
            "locate information faster and avoid rereading the entire text for every question."
        )

        win = tk.Toplevel(self)
        win.title("Reading Tips")
        win.minsize(500, 400)
        win.transient(self.winfo_toplevel())
        win.grab_set()

        # Layout
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)

        text = tk.Text(win, wrap="word")
        text.grid(row=0, column=0, sticky="nsew")
        text.insert("1.0", tips_text)
        text.configure(state="disabled")

        btn_close = ttk.Button(win, text="Close", command=win.destroy)
        btn_close.grid(row=1, column=0, pady=8)
