# ![plot](./bpm.png) BpmAnalyzer

<p align="center">
  <strong>Real-time BPM Detection and Synchronization for Live Performance</strong>
</p>

<br/>

<p align="center">
  <img src="./UI.png" alt="BpmAnalyzer Interface">
</p>

---

## 📋 Overview

**BpmAnalyzer** is a powerful real-time BPM detection application designed for live musicians, DJs, and VJs who use DAWs (Digital Audio Workstations) like Ableton Live or VJ software. It automatically detects the tempo of any audio source and synchronizes it with your equipment.

Whether you're performing with Ableton Live, controlling visual effects, or collaborating with other artists, BpmAnalyzer eliminates the need to manually set the tempo. Just point it at an audio source and let it work.

### 🎯 Key Features

- ✅ **High Accuracy**: Detects BPM with ±0.10 precision across all music genres
- ✅ **Ableton Link Integration**: Sync with Ableton Live, other DAWs, and VJ software
- ✅ **Multiple BPM Ranges**: 60-160, 130-230, and 210-300 BPM detection
- ✅ **Low-Quality Signal Support**: Works with microphone input and noisy sources
- ✅ **Multi-Platform**: macOS, Windows, and Linux support
- ✅ **Lightweight & Fast**: Minimal latency, fast startup time
- ✅ **Open Source**: Built on innovative pattern-matching algorithms

---

## 🚀 Quick Start

### Using the Pre-Built Application

#### macOS
1. Download `BpmAnalyzer.app` from releases
2. Double-click to launch
3. Select your audio device and BPM range
4. Click "Activate" to start detection

#### Windows
1. Download `BpmAnalyzer.exe` from releases
2. Double-click to run
3. Select your audio device and BPM range
4. Click "Activate" to start detection

#### Linux
1. Download `BpmAnalyzer` executable from releases
2. Run from terminal: `./BpmAnalyzer`
3. Select your audio device and BPM range
4. Click "Activate" to start detection

### From Source Code

#### Prerequisites
- Python 3.8+
- PyAudio
- NumPy
- SciPy
- aalink (Ableton Link)
- tkinter (usually included with Python)

#### Installation

```bash
# Clone or download the repository
cd BpmAnalyzer

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 App.py
```

---

## 🎚️ How to Use

### 1. **Select Audio Device**
   - Use the "Audio Device" dropdown to select your input source
   - Click "Refresh" to detect new devices

### 2. **Choose BPM Range**
   - **60–160**: For slower genres (hip-hop, R&B, house)
   - **130–230**: For faster electronic music
   - **210–300**: For very fast genres (drum and bass, hardcore)

### 3. **Activate Detection**
   - Click the "Activate" button to start BPM detection
   - The display shows the detected BPM in real-time
   - Ableton Link client count appears below

### 4. **Deactivate**
   - Click "Deactivate" to stop processing

---

## 🔗 Ableton Link Integration

BpmAnalyzer supports **Ableton Link**, allowing instant synchronization with:
- Ableton Live
- Other DAWs supporting Ableton Link
- VJ software and visual synthesizers
- Hardware instruments

The application displays the number of connected Link clients at the bottom of the interface.

---

## 💻 Building Executables

To create standalone executables for distribution:

```bash
cd build
python3 build.py --macos          # Build for macOS
python3 build.py --windows        # Build for Windows
python3 build.py --linux          # Build for Linux
python3 build.py --all --clean    # Build for all platforms
```

See [build/README.md](./build/README.md) for detailed build instructions.

---

## 📊 Technical Details

### Algorithm
BpmAnalyzer uses **pattern-matching algorithms** based on frame correlation and spectral analysis:
- Analyzes audio in real-time using a digital buffer
- Applies digital filtering (Butterworth filter)
- Matches patterns against pre-computed BPM templates
- Generates accurate BPM values with fine-tuning

### Performance
- **Latency**: ~500ms detection time
- **Accuracy**: ±0.10 BPM
- **CPU Usage**: ~5-10% on modern systems
- **Memory**: ~100-150 MB

---

## 🛠️ System Requirements

### Minimum
- **CPU**: Dual-core processor
- **RAM**: 512 MB
- **Audio**: Line-in or microphone input

### Recommended
- **CPU**: Quad-core processor
- **RAM**: 2 GB
- **Audio**: External audio interface
- **OS**: macOS 10.14+, Windows 10+, or modern Linux

---

## 🔧 Configuration

All configuration is done through the GUI. No config files needed.

### Default Settings
- Sample Rate: 11,025 Hz
- Frame Rate: 11,025 Hz
- Default BPM Range: 60–160 BPM
- Default Device: System default input

---

## 🐛 Troubleshooting

### No audio devices detected
- Check that your audio device is properly connected
- Click "Refresh" to rescan devices
- On macOS, check System Preferences > Sound

### BPM values are unstable
- Ensure a consistent audio signal
- Select the correct BPM range for your music
- Avoid sudden volume changes

### Application starts slowly
- This is normal on first launch (patterns are generated)
- Subsequent launches are faster
- On Windows with `.exe`, patterns are cached

### Cannot sync with Ableton Live
- Ensure Ableton Link is enabled in Live
- Both applications must be on the same network
- Check firewall settings

---

## 📜 License

This project is open source. See LICENSE file for details.

### Attribution

BpmAnalyzer is based on innovative BPM detection algorithms. Special thanks to the creators of the original concept and pattern-matching methodology.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

---

## 📧 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the build/README.md for compilation issues

---

## 🔄 Version History

### v1.0.0
- Initial release
- Multi-platform support (macOS, Windows, Linux)
- Ableton Link integration
- Real-time BPM detection
- Three BPM range presets
- Pattern-based detection algorithm

---

## 🚀 Future Improvements

- [ ] MIDI CC output for tempo sync
- [ ] Pitch detection alongside BPM
- [ ] Recording and analysis of detected BPM history
- [ ] GUI customization options
- [ ] Standalone plugin versions
- [ ] CLI mode for server deployment

---

**Built with ❤️ for live performers and audio professionals**
