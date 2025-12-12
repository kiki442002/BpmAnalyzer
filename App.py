
from UserInterface import UserInterface
from UserInterface import BpmStorage
from BpmAnalizer import BpmAnalyzer
from AudioStreamer import AudioStreamer
from AbletonLink import AbletonLink

FRAME_RATE = 11025

class InitialiseModules:
    def __init__(self):
        self.bpm_storage = BpmStorage()
        self.audio_streamer = AudioStreamer(FRAME_RATE)
        self.ableton_link = AbletonLink()
        self.bpm_analyzer = BpmAnalyzer(self, frame_rate=FRAME_RATE)
        self.ui = UserInterface(self)  
        self.ui.start()


if __name__ == "__main__":
    InitialiseModules()