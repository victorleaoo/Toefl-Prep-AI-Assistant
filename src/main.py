#!/usr/bin/env python3

"""
TOEFL Prep - Entry point

Launches the main application window. App components are modularized under
app.py (shell), screens/, ui/, and storage.py.
"""

from app import MainWindow


def main() -> None:
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()