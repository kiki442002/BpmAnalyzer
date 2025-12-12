import pyaudio
import struct
import numpy as np
import threading
from collections import deque
import traceback
import sys


class AudioStreamer:
    def __init__(self, frame_rate: int = 11025, operating_range_seconds: int = 12):
        """Audio streamer wrapper with error handling.

        Args:
            frame_rate: sample rate in Hz (default 44100)
            operating_range_seconds: how many seconds of signal to keep in buffer
        """
        try:
            self.frame_rate = frame_rate
            self.format = pyaudio.paInt16
            self.chunk = 10240
            self.audio = pyaudio.PyAudio()
            self.signal_buffer = deque(maxlen=int(frame_rate * operating_range_seconds))
            self.operating_range_seconds = operating_range_seconds
            self.buffer_updated = threading.Event()
            self.stream = None
            print("✅ AudioStreamer initialisé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation d'AudioStreamer: {e}")
            traceback.print_exc()
            sys.exit(1)

    def audio_callback(self, in_data: bytes, frame_count, time_info, status) -> None:
        """Audio callback with error handling."""
        try:
            num_int16_values = len(in_data) // 2
            signal_buffer_int = struct.unpack(f"<{num_int16_values}h", in_data)
            self.signal_buffer.extend(signal_buffer_int)
            self.buffer_updated.set()
            print("Audio callback received data.")
            return (None, pyaudio.paContinue)
        except Exception as e:
            print(f"❌ Erreur dans le callback audio: {e}")
            traceback.print_exc()
            return (None, pyaudio.paAbort)

    def start_stream(self, input_device_index) -> None:
        """Start audio stream with error handling."""
        try:
            if input_device_index is None:
                raise ValueError("❌ Aucun appareil audio sélectionné")

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
            print(f"✅ Stream audio démarré avec l'appareil {input_device_index}")
        except Exception as e:
            print(f"❌ Erreur au démarrage du stream: {e}")
            traceback.print_exc()
            raise

    def get_buffer(self) -> np.ndarray:
        """Get audio buffer with error handling."""
        try:
            # Timeout court pour permettre un arrêt rapide
            if not self.buffer_updated.wait(timeout=0.5):
                # Pas de timeout fatal — continuer
                pass
            buffer = np.array(self.signal_buffer, dtype=np.int16)
            self.buffer_updated.clear()
            return buffer
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du buffer: {e}")
            traceback.print_exc()
            raise

    def stop_stream(self):
        """Stop audio stream with error handling."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.audio.terminate()
                self.audio = pyaudio.PyAudio()
                print("✅ Stream audio arrêté")
        except Exception as e:
            print(f"❌ Erreur à l'arrêt du stream: {e}")
            traceback.print_exc()
            raise

    def available_audio_devices(self) -> list:
        """Get available audio devices with error handling."""
        try:
            devices = []
            indices_of_devices = []
            info = self.audio.get_host_api_info_by_index(0)
            numdevices = info.get("deviceCount")
            
            if numdevices == 0:
                raise RuntimeError("Aucun appareil audio trouvé sur le système")
            
            for i in range(0, numdevices):
                try:
                    device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
                    if device_info.get("maxInputChannels") > 0:
                        device = device_info.get("name")
                        index_of_device = device_info.get("index")
                        devices.append(device)
                        indices_of_devices.append(index_of_device)
                except Exception as e:
                    print(f"⚠️  Erreur en énumérant appareil {i}: {e}")
                    continue
            
            if not devices:
                raise RuntimeError("Aucun appareil d'entrée audio trouvé")
            
            print(f"✅ {len(devices)} appareil(s) audio trouvé(s)")
            return [devices, indices_of_devices]
            
        except Exception as e:
            print(f"❌ Erreur lors de l'énumération des appareils: {e}")
            traceback.print_exc()
            raise
