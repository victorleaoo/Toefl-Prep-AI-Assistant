import tkinter as tk
from tkinter import ttk
from typing import Dict

from utils import center_window
from screens.reading import ReadingScreen
from screens.listening import ListeningScreen
from screens.speaking import SpeakingScreen


APP_TITLE = "TOEFL Prep"


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(800, 520)
        self.configure(padx=16, pady=16)

        # Make root grid expandable
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Host a single content frame where we switch screens
        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # Initialize screens
        self._screens = {}
        self._screens["main"] = self._build_main_menu(self.content)
        self._screens["reading"] = ReadingScreen(self.content, on_back=lambda: self.show("main"))
        self._screens["listening"] = ListeningScreen(self.content, on_back=lambda: self.show("main"))
        self._screens["speaking"] = SpeakingScreen(self.content, on_back=lambda: self.show("main"))

        self.show("main")

        # Center after widgets are laid out
        self.after(0, lambda: center_window(self))

    def show(self, name: str) -> None:
        for _, frame in self._screens.items():
            frame.grid_forget()
        frame = self._screens[name]
        frame.grid(row=0, column=0, sticky="nsew")

    def _build_main_menu(self, parent: tk.Widget) -> tk.Frame:
        container = ttk.Frame(parent)

        # Use a 3x3 grid to easily center content at (1,1)
        for i in range(3):
            container.grid_columnconfigure(i, weight=1)
            container.grid_rowconfigure(i, weight=1)

        # Title
        title = ttk.Label(
            container,
            text="TOEFL Preparation",
            font=("Segoe UI", 22, "bold"),
            anchor="center",
        )
        title.grid(row=0, column=1, pady=(12, 8))

        # Buttons block (2x2 grid) centered
        buttons_frame = ttk.Frame(container, padding=10)
        buttons_frame.grid(row=1, column=1)

        for i in range(2):
            buttons_frame.grid_columnconfigure(i, weight=1, uniform="btns")
            buttons_frame.grid_rowconfigure(i, weight=1, uniform="btns")

        # Create the four buttons
        labels_positions = [
            ("Reading", 0, 0, lambda: self.show("reading")),
            ("Listening", 0, 1, lambda: self.show("listening")),
            ("Speaking", 1, 0, lambda: self.show("speaking")),
            ("Writing", 1, 1, lambda: None),
        ]

        for text, r, c, cmd in labels_positions:
            btn = ttk.Button(buttons_frame, text=text, command=cmd)
            btn.grid(row=r, column=c, padx=12, pady=12, ipadx=28, ipady=24, sticky="nsew")

        return container
