
from UserInterface import UserInterface
from UserInterface import BpmStorage
from BpmAnalizer import BpmAnalyzer
from AudioStreamer import AudioStreamer
from AbletonLink import AbletonLink
import sys
import traceback

FRAME_RATE = 11025

class InitialiseModules:
    def __init__(self):
        try:
            print("Initialisation de BpmStorage...")
            self.bpm_storage = BpmStorage()
            
            print("Initialisation d'AudioStreamer...")
            self.audio_streamer = AudioStreamer(FRAME_RATE)
            
            print("Initialisation d'AbletonLink...")
            self.ableton_link = AbletonLink()
            
            print("Initialisation de BpmAnalyzer...")
            self.bpm_analyzer = BpmAnalyzer(self, frame_rate=FRAME_RATE)
            
            print("Création de l'interface utilisateur...")
            self.ui = UserInterface(self)
            
            print("✅ Tous les modules initialisés avec succès")
            self.ui.start()
            
        except Exception as e:
            print(f"❌ Erreur fatale lors de l'initialisation: {e}")
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    try:
        InitialiseModules()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        traceback.print_exc()
        sys.exit(1)