#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import pyaudio
import queue
from collections import deque


FRAME_RATE = 11025

# Predefined BPM range options
BPM_RANGES = {
    "60–160": (60, 100),
    "130–230": (130, 100),
    "210–300": (210, 90),
}

class BpmStorage:
    """Storage for BPM values."""
    def __init__(self):
        self._float = 120.00  # default
        self._str = "***.**"  # default
        self.average_window = deque(maxlen=3)
             

class UserInterface:
    """Main UI for BPM analyzer with Tk."""

    def __init__(self, module):
        """Initialize user interface."""
        self.module = module
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
        tk.Label(dev_frame, text="Audio Device:").pack(side=tk.LEFT)
        self.device_var = tk.StringVar()
        self.combobox = ttk.Combobox(dev_frame, textvariable=self.device_var, state="readonly", width=50)
        self.combobox.pack(side=tk.LEFT, padx=(6, 6))
        tk.Button(dev_frame, text="Refresh", command=self.refresh_devices).pack(side=tk.LEFT)

        # BPM range selector
        range_frame = tk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(range_frame, text="BPM Range:").pack(side=tk.LEFT)
        self.range_var = tk.StringVar(value="60–160")
        self.range_combobox = ttk.Combobox(range_frame, textvariable=self.range_var, values=list(BPM_RANGES.keys()), state="readonly", width=20)
        self.range_combobox.pack(side=tk.LEFT, padx=(6, 6))
        self.range_combobox.bind("<<ComboboxSelected>>", self.on_range_change)
     

        # Activate button
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
        # Flag to prevent BPM enqueueing during shutdown
        self._accepting_bpm = False
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
        """Refresh audio device list from audio streamer."""
        # Use AudioStreamer to get device names and indices to avoid
        # passing a string device name later to PyAudio (which expects an
        # integer index). AudioStreamer.available_audio_devices() returns
        # [names, indices].
        try:
            devices, indices = self.module.audio_streamer.available_audio_devices()
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
            # Only enqueue if we're accepting BPM updates (not shutting down)
            if self._accepting_bpm:
                # keep a lightweight log for debugging
                self._bpm_queue.put(value)
        except Exception:
            # If queueing fails, ignore — UI shouldn't crash because of analyzer
            pass

    def _process_bpm_queue(self):
        """Process BPM updates in Tk mainloop and display on UI."""
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
        self.root.after(500, self._process_bpm_queue)

    def _update_ableton_link_clients(self):
        """Update Ableton Link client count display periodically."""
        # Only update if accepting BPM (not shutting down)
        if self._accepting_bpm:
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

    def toggle_activate(self):
        if not self.is_active:
            self.is_active = True
            self._accepting_bpm = True  # Enable BPM updates
            self.activate_btn.config(text="Deactivate", bg=self.orig_bg, fg=self.orig_fg)
            # Use the integer device index mapped by refresh_devices()
            idx = self.get_selected_device_index()
            
            self.module.bpm_analyzer.start_run_analyzer_thread(input_device_index=idx)
        else:
            self.is_active = False
            self._accepting_bpm = False  # Disable BPM updates immediately
            # Drain the queue to remove any pending updates
            try:
                while not self._bpm_queue.empty():
                    self._bpm_queue.get_nowait()
            except Exception:
                pass
            
            self.module.bpm_analyzer.stop_run_analyzer_thread()
            if self.after_id:
                try:
                    self.root.after_cancel(self.after_id)
                except Exception:
                    pass
                self.after_id = None

            self.activate_btn.config(text="Activate", bg=self.orig_bg, fg=self.orig_fg)

            # Reset BPM and client count display
            self.set_bpm(None)
            self.bpm_var.set("***.**")
            self.ableton_clients_var.set("")

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
        """Handle BPM range change from combobox."""
        range_name = self.range_var.get()
        if range_name in BPM_RANGES:
            print(f"Selected BPM range: {range_name}")
            self.module.bpm_analyzer.change_bpm_pattern(range_name)
        else:
            print(f"Unknown BPM range: {range_name}")

