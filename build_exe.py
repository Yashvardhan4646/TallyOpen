import os
import subprocess
import sys

def main():
    print("Building Standalone Executable for TallyOpen...")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "TallyOpen",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--add-data", "database;database",
        "app.py"
    ]
    
    # Note: --onedir creates a folder with the executable and its dependencies, which is faster and more reliable than --onefile.
    # The user just runs TallyOpen/TallyOpen.exe
    
    print("Running PyInstaller...")
    subprocess.check_call(cmd)
    
    print("Build complete! Look inside the 'dist/TallyOpen' folder for 'TallyOpen.exe'.")

if __name__ == "__main__":
    main()
