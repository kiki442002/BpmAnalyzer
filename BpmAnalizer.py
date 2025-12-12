import numpy as np
from scipy import signal



import ExtractBpmPatterns

FRAME_RATE = 11025



try:
    BPM_PATTERN_60 = np.load("./patterns/60_bpm_pattern.npy")
    BPM_PATTERN_FINE_60 = np.load("./patterns/60_bpm_pattern_fine.npy")
    BPM_PATTERN_130 = np.load("./patterns/130_bpm_pattern.npy")
    BPM_PATTERN_FINE_130 = np.load("./patterns/130_bpm_pattern_fine.npy")
    BPM_PATTERN_210 = np.load("./patterns/210_bpm_pattern.npy")
    BPM_PATTERN_FINE_210 = np.load("./patterns/210_bpm_pattern_fine.npy")
except FileNotFoundError:
    ExtractBpmPatterns.extract(FRAME_RATE)
    BPM_PATTERN_60 = np.load("./patterns/60_bpm_pattern.npy")
    BPM_PATTERN_FINE_60 = np.load("./patterns/60_bpm_pattern_fine.npy")
    BPM_PATTERN_130 = np.load("./patterns/130_bpm_pattern.npy")
    BPM_PATTERN_FINE_130 = np.load("./patterns/130_bpm_pattern_fine.npy")
    BPM_PATTERN_210 = np.load("./patterns/210_bpm_pattern.npy")
    BPM_PATTERN_FINE_210 = np.load("./patterns/210_bpm_pattern_fine.npy")
   

# BPM range parameters (can be changed dynamically)
BPM_PATTERN = BPM_PATTERN_60
BPM_PATTERN_FINE = BPM_PATTERN_FINE_60
START_BPM = 60
WIDTH = 100
COARSE_STEPS = 440
FINE_STEPS = 2200
class BpmAnalyzer:
    def search_beat_events(signal_array: np.ndarray, frame_rate: int) -> np.ndarray:
        step_size = frame_rate // 2
        events = []
        for step_start in range(0, len(signal_array), step_size):
            signal_array_window = signal_array[step_start : step_start + step_size]
            signal_array_window[signal_array_window < signal_array_window.max()] = 0
            signal_array_window[signal_array_window > 0] = 1
            event = np.argmax(signal_array_window) + step_start
            events.append(event)
        return np.array(events, dtype=np.int64)

    def bpm_container(beat_events: np.ndarray, bpm_pattern: np.ndarray, steps: int) -> list[list]:
        bpm_container = [list(np.zeros((1,), dtype=np.int64))for _ in range(beat_events.size * steps)]
        for i, beat_event in enumerate(beat_events):
            found_in_pattern = np.where(np.logical_and(bpm_pattern >= beat_event - 20, bpm_pattern <= beat_event + 20))
            for x, q in enumerate(found_in_pattern[0]):
                bpm_container[i * steps + q].append(found_in_pattern[1][x])
        return bpm_container

    def wrap_bpm_container(bpm_container: list, steps: int) -> list[list]:
        def flatten(input_list: list) -> list:
            return [item for sublist in input_list for item in sublist]

        bpm_container_wrapped = [list(np.zeros((1,), dtype=np.int64)) for _ in range(steps)]
        for i, w in enumerate(bpm_container_wrapped):
            w.extend(flatten(bpm_container[i::steps]))
            w.remove(0)
            bpm_container_wrapped[i] = list(filter(lambda num: num != 0, w))
        return bpm_container_wrapped

    def finalise_bpm_container(bpm_container_wrapped: list, steps: int) -> np.ndarray:
        bpm_container_final = np.zeros((steps, 1), dtype=np.int64)
        for i, w in enumerate(bpm_container_wrapped):
            values, counts = np.unique(w, return_counts=True)
            values = values[counts == counts.max()]
            if values[0] > 0:
                count = np.count_nonzero(w == values[0])
                bpm_container_final[i] = count
        return bpm_container_final

    def get_bpm_wrapped(bpm_container_final: np.ndarray) -> np.ndarray:
        return np.where(bpm_container_final == np.amax(bpm_container_final))

    def check_bpm_wrapped(bpm_wrapped: np.ndarray, bpm_container_final: np.ndarray) -> bool:
        count = np.count_nonzero(bpm_container_final == bpm_wrapped[0][0])
        if count > 1 or bpm_container_final[int(bpm_wrapped[0][0])] < 6:
            return 0
        else:
            return 1

    def get_bpm_pattern_fine_window(bpm_wrapped: np.ndarray) -> int:
        start = int(((bpm_wrapped[0][0] / 4) / 0.05) - 20)
        end = int(start + 40)
        return start, end

    def bpm_wrapped_to_float_str(bpm: np.ndarray, bpm_fine: np.ndarray) -> float:
        bpm_float = round(
            float((((bpm[0][0] / 4) + START_BPM-10) - 1) + (bpm_fine[0][0] * 0.05)), 2
        )
        bpm_str = format(bpm_float, ".2f")
        return bpm_float, bpm_str
    
    def change_bpm_pattern(range_key: str) -> None:
        global BPM_PATTERN, BPM_PATTERN_FINE, START_BPM
        if range_key == "60–160":
            BPM_PATTERN = BPM_PATTERN_60
            BPM_PATTERN_FINE = BPM_PATTERN_FINE_60
            START_BPM = 60
        elif range_key == "130–230":
            BPM_PATTERN = BPM_PATTERN_130
            BPM_PATTERN_FINE = BPM_PATTERN_FINE_130
            START_BPM = 130
        elif range_key == "210–300":
            BPM_PATTERN = BPM_PATTERN_210
            BPM_PATTERN_FINE = BPM_PATTERN_FINE_210
            START_BPM = 210

    def search_bpm(signal_array: np.ndarray, frame_rate: int) -> tuple:
        bpm_pattern = BPM_PATTERN
        bpm_pattern_fine = BPM_PATTERN_FINE
        beat_events = BpmAnalyzer.search_beat_events(signal_array, frame_rate)
        for switch_pattern in [440, 40]:
            bpm_container = BpmAnalyzer.bpm_container(
                beat_events, bpm_pattern, switch_pattern
            )
            bpm_container_wrapped = BpmAnalyzer.wrap_bpm_container(
                bpm_container, switch_pattern
            )
            try:
                bpm_container_final = BpmAnalyzer.finalise_bpm_container(
                    bpm_container_wrapped, switch_pattern
                )
            except ValueError:
                return 0
            bpm_wrapped = BpmAnalyzer.get_bpm_wrapped(bpm_container_final)
            if not BpmAnalyzer.check_bpm_wrapped(bpm_wrapped, bpm_container_final):
                return 0
            if switch_pattern == 440:
                start, end = BpmAnalyzer.get_bpm_pattern_fine_window(bpm_wrapped)
                bpm_pattern = bpm_pattern_fine[start:end]
                bpm_wrapped_full_range = bpm_wrapped
            else:
                bpm_wrapped_fine_range = bpm_wrapped
                return BpmAnalyzer.bpm_wrapped_to_float_str(
                    bpm_wrapped_full_range, bpm_wrapped_fine_range
                )

    def run_analyzer(modules: object) -> None:
        while not modules.threading_events.stop_analyzer.is_set():
            buffer = modules.audio_streamer.get_buffer()
            print("Analyzer received buffer.")
            buffer = bandpass_filter(buffer)
            if bpm_float_str := BpmAnalyzer.search_bpm(buffer, FRAME_RATE):
                modules.bpm_storage.average_window.append(bpm_float_str[0])
                bpm_average = round(
                    (
                        sum(modules.bpm_storage.average_window)
                        / len(modules.bpm_storage.average_window)
                    ),
                    2,
                )
                (
                    modules.bpm_storage._float,
                    modules.bpm_storage._str,
                ) = bpm_average, format(bpm_average, ".2f")
                # if UI is available, update displayed BPM
                try:
                    print("Detected BPM:", modules.bpm_storage._str)
                    if hasattr(modules, "ui") and modules.ui:
                        modules.ui.set_bpm(modules.bpm_storage._float)
                        modules.ableton_link.set_bpm(float(modules.bpm_storage._float))
                except Exception:
                    pass

      


def bandpass_filter(audio_signal, lowcut=60.0, highcut=3000.0) -> np.ndarray:
    def butter_bandpass(lowcut, highcut, fs, order=10):
            nyq = 0.5 * fs
            low = lowcut / nyq
            high = highcut / nyq
            b, a = signal.butter(order, [low, high], btype='band')
            return b, a

    def butter_bandpass_filter(data, lowcut, highcut, fs, order=10):
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y

    def _bandpass_filter(buffer):
        return butter_bandpass_filter(buffer, lowcut, highcut, FRAME_RATE, order=6)
    
    return np.apply_along_axis(_bandpass_filter, 0, audio_signal).astype('int16')
