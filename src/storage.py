"""Local CSV storage utilities for TOEFL Prep.

Stores Reading section items as CSV with columns:
id,url,right_answers,day

File path: data/reading.csv relative to the project root.
"""

from __future__ import annotations

import csv
import os
from typing import List, Dict


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
READING_CSV = os.path.join(DATA_DIR, "reading.csv")
LISTENING_CSV = os.path.join(DATA_DIR, "listening.csv")
SPEAKING_CSV = os.path.join(DATA_DIR, "speaking.csv")
SPEAKING_AUDIO_DIR = os.path.join(DATA_DIR, "speaking_recordings")


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SPEAKING_AUDIO_DIR, exist_ok=True)

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_reading_items() -> List[Dict]:
    ensure_data_dir()
    items: List[Dict] = []
    if not os.path.exists(READING_CSV):
        return items
    with open(READING_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                items.append(
                    {
                        "id": int(row.get("id", "0") or 0),
                        "url": row.get("url", ""),
                        "right_answers": int(row.get("right_answers", "0") or 0),
                        "day": row.get("day", ""),
                    }
                )
            except Exception:
                # Skip malformed rows silently; could log in the future.
                continue
    # Keep sorted by id
    items.sort(key=lambda x: x["id"])
    return items


def save_reading_items(items: List[Dict]) -> None:
    ensure_data_dir()
    fieldnames = ["id", "url", "right_answers", "day"]
    with open(READING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in sorted(items, key=lambda x: x["id"]):
            writer.writerow(
                {
                    "id": it.get("id", 0),
                    "url": it.get("url", ""),
                    "right_answers": it.get("right_answers", 0),
                    "day": it.get("day", ""),
                }
            )


def next_id(items: List[Dict]) -> int:
    if not items:
        return 1
    return max(i.get("id", 0) for i in items) + 1


def delete_reading_item(item_id: int) -> None:
    """Delete a reading item by id from the CSV storage.

    Loads all items, filters out the given id, and writes back the file.
    """
    items = load_reading_items()
    filtered = [it for it in items if it.get("id") != item_id]
    save_reading_items(filtered)


# Listening section storage
def load_listening_items() -> List[Dict]:
    ensure_data_dir()
    items: List[Dict] = []
    if not os.path.exists(LISTENING_CSV):
        return items
    with open(LISTENING_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                items.append(
                    {
                        "id": int(row.get("id", "0") or 0),
                        "url": row.get("url", ""),
                        "right_answers": int(row.get("right_answers", "0") or 0),
                        "day": row.get("day", ""),
                    }
                )
            except Exception:
                continue
    items.sort(key=lambda x: x["id"])
    return items


def save_listening_items(items: List[Dict]) -> None:
    ensure_data_dir()
    fieldnames = ["id", "url", "right_answers", "day"]
    with open(LISTENING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in sorted(items, key=lambda x: x["id"]):
            writer.writerow(
                {
                    "id": it.get("id", 0),
                    "url": it.get("url", ""),
                    "right_answers": it.get("right_answers", 0),
                    "day": it.get("day", ""),
                }
            )


def delete_listening_item(item_id: int) -> None:
    items = load_listening_items()
    filtered = [it for it in items if it.get("id") != item_id]
    save_listening_items(filtered)


# Speaking section storage (no right_answers column)
def load_speaking_items() -> List[Dict]:
    ensure_data_dir()
    items: List[Dict] = []
    if not os.path.exists(SPEAKING_CSV):
        return items
    with open(SPEAKING_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                items.append(
                    {
                        "id": int(row.get("id", "0") or 0),
                        "url": row.get("url", ""),
                        "day": row.get("day", ""),
                    }
                )
            except Exception:
                continue
    items.sort(key=lambda x: x["id"])
    return items


def save_speaking_items(items: List[Dict]) -> None:
    ensure_data_dir()
    fieldnames = ["id", "url", "day"]
    with open(SPEAKING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in sorted(items, key=lambda x: x["id"]):
            writer.writerow(
                {
                    "id": it.get("id", 0),
                    "url": it.get("url", ""),
                    "day": it.get("day", ""),
                }
            )
            
def write_speaking_items(items: List[Dict]) -> None:
    _ensure_data_dir()
    fieldnames = ["id", "url", "day"]
    with open(SPEAKING_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in sorted(items, key=lambda r: r["id"]):
            writer.writerow({"id": int(it["id"]), "url": it.get("url", ""), "day": it.get("day", "")})


def delete_speaking_item(item_id: int) -> None:
    items = load_speaking_items()
    filtered = [it for it in items if it.get("id") != item_id]
    save_speaking_items(filtered)


def speaking_audio_dir() -> str:
    """Return path to the directory where speaking recordings are stored."""
    ensure_data_dir()
    return SPEAKING_AUDIO_DIR

def next_speaking_id(items: List[Dict]) -> int:
    if not items:
        return 1
    return max(int(it["id"]) for it in items) + 1