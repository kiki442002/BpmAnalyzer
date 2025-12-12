#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import pyaudio
import queue
from threading import Thread
from collections import deque
import threading
from threading import Thread

from AudioStreamer import AudioStreamer
from AbletonLink import AbletonLink
from BpmAnalizer import BpmAnalyzer
import ExtractBpmPatterns

FRAME_RATE = 11025

# Predefined BPM range options
BPM_RANGES = {
    "60–160": (60, 100),
    "130–230": (130, 100),
    "210–300": (210, 90),
}

class BpmStorage:
    def __init__(self):
        self._float = 120.00  # default
        self._str = "***.**"  # default
        self.average_window = deque(maxlen=3)

class InitialiseModules:
    def __init__(self):
        self.bpm_storage = BpmStorage()
        self.threading_events = ThreadingEvents()
        self.audio_streamer = AudioStreamer(FRAME_RATE)
        self.ableton_link = AbletonLink()
        self.ui = UserInterface()  
        self.ui.module = self  # Link UI to modules
        self.ui.start()

class ThreadingEvents:
    def __init__(self):
        self.stop_analyzer = threading.Event()
        self.stop_trigger_set_bpm = threading.Event()
        self.stop_update_link_button = threading.Event()
        self.stop_refresh_main_window = threading.Event()
        self.bpm_updated = threading.Event()

    def stop_threads(self) -> None:
        self.stop_analyzer.set()
        self.stop_trigger_set_bpm.set()
        self.stop_update_link_button.set()
        self.stop_refresh_main_window.set()
        
    def start_update_link_button_thread(main_window: object, modules: object) -> None:
        Thread(
            target=UserInterface.update_link_button,
            args=(main_window, modules),
        ).start()
        
        
    def start_run_analyzer_thread(modules: object) -> None:
        Thread(
            target=BpmAnalyzer.run_analyzer, args=(modules,), daemon=True
        ).start()
        

class UserInterface:
    """Minimal Tk UI exposing start() and set_bpm(value).

    The mainloop runs in a background thread so the analyzer can call set_bpm.
    """

    def __init__(self):
        self.module = None  # to be set by InitialiseModules
        self.root = tk.Tk()
        self.root.title("Ableton Link BPM Analyzer")
        self.root.geometry("735x260")

        header = tk.Frame(self.root, padx=10, pady=6)
        header.pack(fill=tk.X)

        tk.Label(header, text="Ableton Link BPM Analyzer", font=(None, 14)).pack(side=tk.LEFT)

        self.bpm_var = tk.StringVar(value="***.**")
        tk.Label(header, textvariable=self.bpm_var, font=("Helvetica", 36, "bold"), fg="#1a73e8").pack(side=tk.RIGHT)

        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(expand=True, fill=tk.BOTH)

        dev_frame = tk.Frame(frame)
        dev_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(dev_frame, text="Périphérique audio:").pack(side=tk.LEFT)
        self.device_var = tk.StringVar()
        self.combobox = ttk.Combobox(dev_frame, textvariable=self.device_var, state="readonly", width=50)
        self.combobox.pack(side=tk.LEFT, padx=(6, 6))
        tk.Button(dev_frame, text="Rafraîchir", command=self.refresh_devices).pack(side=tk.LEFT)

        # BPM range selector
        range_frame = tk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(range_frame, text="Plage BPM:").pack(side=tk.LEFT)
        self.range_var = tk.StringVar(value="60–160")
        self.range_combobox = ttk.Combobox(range_frame, textvariable=self.range_var, values=list(BPM_RANGES.keys()), state="readonly", width=20)
        self.range_combobox.pack(side=tk.LEFT, padx=(6, 6))
        self.range_combobox.bind("<<ComboboxSelected>>", self.on_range_change)
     

        # Activate button (placeholder behavior)
        self.is_active = False
        self.after_id = None
        
        # Frame for Activate button and client count below
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=(6, 6))
        
        self.activate_btn = tk.Button(button_frame, text="Activate", command=self.toggle_activate, width=12)
        self.activate_btn.pack()
        
        # Ableton Link client count display (below button)
        self.ableton_clients_var = tk.StringVar(value="")
        self.ableton_clients_label = tk.Label(button_frame, textvariable=self.ableton_clients_var, font=("Helvetica", 10, "bold"), fg="#4285F4")
        self.ableton_clients_label.pack(pady=(4, 0))

        self.orig_bg = self.activate_btn.cget("bg")
        self.orig_fg = self.activate_btn.cget("fg")

        self.refresh_devices()
        # Queue for thread-safe BPM updates from analyzer threads.
        self._bpm_queue = queue.Queue()
        # Start polling the queue in the mainloop to update the UI.
        self.root.after(500, self._process_bpm_queue)
        # Start updating Ableton Link client count
        self.root.after(500, self._update_ableton_link_clients)

    def get_audio_devices(self):
        try:
            p = pyaudio.PyAudio()
        except Exception:
            return []
        names = []
        try:
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                names.append(info.get("name", "unknown"))
        finally:
            p.terminate()
        seen = set()
        return [x for x in names if not (x in seen or seen.add(x))]

    def refresh_devices(self):
        # Use AudioStreamer to get device names and indices to avoid
        # passing a string device name later to PyAudio (which expects an
        # integer index). AudioStreamer.available_audio_devices() returns
        # [names, indices].
        try:
            devices, indices = self.audio_streamer.available_audio_devices()
        except Exception:
            devices = self.get_audio_devices()
            indices = [None] * len(devices)
        self.device_indices = indices
        self.combobox["values"] = devices
        if devices:
            self.device_var.set(devices[0])

    def set_bpm(self, value=None):
        """Thread-safe entry point called by analyzer threads.

        Instead of calling root.after from worker threads (which can fail if
        the mainloop isn't running in the same context), we enqueue the value
        and let the UI mainloop process it via _process_bpm_queue().
        """
        try:
            # keep a lightweight log for debugging
            print("UserInterface.set_bpm enqueue:", value)
            self._bpm_queue.put(value)
        except Exception:
            # If queueing fails, ignore — UI shouldn't crash because of analyzer
            pass

    def _process_bpm_queue(self):
        """Called in the Tk mainloop to drain the queue and update the label."""
        updated = False
        try:
            while not self._bpm_queue.empty():
                value = self._bpm_queue.get_nowait()
                try:
                    if value is None:
                        self.bpm_var.set("***.**")
                    else:
                        v = float(value)
                        self.bpm_var.set(f"{v:.2f}")
                    updated = True
                except Exception:
                    self.bpm_var.set("***.**")
        except Exception:
            # ignore queue errors
            pass
        # schedule next poll
        self.root.after(100, self._process_bpm_queue)

    def _update_ableton_link_clients(self):
        """Periodically update the Ableton Link client count display."""
        try:
            if hasattr(self.module, 'ableton_link') and self.module.ableton_link:
                num_clients = self.module.ableton_link.get_num_peers()
                if num_clients is not None and num_clients >= 0:
                    self.ableton_clients_var.set(str(num_clients))
                else:
                    self.ableton_clients_var.set("")
            else:
                self.ableton_clients_var.set("")
        except Exception:
            self.ableton_clients_var.set("")
        # schedule next update
        self.root.after(500, self._update_ableton_link_clients)


    def _simulate_update(self):
        import random

        if random.random() > 0.4:
            self.set_bpm(random.uniform(60, 180))
        else:
            self.set_bpm(None)
        if self.is_active:
            self.after_id = self.root.after(1000, self._simulate_update)

    def toggle_activate(self):
        if not self.is_active:
            self.is_active = True
            self.activate_btn.config(text="Deactivate", bg=self.orig_bg, fg=self.orig_fg)
            # Use the integer device index mapped by refresh_devices()
            idx = self.get_selected_device_index()
            self.module.audio_streamer.start_stream(input_device_index=idx)
            self.module.ableton_link.enable(True)
            ThreadingEvents.start_run_analyzer_thread(self.module)
        else:
            self.is_active = False
            if self.after_id:
                try:
                    self.root.after_cancel(self.after_id)
                except Exception:
                    pass
                self.after_id = None
            # Stop the audio stream if it was started.
            try:
                if hasattr(self.module.audio_streamer, "stop_stream"):
                    self.module.audio_streamer.stop_stream()
                    ThreadingEvents.stop_threads()
                    self.module.ableton_link.enable(True)
            except Exception:
                # ignore stop errors; the UI should remain responsive
                pass
            self.activate_btn.config(text="Activate", bg=self.orig_bg, fg=self.orig_fg)
            self.set_bpm(None)

    def start(self):
        self.root.mainloop()

    def get_selected_device_index(self):
        """Return the integer input_device_index for the currently selected device.

        Returns None if no device or if the selection cannot be mapped to an index.
        """
        sel = self.device_var.get()
        if not sel:
            return None
        # Find the selected name index in combobox values
        try:
            vals = list(self.combobox["values"])
            pos = vals.index(sel)
        except Exception:
            return None
        # Map to stored device indices (if available)
        try:
            idx = self.device_indices[pos]
            return int(idx) if idx is not None else None
        except Exception:
            return None

    def on_range_change(self, event=None):
        """Called when user selects a new BPM range from the combobox."""
        range_name = self.range_var.get()
        if range_name in BPM_RANGES:
            print(f"Selected BPM range: {range_name}")
            BpmAnalyzer.change_bpm_pattern(range_name)
        else:
            print(f"Unknown BPM range: {range_name}")

if __name__ == "__main__":
    InitialiseModules()

