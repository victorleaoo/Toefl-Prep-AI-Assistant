from typing import Optional
import tkinter as tk
from tkinter import ttk


class TimerWidget(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.elapsed_seconds: int = 0
        self.running = False
        self._tick_job: Optional[str] = None

        self.time_label = ttk.Label(self, text=self._format_time(), font=("Segoe UI", 12, "bold"))
        self.time_label.grid(row=0, column=0, padx=(0, 6))

        self.start_btn = ttk.Button(self, text="Start", command=self.start)
        self.pause_btn = ttk.Button(self, text="Pause", command=self.pause)
        self.reset_btn = ttk.Button(self, text="Reset", command=self.reset)

        self.start_btn.grid(row=0, column=1, padx=2)
        self.pause_btn.grid(row=0, column=2, padx=2)
        self.reset_btn.grid(row=0, column=3, padx=2)

    def _format_time(self) -> str:
        hrs = self.elapsed_seconds // 3600
        mins = (self.elapsed_seconds % 3600) // 60
        secs = self.elapsed_seconds % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def _tick(self):
        if self.running:
            self.elapsed_seconds += 1
            self.time_label.configure(text=self._format_time())
            self._tick_job = self.after(1000, self._tick)

    def start(self):
        if not self.running:
            self.running = True
            self._tick()

    def pause(self):
        self.running = False
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None

    def reset(self):
        self.pause()
        self.elapsed_seconds = 0
        self.time_label.configure(text=self._format_time())
