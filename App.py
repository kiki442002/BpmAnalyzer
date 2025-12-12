
from UserInterface import UserInterface
from UserInterface import BpmStorage
from BpmAnalizer import BpmAnalyzer
from AudioStreamer import AudioStreamer
from AbletonLink import AbletonLink
import sys
import traceback

FRAME_RATE = 11025

class InitialiseModules:
    """Initialize all application modules."""
    def __init__(self):
        try:
            print("Initializing BpmStorage...")
            self.bpm_storage = BpmStorage()
            
            print("Initializing AudioStreamer...")
            self.audio_streamer = AudioStreamer(FRAME_RATE)
            
            print("Initializing AbletonLink...")
            self.ableton_link = AbletonLink()
            
            print("Initializing BpmAnalyzer...")
            self.bpm_analyzer = BpmAnalyzer(self, frame_rate=FRAME_RATE)
            
            print("Creating user interface...")
            self.ui = UserInterface(self)
            
            print("✅ All modules initialized successfully")
            self.ui.start()
            
        except Exception as e:
            print(f"❌ Fatal initialization error: {e}")
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        InitialiseModules()
    except Exception as e:
        print(f"❌ Critical error: {e}")
        traceback.print_exc()
        sys.exit(1)