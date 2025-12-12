# 🏗️ Build Directory - Create Multi-Platform Executables

This folder contains the tools needed to create BpmAnalyzer executables for **macOS**, **Windows**, and **Linux**.

## 📋 Contents

- `build.py` - Cross-platform Python script (🌟 **Use on all OS**)
- `requirements-build.txt` - Dependencies for building executables

## 🚀 Quick Start

### **Auto-Detection (Current Platform)**

```bash
cd build
python3 build.py
```

### **Specific Platform**

```bash
# macOS only
python3 build.py --macos

# Windows only
python3 build.py --windows

# Linux only
python3 build.py --linux
```

### **All Platforms**

```bash
python3 build.py --all
```

### **With Cleanup**

```bash
python3 build.py --all --clean
python3 build.py --macos --clean
```

## 📦 Prerequisites

Install build dependencies:

```bash
pip install -r requirements-build.txt
```

Or manually:

```bash
pip install pyinstaller
```

## 📍 Output

Executables are generated in: `../dist/`

```
dist/
├── BpmAnalyzer           (macOS & Linux)
└── BpmAnalyzer.exe       (Windows)
```

## 🎯 Complete Examples

### Build for macOS only
```bash
python3 build.py --macos --clean
```

### Build for Windows and Linux
```bash
python3 build.py --windows --linux --clean
```

### Build for all platforms
```bash
python3 build.py --all --clean
```

## ⚙️ Running the Builds

### macOS
```bash
../dist/BpmAnalyzer
```

### Windows
```bash
..\dist\BpmAnalyzer.exe
```

### Linux
```bash
../dist/BpmAnalyzer
chmod +x ../dist/BpmAnalyzer  # Make executable if needed
```

## 📦 Bundle Contents

Executables include **automatically**:

✅ **All Python dependencies** (numpy, pyaudio, scipy, aalink)  
✅ **Complete Tkinter interface**  
✅ **Built-in pattern generator**  

### BPM Patterns

Pattern files (`60_bpm_pattern.npy`, `130_bpm_pattern.npy`, `210_bpm_pattern.npy`, etc.) are **automatically generated on first launch** in the data directory of your system:

- **macOS**: `~/Library/Application Support/BpmAnalyzer/patterns/`
- **Windows**: `%APPDATA%/BpmAnalyzer/patterns/`
- **Linux**: `~/.local/share/BpmAnalyzer/patterns/`

No external files needed! The bundle generates patterns once and reuses them on subsequent launches.

## 📊 Architecture

- **macOS**: Apple Silicon + Intel (native architecture)
- **Windows**: 32/64-bit compatible
- **Linux**: x86_64

## 🔧 Customization

Edit `build.py` to:
- Add an icon (place `icon.ico` or `icon.png` in this folder)
- Change the bundle name
- Add/modify hidden imports
- Include other files/folders

### Add an Icon

Place an ICO image in `build/`:
```bash
build/icon.ico
```

It will be automatically used when building for Windows.

## 🐛 Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Patterns folder not found"
Make sure you're in the `build/` folder before running the script.

### Build fails with Python error
Check that you're using Python 3.8+:
```bash
python3 --version
```

### Permission errors (Linux)
```bash
chmod +x ../dist/BpmAnalyzer
```

## ✨ Features

✅ Multi-platform support (macOS, Windows, Linux)  
✅ Standalone executables (no Python required)  
✅ Dependencies automatically bundled  
✅ Patterns generated on first run  
✅ Reusable and maintainable scripts  
✅ Automatic cache cleanup  
✅ Build verification  

## 📞 Support

For more information about PyInstaller:
https://pyinstaller.org/
