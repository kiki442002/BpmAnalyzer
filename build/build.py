#!/usr/bin/env python3
"""
Build Script for BpmAnalyzer Executable
Compatible with macOS, Windows, and Linux

Usage:
    python3 build.py                 # Auto-detect platform
    python3 build.py --macos         # Build for macOS
    python3 build.py --windows       # Build for Windows
    python3 build.py --linux         # Build for Linux
    python3 build.py --all           # Build for all platforms
    python3 build.py --clean         # Clean and build
    python3 build.py --help          # Show help
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path


class BpmAnalyzerBuilder:
    """Build BpmAnalyzer executable for multiple platforms."""
    
    def __init__(self, macos=False, windows=False, linux=False, all_platforms=False, clean=False):
        """Initialize builder."""
        self.project_root = Path(__file__).parent.parent
        self.build_dir = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_cache = self.project_root / "build_cache"
        self.spec_file = self.project_root / "BpmAnalyzer.spec"
        
        self.clean = clean
        self.system = platform.system()
        
        # Determine target platforms
        if all_platforms:
            self.macos = True
            self.windows = True
            self.linux = True
        else:
            self.macos = macos
            self.windows = windows
            self.linux = linux
            
            # If none specified, build for current platform
            if not (macos or windows or linux):
                if self.system == "Darwin":
                    self.macos = True
                elif self.system == "Windows":
                    self.windows = True
                else:
                    self.linux = True
    
    def print_header(self, text):
        """Print formatted header."""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_success(self, text):
        """Print success message."""
        print(f"✅ {text}")
    
    def print_error(self, text):
        """Print error message."""
        print(f"❌ {text}")
        sys.exit(1)
    
    def print_info(self, text):
        """Print info message."""
        print(f"ℹ️  {text}")
    
    def print_warning(self, text):
        """Print warning message."""
        print(f"⚠️  {text}")
    
    def check_dependencies(self):
        """Check if all dependencies are installed."""
        self.print_header("Checking Dependencies")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.print_error(f"Python 3.8+ required, got {sys.version}")
        self.print_success(f"Python {sys.version.split()[0]}")
        
        # Check patterns folder
        patterns_dir = self.project_root / "patterns"
        if not patterns_dir.exists():
            self.print_error(f"Patterns folder not found at {patterns_dir}")
        pattern_files = list(patterns_dir.glob("*.npy"))
        if len(pattern_files) == 0:
            self.print_error(f"No .npy files found in {patterns_dir}")
        self.print_success(f"Patterns folder found with {len(pattern_files)} files")
        
        # Check PyInstaller
        try:
            import PyInstaller
            self.print_success(f"PyInstaller found")
        except ImportError:
            self.print_info("Installing PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                         check=True)
            self.print_success("PyInstaller installed")
        
        # Check other dependencies
        try:
            import numpy
            import pyaudio
            import scipy
            self.print_success("All runtime dependencies found")
        except ImportError as e:
            self.print_error(f"Missing dependency: {e}")
    
    def clean_build(self):
        """Clean previous builds."""
        self.print_header("Cleaning Previous Builds")
        
        for path in [self.dist_dir, self.build_cache, self.spec_file]:
            if isinstance(path, Path):
                if path.exists():
                    if path.is_file():
                        path.unlink()
                        self.print_success(f"Removed {path.name}")
                    else:
                        shutil.rmtree(path)
                        self.print_success(f"Removed {path.name}/")
    
    def build_for_macos(self):
        """Build for macOS."""
        if not self.macos:
            return
        
        self.print_header("Building for macOS 🍎")
        
        args = [
            "pyinstaller",
            "--onedir",
            "--windowed",
            "--collect-all=tkinter",
            "--optimize=2",
            "--name=BpmAnalyzer",
            "--hidden-import=pyaudio",
            "--hidden-import=aalink",
            "--hidden-import=scipy",
            "--hidden-import=numpy",
            "--osx-bundle-identifier=com.bpmanalyzer.app",
            "App.py"
        ]
        
        self._run_pyinstaller(args)
        self.print_success("macOS .app bundle created in dist/")
    
    def build_for_windows(self):
        """Build for Windows."""
        if not self.windows:
            return
        
        self.print_header("Building for Windows 🪟")
        
        # Check for icon
        icon_path = self.project_root / "build" / "icon.ico"
        icon_arg = f"--icon={icon_path}" if icon_path.exists() else ""
        
        args = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=BpmAnalyzer",
            "--hidden-import=pyaudio",
            "--hidden-import=aalink",
            "--hidden-import=scipy",
            "--hidden-import=numpy",
            "--collect-all=tkinter",
            "--optimize=2",
        ]
        
        if icon_arg:
            args.append(icon_arg)
        
        args.append("App.py")
        
        self._run_pyinstaller(args)
    
    def build_for_linux(self):
        """Build for Linux."""
        if not self.linux:
            return
        
        self.print_header("Building for Linux 🐧")
        
        args = [
            "pyinstaller",
            "--onefdir",
            "--windowed",
            "--name=BpmAnalyzer",
            "--hidden-import=pyaudio",
            "--hidden-import=aalink",
            "--hidden-import=scipy",
            "--hidden-import=numpy",
            "--collect-all=tkinter",
            "--optimize=2",
            "App.py"
        ]
        
        self._run_pyinstaller(args)
        
        # Optionally create AppImage for Linux
        self._create_appimage()
    
    def _run_pyinstaller(self, args):
        """Run PyInstaller with given arguments."""
        try:
            os.chdir(self.project_root)
            print(f"\n📁 Working directory: {os.getcwd()}")
            
            # Verify App.py exists
            if not os.path.exists("App.py"):
                self.print_error(f"App.py not found in {os.getcwd()}")
            
            result = subprocess.run(args, check=True)
            
            if result.returncode == 0:
                self.print_success("Executable built successfully")
            else:
                self.print_error(f"Build failed with code {result.returncode}")
        except subprocess.CalledProcessError as e:
            self.print_error(f"PyInstaller error: {e}")
    
    def _create_appimage(self):
        """Create AppImage for Linux (optional)."""
        try:
            import appimagetool
            self.print_info("Creating AppImage for Linux...")
            # Implementation would go here
        except ImportError:
            self.print_warning("appimagetool not available - skipping AppImage creation")
    
    def verify_build(self):
        """Verify the builds were successful."""
        self.print_header("Verifying Builds")
        
        builds = []
        
        if self.macos:
            exe_path = self.dist_dir / "BpmAnalyzer"
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)
                self.print_success(f"macOS:   {exe_path.name} ({size:.2f} MB)")
                
                # Check if patterns are included
                self._verify_patterns_included(exe_path)
                builds.append(("macOS", exe_path))
            else:
                self.print_warning(f"macOS executable not found")
        
        if self.windows:
            exe_path = self.dist_dir / "BpmAnalyzer.exe"
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)
                self.print_success(f"Windows: {exe_path.name} ({size:.2f} MB)")
                
                # Check if patterns are included
                self._verify_patterns_included(exe_path)
                builds.append(("Windows", exe_path))
            else:
                self.print_warning(f"Windows executable not found")
        
        if self.linux:
            exe_path = self.dist_dir / "BpmAnalyzer"
            if exe_path.exists():
                size = exe_path.stat().st_size / (1024 * 1024)
                self.print_success(f"Linux:   {exe_path.name} ({size:.2f} MB)")
                
                # Check if patterns are included
                self._verify_patterns_included(exe_path)
                builds.append(("Linux", exe_path))
            else:
                self.print_warning(f"Linux executable not found")
        
        return len(builds) > 0
    
    def _verify_patterns_included(self, exe_path):
        """Verify that pattern files are included in the executable."""
        try:
            import zipfile
            
            # PyInstaller bundles everything in a .zip inside the executable
            # For onefile builds, patterns should be in _internal/patterns/
            if exe_path.exists():
                # Check if it's a ZIP file (onefile builds are compressed)
                with zipfile.ZipFile(exe_path, 'r') as z:
                    files = z.namelist()
                    pattern_files = [f for f in files if 'pattern' in f and '.npy' in f]
                    if pattern_files:
                        self.print_success(f"  ✓ {len(pattern_files)} pattern files included in bundle")
                    else:
                        self.print_warning(f"  ⚠ Pattern files may not be included (check _internal/patterns/)")
        except Exception:
            # Not a ZIP file or other error - patterns might still be included
            self.print_info(f"  ℹ Pattern verification skipped (executable is not ZIP format)")
    
    def cleanup(self):
        """Clean up build cache."""
        self.print_header("Cleaning Build Cache")
        
        cache_dirs = [
            self.project_root / "build_cache",
            self.project_root / "build",
        ]
        
        for path in cache_dirs:
            if path.exists() and path.is_dir():
                # Don't remove the build folder we're in
                if path != self.build_dir:
                    shutil.rmtree(path)
                    self.print_success(f"Removed {path.name}/")
    
    def print_summary(self):
        """Print build summary."""
        self.print_header("Build Summary")
        
        print(f"Current Platform: {self.system}")
        print(f"Target Platforms: {', '.join([p for p, v in [('macOS', self.macos), ('Windows', self.windows), ('Linux', self.linux)] if v])}")
        print(f"\nExecutables location: {self.dist_dir}/")
        
        print("\n📦 Generated Files:")
        if self.macos:
            print(f"  🍎 {self.dist_dir}/BpmAnalyzer          (macOS)")
        if self.windows:
            print(f"  🪟 {self.dist_dir}/BpmAnalyzer.exe      (Windows)")
        if self.linux:
            print(f"  🐧 {self.dist_dir}/BpmAnalyzer          (Linux)")
        
        print("\n🚀 To Run:")
        if self.macos:
            print(f"  macOS:   {self.dist_dir}/BpmAnalyzer")
        if self.windows:
            print(f"  Windows: {self.dist_dir}\\BpmAnalyzer.exe")
        if self.linux:
            print(f"  Linux:   ./{self.dist_dir.name}/BpmAnalyzer")
        
        print()
    
    def build(self):
        """Run the complete build process."""
        print("\n" + "="*60)
        print("  BpmAnalyzer Multi-Platform Build System")
        print("="*60)
        
        try:
            self.check_dependencies()
            
            if self.clean:
                self.clean_build()
            
            # Build for each platform
            self.build_for_macos()
            self.build_for_windows()
            self.build_for_linux()
            
            if self.verify_build():
                self.cleanup()
                self.print_summary()
                self.print_success("Build complete! ✨")
            else:
                self.print_error("No builds were successful")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Build interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build BpmAnalyzer executable for multiple platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Platform Selection:
  If no platform is specified, builds for the current system.
  You can specify multiple platforms, or use --all for all platforms.

Examples:
  python3 build.py                       # Auto-detect and build
  python3 build.py --macos               # Build for macOS only
  python3 build.py --windows             # Build for Windows only
  python3 build.py --linux               # Build for Linux only
  python3 build.py --all                 # Build for all platforms
  python3 build.py --all --clean         # Clean and build all
  python3 build.py --macos --windows     # Build for macOS and Windows
        """
    )
    
    parser.add_argument("--macos", action="store_true",
                      help="Build for macOS")
    parser.add_argument("--windows", action="store_true",
                      help="Build for Windows")
    parser.add_argument("--linux", action="store_true",
                      help="Build for Linux")
    parser.add_argument("--all", action="store_true",
                      help="Build for all platforms (macOS, Windows, Linux)")
    parser.add_argument("--clean", action="store_true",
                      help="Clean previous builds before building")
    
    args = parser.parse_args()
    
    builder = BpmAnalyzerBuilder(
        macos=args.macos,
        windows=args.windows,
        linux=args.linux,
        all_platforms=args.all,
        clean=args.clean
    )
    
    builder.build()


if __name__ == "__main__":
    main()
