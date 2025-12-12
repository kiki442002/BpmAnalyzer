import pyaudio
import struct
import numpy as np
import threading
from collections import deque


class AudioStreamer:
    def __init__(self, frame_rate: int = 11025, operating_range_seconds: int = 12):
        """Audio streamer wrapper.

        Args:
            frame_rate: sample rate in Hz (default 44100)
            operating_range_seconds: how many seconds of signal to keep in buffer
        """
        self.frame_rate = frame_rate
        self.format = pyaudio.paInt16
        self.chunk = 10240
        self.audio = pyaudio.PyAudio()
        self.signal_buffer = deque(maxlen=int(frame_rate * operating_range_seconds))
        self.operating_range_seconds = operating_range_seconds
        self.buffer_updated = threading.Event()
        self.stream = None

    def audio_callback(self, in_data: bytes, frame_count, time_info, status) -> None:
        num_int16_values = len(in_data) // 2
        signal_buffer_int = struct.unpack(f"<{num_int16_values}h", in_data)
        self.signal_buffer.extend(signal_buffer_int)
        self.buffer_updated.set()
        print("Audio callback received data.")
        return (None, pyaudio.paContinue)

    def start_stream(self, input_device_index) -> None:
        self.stream = self.audio.open(
            format=self.format,
            channels=1,
            rate=self.frame_rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=input_device_index,
            stream_callback=self.audio_callback,
            start=False,
        )
        self.stream.start_stream()

    def get_buffer(self) -> np.ndarray:
        self.buffer_updated.wait()
        buffer = np.array(self.signal_buffer, dtype=np.int16)
        self.buffer_updated.clear()
        return buffer

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def available_audio_devices(self) -> list:
        devices = []
        indices_of_devices = []
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get("deviceCount")
        for i in range(0, numdevices):
            if (
                self.audio.get_device_info_by_host_api_device_index(0, i).get(
                    "maxInputChannels"
                )
            ) > 0:
                device = self.audio.get_device_info_by_host_api_device_index(0, i).get(
                    "name"
                )
                index_of_device = self.audio.get_device_info_by_host_api_device_index(
                    0, i
                ).get("index")
                devices.append(device)
                indices_of_devices.append(index_of_device)
        return [devices, indices_of_devices]
