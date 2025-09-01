from __future__ import annotations

import os
import time
import datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox

from ui.scrollable import ScrollableFrame
from ui.timer import TimerWidget
from storage import (
    load_speaking_items,
    write_speaking_items,
    delete_speaking_item,
    next_speaking_id,
)
from utils import center_window


SPEAKING_TIPS = """The TOEFL Speaking Section evaluates your ability to communicate your ideas clearly and effectively in spoken English. The entire section takes about 17 minutes. You will speak into a microphone, and your responses will be recorded and graded by a combination of AI and human raters.
There are 4 tasks:

- Task 1 (Independent): You will be asked to state and defend your opinion on a familiar topic. You get 15 seconds to prepare and 45 seconds to speak.
- Tasks 2 & 3 (Integrated): You will read a short passage, listen to a related audio clip (a lecture or conversation), and then summarize and connect the information from both sources. You get 30 seconds to prepare and 60 seconds to speak.
- Task 4 (Integrated): You will listen to a short academic lecture and then summarize the key points. You get 20 seconds to prepare and 60 seconds to speak.

Tips:

1. Structure Your Responses: Even for a 60-second answer, having a clear structure is crucial. For every task, follow the templates.
2. Take Effective Notes: For the integrated tasks, use your preparation time to jot down key points. A good strategy is to use a two-column chart for Task 2/3 to separate points from the reading and the listening, which helps you see the connection between them.
3. Use Transition Words: Guide the listener through your response with signposting language. Use phrases like "First of all...", "For example...", "The professor explains that...", and "In contrast..." to make your answer coherent and easy to follow.
4. Pace Yourself: Speak clearly and at a natural, steady pace. It's better to be clear and deliver a complete thought than to rush and make many mistakes. Practice with a timer to get comfortable with the 45 and 60-second time limits.
5. Don't worry about perfection: Small grammatical mistakes are acceptable. The goal is clear communication. If you make a mistake, just correct it quickly and keep going. Don't let it stop you.
"""


class SpeakingScreen(ttk.Frame):
    def __init__(self, parent: tk.Widget, on_back):
        super().__init__(parent)
        self.on_back = on_back

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Top bar: Back, Title, Actions (Tips/Templates), Timer
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for i in range(6):
            top.grid_columnconfigure(i, weight=1)

        back_btn = ttk.Button(top, text="← Back", command=self.on_back)
        back_btn.grid(row=0, column=0, sticky="w")

        title = ttk.Label(top, text="Speaking", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=1, columnspan=2, sticky="w", padx=(8, 0))

        tips_btn = ttk.Button(top, text="Speaking Tips", command=self._open_tips)
        tips_btn.grid(row=0, column=3, sticky="e", padx=(0, 8))

        templates_btn = ttk.Button(top, text="Templates", command=self._open_templates)
        templates_btn.grid(row=0, column=4, sticky="e", padx=(0, 8))

        self.timer = TimerWidget(top)
        self.timer.grid(row=0, column=5, sticky="e")

        # Scrollable table
        self.scroll = ScrollableFrame(self)
        self.scroll.grid(row=2, column=0, sticky="nsew")

        # Footer actions
        footer = ttk.Frame(self)
        footer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        footer.grid_columnconfigure(0, weight=1)
        self.add_btn = ttk.Button(footer, text="+ Add new item", command=self._add_item)
        self.add_btn.grid(row=0, column=0, sticky="e")

        # Load data and render
        self.items = load_speaking_items()
        self._render_rows()

    # ---------- UI Helpers ----------

    def _content_frame(self) -> ttk.Frame:
        """Handle ScrollableFrame API differences gracefully."""
        if hasattr(self.scroll, "content"):
            return getattr(self.scroll, "content")
        if hasattr(self.scroll, "scrollable_frame"):
            return getattr(self.scroll, "scrollable_frame")
        return self.scroll  # fallback

    def _render_rows(self):
        content = self._content_frame()
        for w in list(content.children.values()):
            w.destroy()

        # Header
        header = ttk.Frame(content, padding=(0, 0, 0, 4))
        header.grid(row=0, column=0, sticky="ew")
        for i, width in enumerate([10, 50, 20, 20, 20]):
            header.grid_columnconfigure(i, weight=1, minsize=0, uniform="cols")

        def hlabel(text, col):
            ttk.Label(header, text=text, style="Header.TLabel").grid(row=0, column=col, sticky="w", padx=4)

        hlabel("Link Number", 0)
        hlabel("Questions Link", 1)
        hlabel("Day", 2)
        hlabel("Answer", 3)
        hlabel("Delete", 4)

        # Rows
        for idx, item in enumerate(self.items, start=1):
            row = SpeakingRow(
                content,
                index=idx,
                item=item,
                on_answer=self._on_answer,
                on_delete=self._on_delete,
                on_changed=self._on_row_changed,
            )
            row.grid(row=idx, column=0, sticky="ew", pady=2)

    # ---------- Actions ----------

    def _add_item(self):
        new_id = next_speaking_id(self.items)
        today = dt.date.today().isoformat()
        new_item = {"id": new_id, "url": "", "day": today}
        self.items.append(new_item)
        write_speaking_items(self.items)
        self._render_rows()

    def _on_delete(self, item_id: int):
        if not messagebox.askyesno("Confirm Delete", "Delete this item?"):
            return
        delete_speaking_item(item_id)
        # Reload to keep IDs stable in file and UI
        self.items = load_speaking_items()
        self._render_rows()

    def _on_row_changed(self, item_id: int, url: str, day: str):
        # Update in-memory and persist
        updated = False
        for it in self.items:
            if it["id"] == item_id:
                it["url"] = url.strip()
                it["day"] = day.strip()
                updated = True
                break
        if updated:
            write_speaking_items(self.items)

    def _on_answer(self, item_id: int, url: str, day: str):
        # Save edits then open popup
        self._on_row_changed(item_id, url, day)
        AnswerPopup(self, item_id=item_id, link=url)

    def _open_tips(self):
        TipsPopup(self, "Speaking Tips", SPEAKING_TIPS)

    def _open_templates(self):
        # Placeholder popup; content will be provided later
        popup = tk.Toplevel(self)
        popup.title("Speaking Templates")
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.geometry("600x400")
        ttk.Label(popup, text="Templates (coming soon)", font=("Segoe UI", 12, "bold")).pack(pady=8)
        body = tk.Text(popup, wrap="word")
        body.insert("1.0", "You can paste your templates here later.")
        body.configure(state="disabled")
        body.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=8)


class SpeakingRow(ttk.Frame):
    def __init__(self, parent, index: int, item: dict, on_answer, on_delete, on_changed):
        super().__init__(parent)
        self.item = item
        self.on_answer = on_answer
        self.on_delete = on_delete
        self.on_changed = on_changed

        for i, width in enumerate([10, 50, 20, 20, 20]):
            self.grid_columnconfigure(i, weight=1, minsize=0, uniform="cols")

        # Link Number (incremental index, not the ID)
        ttk.Label(self, text=str(index)).grid(row=0, column=0, sticky="w", padx=4)

        # URL entry
        self.url_var = tk.StringVar(value=item.get("url", ""))
        url_entry = ttk.Entry(self, textvariable=self.url_var)
        url_entry.grid(row=0, column=1, sticky="ew", padx=4)

        # Day entry
        self.day_var = tk.StringVar(value=item.get("day", ""))
        day_entry = ttk.Entry(self, textvariable=self.day_var, width=12)
        day_entry.grid(row=0, column=2, sticky="ew", padx=4)

        # Answer button (saves any edits first)
        answer_btn = ttk.Button(
            self,
            text="Answer",
            command=lambda: self.on_answer(self.item["id"], self.url_var.get(), self.day_var.get()),
        )
        answer_btn.grid(row=0, column=3, sticky="ew", padx=4)

        # Delete button
        del_btn = ttk.Button(self, text="Delete", command=lambda: self.on_delete(self.item["id"]))
        del_btn.grid(row=0, column=4, sticky="ew", padx=4)

        # Auto-save on focus-out
        url_entry.bind("<FocusOut>", lambda e: self.on_changed(self.item["id"], self.url_var.get(), self.day_var.get()))
        day_entry.bind("<FocusOut>", lambda e: self.on_changed(self.item["id"], self.url_var.get(), self.day_var.get()))


class TipsPopup(tk.Toplevel):
    def __init__(self, parent: tk.Widget, title: str, text: str):
        super().__init__(parent)
        self.title(title)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.geometry("720x500")
        self.minsize(480, 320)

        # Header
        hdr = ttk.Frame(self, padding=8)
        hdr.pack(fill="x")
        ttk.Label(hdr, text=title, font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(hdr, text="Close", command=self.destroy).pack(side="right")

        # Body (scrollable text)
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=8, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        txt = tk.Text(body, wrap="word")
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        txt.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(body, orient="vertical", command=txt.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        txt.configure(yscrollcommand=yscroll.set)

        self.after(0, lambda: center_window(self))


class AnswerPopup(tk.Toplevel):
    """
    Popup to time, record, play, and save a response.
    Recording uses sounddevice if available; otherwise shows an error message.
    """

    def __init__(self, parent: tk.Widget, item_id: int, link: str | None = None):
        super().__init__(parent)
        self.title(f"Answer (ID {item_id})")
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.geometry("640x420")
        self.minsize(520, 360)

        self.item_id = item_id
        self.link = link or ""

        # Lazy imports to avoid hard dependency when not needed
        self._sd = None
        self._sf = None
        self._np = None
        self._in_stream = None
        self._buffer = []
        self._samplerate = 16000
        self._channels = 1
        self._dtype = "float32"
        self._has_audio = False
        self._input_devices = []
        self._input_indices = []
        self._device_cb = None
        
        # Audio timing variables
        self._recording_start_time = 0
        self._audio_duration = 0
        self._playback_start_time = 0
        self._is_playing = False
        self._playback_position = 0
        self._seeking = False
        self._playback_timer_id = None

        try:
            import sounddevice as sd  # type: ignore
            import soundfile as sf  # type: ignore
            import numpy as np  # type: ignore

            self._sd = sd
            self._sf = sf
            self._np = np
        except Exception as e:
            messagebox.showwarning(
                "Audio Not Available",
                "Audio dependencies not installed.\n\n"
                "Install with:\n"
                "  python -m pip install sounddevice soundfile\n"
                "On Debian/Ubuntu also install: sudo apt-get install libportaudio2",
            )

        # Top: Timer
        top = ttk.Frame(self, padding=(8, 8, 8, 4))
        top.pack(fill="x")
        ttk.Label(top, text="Speaking Timer", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.timer = TimerWidget(top)
        self.timer.pack(side="right")

        # Optional: input device selector (only if audio libs present)
        if self._sd is not None:
            devbar = ttk.Frame(self, padding=(8, 0, 8, 4))
            devbar.pack(fill="x")
            ttk.Label(devbar, text="Input device:").pack(side="left")
            self._device_var = tk.StringVar()
            self._device_cb = ttk.Combobox(devbar, textvariable=self._device_var, state="readonly", width=48)
            self._device_cb.pack(side="left", fill="x", expand=True, padx=6)
            ttk.Button(devbar, text="Refresh", command=self._refresh_devices).pack(side="left")
            # Populate devices and select a default
            self._refresh_devices()

        # Middle: status, time info, and audio progress bar
        mid = ttk.Frame(self, padding=8)
        mid.pack(fill="x")
        
        # Status label
        self.status_var = tk.StringVar(value="Idle. Click 'Record' to start.")
        self.status_label = ttk.Label(mid, textvariable=self.status_var)
        self.status_label.pack(anchor="w")
        
        # Audio time display
        time_frame = ttk.Frame(mid, padding=(0, 4))
        time_frame.pack(fill="x")
        
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        ttk.Label(time_frame, textvariable=self.time_var).pack(side="left")
        
        # Playback slider
        slider_frame = ttk.Frame(mid)
        slider_frame.pack(fill="x", pady=(2, 8))
        
        self.playback_slider = ttk.Scale(
            slider_frame, 
            from_=0, 
            to=100, 
            orient="horizontal",
            command=self._on_slider_move
        )
        self.playback_slider.pack(fill="x")
        self.playback_slider.state(["disabled"])

        # Buttons
        btns = ttk.Frame(self, padding=(8, 0, 8, 8))
        btns.pack(fill="x")
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)
        btns.grid_columnconfigure(2, weight=1)
        btns.grid_columnconfigure(3, weight=1)
        btns.grid_columnconfigure(4, weight=1)

        self.record_btn = ttk.Button(btns, text="Record", command=self._start_record)
        self.stop_btn = ttk.Button(btns, text="Stop", command=self._stop_record, state="disabled")
        self.play_btn = ttk.Button(btns, text="Play", command=self._play, state="disabled")
        self.save_btn = ttk.Button(btns, text="Save", command=self._save, state="disabled")
        self.transcribe_btn = ttk.Button(btns, text="Transcribe", command=self._transcribe_placeholder)

        self.record_btn.grid(row=0, column=0, sticky="ew", padx=4)
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=4)
        self.play_btn.grid(row=0, column=2, sticky="ew", padx=4)
        self.save_btn.grid(row=0, column=3, sticky="ew", padx=4)
        self.transcribe_btn.grid(row=0, column=4, sticky="ew", padx=4)

        # Bottom: link info and Close
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill="x")
        if self.link:
            ttk.Label(bottom, text=f"Link: {self.link}", wraplength=580).pack(anchor="w", pady=(0, 6))
        ttk.Button(bottom, text="Close", command=self._on_close).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(0, lambda: center_window(self))

    # ----- Recording logic -----

    def _audio_supported(self) -> bool:
        return all([self._sd, self._sf, self._np])

    def _refresh_devices(self):
        """Populate input devices into the combobox."""
        try:
            devices = self._sd.query_devices()
            input_devs = [(i, d) for i, d in enumerate(devices) if int(d.get("max_input_channels", 0)) > 0]
        except Exception as e:
            input_devs = []
        self._input_devices = input_devs
        self._input_indices = [i for i, _ in input_devs]
        labels = [f"[{i}] {d.get('name','Unknown')}" for i, d in input_devs]
        if self._device_cb is not None:
            self._device_cb["values"] = labels
            if labels:
                self._device_cb.current(0)
            else:
                self._device_cb.set("No input device")

    def _selected_device_index(self) -> int | None:
        """Return selected device index or None."""
        if not getattr(self, "_input_indices", []):
            return None
        if self._device_cb is None:
            return self._input_indices[0]
        sel = self._device_cb.current()
        if sel < 0:
            return self._input_indices[0]
        return self._input_indices[sel]

    def _start_record(self):
        if not self._audio_supported():
            messagebox.showerror("Audio", "Audio recording not available.")
            return
        if self._in_stream is not None:
            return
        dev_index = self._selected_device_index()
        if dev_index is None:
            messagebox.showerror("Audio", "No input device available.")
            return

        self._buffer.clear()
        self._has_audio = False
        
        # Reset timing info
        self._recording_start_time = time.time()
        self._update_timer()  # Start updating the timer

        def callback(indata, frames, time_info, status):
            if status:
                pass
            self._buffer.append(indata.copy())

        try:
            # Use the device's default sample rate and available channels
            info = self._sd.query_devices(dev_index)
            samplerate = int(info.get("default_samplerate") or self._samplerate)
            channels = max(1, min(self._channels, int(info.get("max_input_channels", 1))))
            self._samplerate = samplerate
            self._channels = channels

            self._in_stream = self._sd.InputStream(
                device=dev_index,
                samplerate=self._samplerate,
                channels=self._channels,
                dtype=self._dtype,
                callback=callback,
            )
            self._in_stream.start()
            self.status_var.set(f"Recording on device [{dev_index}]... Click 'Stop' to finish.")
            self.record_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.play_btn.configure(state="disabled")
            self.save_btn.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Audio", f"Failed to start recording:\n{e}")

    def _update_timer(self):
        """Update the timer display during recording or playback"""
        if self._in_stream is not None:  # Recording in progress
            elapsed = time.time() - self._recording_start_time
            self.time_var.set(f"{self._format_time(elapsed)} / Recording...")
            self.after(100, self._update_timer)
        elif self._is_playing:  # Playback in progress
            elapsed = time.time() - self._playback_start_time + self._playback_position
            if elapsed < self._audio_duration:
                self.time_var.set(f"{self._format_time(elapsed)} / {self._format_time(self._audio_duration)}")
                if not self._seeking:
                    # Update slider position only if not currently seeking
                    self.playback_slider.set((elapsed / self._audio_duration) * 100)
                self.after(100, self._update_timer)
            else:
                # Playback finished
                self._is_playing = False
                self.time_var.set(f"{self._format_time(self._audio_duration)} / {self._format_time(self._audio_duration)}")
                self.playback_slider.set(100)
                self.play_btn.configure(text="Play")
    
    def _format_time(self, seconds):
        """Format time in seconds to MM:SS format"""
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"

    def _on_slider_move(self, value):
        """Handle slider movement for seeking in audio playback"""
        if not self._has_audio:
            return
            
        self._seeking = True
        pos_pct = float(value) / 100
        pos_time = pos_pct * self._audio_duration
        self._playback_position = pos_time
        self.time_var.set(f"{self._format_time(pos_time)} / {self._format_time(self._audio_duration)}")
        
        # If we're playing, adjust the playback position
        if self._is_playing:
            self._stop_playback()
            self._start_playback_at_position(pos_time)
        
        self._seeking = False

    def _stop_record(self):
        if self._in_stream is None:
            return
        try:
            self._in_stream.stop()
            self._in_stream.close()
        finally:
            self._in_stream = None

        # Calculate recording duration
        self._audio_duration = time.time() - self._recording_start_time

        if self._buffer and self._np is not None:
            data = self._np.concatenate(self._buffer, axis=0)
            self._buffer.clear()
            self._audio_data = data  # keep in memory only
            self._has_audio = True
            
            duration_str = self._format_time(self._audio_duration)
            self.status_var.set(f"Recorded {duration_str}. You can Play or Save.")
            self.time_var.set(f"00:00 / {duration_str}")
            
            # Enable playback controls
            self.play_btn.configure(state="normal")
            self.save_btn.configure(state="normal")
            self.record_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.playback_slider.state(["!disabled"])  # Enable slider
            self.playback_slider.set(0)  # Reset slider position

    def _play(self):
        if not self._audio_supported() or not self._has_audio:
            return
        
        if self._is_playing:
            # If already playing, stop playback
            self._stop_playback()
            self.play_btn.configure(text="Play")
        else:
            # Start playback from current position
            self._start_playback_at_position(self._playback_position)
            self.play_btn.configure(text="Pause")

    def _start_playback_at_position(self, position_seconds):
        """Start playback from the specified position in seconds"""
        try:
            if position_seconds >= self._audio_duration:
                position_seconds = 0
                
            frame_position = int(position_seconds * self._samplerate)
            
            # Calculate how many frames to skip (assuming mono audio for simplicity)
            if frame_position > 0 and frame_position < len(self._audio_data):
                audio_to_play = self._audio_data[frame_position:]
            else:
                audio_to_play = self._audio_data
                
            self._sd.play(audio_to_play, self._samplerate)
            self._playback_start_time = time.time()
            self._playback_position = position_seconds
            self._is_playing = True
            
            # Start updating the timer
            self._update_timer()
            
            # Set callback for when playback finishes
            self._playback_timer_id = self.after(
                int(self._audio_duration * 1000), 
                self._on_playback_finished
            )
            
        except Exception as e:
            messagebox.showerror("Audio", f"Playback failed:\n{e}")

    def _stop_playback(self):
        """Stop the current playback"""
        if self._is_playing:
            self._sd.stop()
            self._is_playing = False
            
            # Cancel the scheduled playback finished callback
            if self._playback_timer_id is not None:
                self.after_cancel(self._playback_timer_id)
                self._playback_timer_id = None

    def _on_playback_finished(self):
        """Called when playback finishes naturally"""
        self._is_playing = False
        self._playback_position = 0
        self.play_btn.configure(text="Play")
        self.playback_slider.set(0)
        self.time_var.set(f"00:00 / {self._format_time(self._audio_duration)}")

    def _save(self):
        if not self._audio_supported() or not getattr(self, "_audio_data", None) is not None:
            return
        try:
            out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "speaking_audio")
            out_dir = os.path.normpath(out_dir)
            os.makedirs(out_dir, exist_ok=True)
            ts = time.strftime("%Y%m%d-%H%M%S")
            filename = f"speaking_{self.item_id}_{ts}.wav"
            out_path = os.path.join(out_dir, filename)

            # soundfile expects float data in range [-1,1] for float subtype; this is fine
            self._sf.write(out_path, self._audio_data, self._samplerate, subtype="PCM_16")
            messagebox.showinfo("Saved", f"Audio saved:\n{out_path}")
            # Consider clearing after save (user can re-record a new one)
            self._has_audio = False
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save audio:\n{e}")

    def _transcribe_placeholder(self):
        messagebox.showinfo("Transcribe", "Transcription will be implemented later.")

    def _on_close(self):
        # Stop any ongoing operations
        if self._in_stream is not None:
            try:
                self._in_stream.abort()
                self._in_stream.close()
            except Exception:
                pass
        
        # Stop any ongoing playback
        if self._is_playing:
            self._stop_playback()
            
        # Cancel any pending timers
        if self._playback_timer_id is not None:
            self.after_cancel(self._playback_timer_id)
            
        # If audio exists and not saved, ask confirmation
        if getattr(self, "_audio_data", None) is not None and self._has_audio:
            if not messagebox.askyesno("Discard Recording", "You have an unsaved recording. Close and discard it?"):
                return
        self.destroy()