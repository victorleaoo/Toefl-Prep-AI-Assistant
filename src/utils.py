import tkinter as tk


def center_window(win: tk.Tk, width: int = 900, height: int = 600) -> None:
    """Center the window on the current screen."""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = max((screen_w // 2) - (width // 2), 0)
    y = max((screen_h // 2) - (height // 2), 0)
    win.geometry(f"{width}x{height}+{x}+{y}")
