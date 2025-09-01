# TOEFL Prep (Desktop)

A simple local desktop app scaffolding for TOEFL preparation built with Python and Tkinter. The main screen shows four buttons (placeholders) for the TOEFL sections: Reading, Listening, Speaking, and Writing.

## Run locally

Requirements:
- Python 3.8+
- Tkinter (usually included; on Linux, you may need to install `python3-tk`) -> sudo apt-get install python3-tk 

Create and activate a virtual environment (optional but recommended), then run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python src/main.py
```

## Build a Windows .exe

To generate a standalone Windows executable, you can use PyInstaller.

 - For Speaking (audio), install system libs: on Debian/Ubuntu `sudo apt-get install libportaudio2` (sounddevice backend).
1) Install PyInstaller in your environment:

```bash
python -m pip install pyinstaller
```

2) Build the executable:

```bash
pyinstaller --noconfirm --onefile --windowed --name "TOEFL Prep" src/main.py
```

Artifacts will be placed under `dist/`. The single-file exe will be `dist/TOEFL Prep.exe`.

Notes:
- Use `--windowed` to suppress the console window for GUI apps.
- If you add images/fonts/data later, include them with `--add-data` options or a .spec file.

## Project structure

```
/ (repo root)
├─ src/
│  └─ main.py           # Tkinter main window with 4 buttons (no functionality yet)
├─ README.md            # This file
└─ requirements.txt     # (optional) dependencies; tkinter is stdlib
```

## Next steps

- Wire the buttons to dedicated modules for each section
- Add simple routing and shared styles
- Package resources (icons, fonts) and app metadata
- Add tests for non-GUI logic as it grows
