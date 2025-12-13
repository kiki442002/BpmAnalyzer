import aalink as link
from time import sleep

class AbletonLink:
    def __init__(self):
        # aalink.Link expects two arguments: bpm and an optional loop object.
        # Pass None for the loop to use the default behavior.
        self.link = link.Link(120.00, None)
        # Some versions of the aalink.Link object may not expose
        # `startStopSyncEnabled`. Guard the assignment to remain
        # compatible with multiple implementations.
        try:
            self.link.startStopSyncEnabled = True
        except Exception:
            # attribute not present; ignore
            pass
        # Enable flag is commonly available; set to False by default.
        try:
            self.link.enabled = False
        except Exception:
            pass

    def enable(self, enabled: bool) -> None:
        """Enable or disable the Ableton Link instance.

        Note: some aalink implementations expose an `enabled` property,
        others may require different calls. We guard against missing
        attributes to avoid crashes at runtime.
        """
        try:
            self.link.enabled = enabled
        except Exception:
            # fallback: try a setter method if present
            if hasattr(self.link, "setEnabled"):
                try:
                    self.link.setEnabled(enabled)
                except Exception:
                    pass

    def get_num_peers(self) -> int:
        """Get the number of connected Ableton Link peers."""
        return self.link.num_peers

    def set_bpm(self, bpm: float) -> None:
        """Set the BPM in Ableton Link.
        
        Try multiple approaches to set tempo depending on aalink API version.
        """
        try:
            # Approche 1: captureSessionState (newer aalink versions)
            if hasattr(self.link, 'captureSessionState'):
                s = self.link.captureSessionState()
                link_time = self.link.clock().micros()
                s.setTempo(bpm, link_time)
                self.link.commitSessionState(s)
            # Approche 2: setTempo directement
            elif hasattr(self.link, 'setTempo'):
                self.link.setTempo(bpm)
            # Approche 3: tempo property
            elif hasattr(self.link, 'tempo'):
                self.link.tempo = bpm
            else:
                print("No suitable method found to set BPM in aalink.Link")
        except Exception as e:
            print(f"Error setting BPM in Ableton Link: {e}")
