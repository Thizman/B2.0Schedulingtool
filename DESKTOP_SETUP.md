# Desktop Application Setup

The B2.0 Scheduling Tool can now be run as a desktop application with a custom calendar icon.

## Files Included

- `calendar.ico` - Application icon (Windows .ico format)
- `run_scheduler.sh` - Shell script launcher for Linux/Unix
- `run_scheduler.bat` - Batch file launcher for Windows
- `run_scheduler_silent.vbs` - Silent launcher for Windows (no console window)
- `B2_Scheduler.desktop` - Desktop entry file for Linux

## Linux/Unix Setup

### Option 1: Desktop Shortcut (Quick Access)

1. **Copy the .desktop file to your Desktop:**
   ```bash
   cp /home/user/B2.0Schedulingtool/B2_Scheduler.desktop ~/Desktop/
   ```

2. **Make it trusted (if needed):**
   ```bash
   chmod +x ~/Desktop/B2_Scheduler.desktop
   gio set ~/Desktop/B2_Scheduler.desktop metadata::trusted true
   ```

3. **Double-click the icon to launch!**

### Option 2: Applications Menu (System Integration)

1. **Copy to applications directory:**
   ```bash
   mkdir -p ~/.local/share/applications
   cp /home/user/B2.0Schedulingtool/B2_Scheduler.desktop ~/.local/share/applications/
   ```

2. **Update desktop database:**
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

3. **Find "B2.0 Scheduler" in your applications menu**
   - Search for "B2.0 Scheduler" or "Scheduler"
   - You can also pin it to favorites/taskbar

### Option 3: Direct Launch from Terminal

```bash
cd /home/user/B2.0Schedulingtool
./run_scheduler.sh
```

Or simply:
```bash
python3 /home/user/B2.0Schedulingtool/scheduler.py
```

## Windows Setup

### Option 1: Desktop Shortcut with Icon

1. **Right-click on your Desktop** → Select "New" → "Shortcut"

2. **Enter the location:**
   ```
   C:\Windows\System32\pythonw.exe "C:\path\to\B2.0Schedulingtool\scheduler.py"
   ```
   *(Replace `C:\path\to\` with the actual path to your folder)*

3. **Click "Next"** and name it: `B2.0 Scheduler`

4. **Click "Finish"**

5. **Add the icon:**
   - Right-click the new shortcut → Select "Properties"
   - Click "Change Icon..." button
   - Click "Browse..." and navigate to: `C:\path\to\B2.0Schedulingtool\calendar.ico`
   - Click OK

6. **Double-click to launch!**

### Option 2: Simple Batch File

1. **Navigate to the folder** in File Explorer:
   ```
   C:\path\to\B2.0Schedulingtool
   ```

2. **Double-click** `run_scheduler.bat` to launch

3. **Pin to Taskbar** (optional):
   - Right-click `run_scheduler.bat`
   - Select "Pin to taskbar"

### Option 3: Silent Mode (No Console Window)

- **Double-click** `run_scheduler_silent.vbs` to launch without console window
- Perfect for a clean desktop experience

## For WSL (Windows Subsystem for Linux) Users

If you're using WSL, use the Linux instructions above:

```bash
cd /home/user/B2.0Schedulingtool
./run_scheduler.sh
```

Or copy the .desktop file to your WSL desktop:
```bash
cp B2_Scheduler.desktop ~/Desktop/
chmod +x ~/Desktop/B2_Scheduler.desktop
```

## Icon Information

The `calendar.ico` file is used for:
- Windows shortcuts and taskbar icons
- Linux .desktop launchers (via Icon field)
- Application window icon (titlebar)

## Troubleshooting

**Python not found:**
- Make sure Python is installed: `python3 --version` (Linux) or `python --version` (Windows)
- For Windows: Download from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

**Script won't run:**
- Linux: Ensure scripts are executable: `chmod +x run_scheduler.sh`
- Windows: Right-click the .bat file → "Run as administrator"
- Or open Command Prompt in the folder and run: `python scheduler.py`

**Icon not showing (Linux):**
- Ensure the icon file exists and has correct permissions
- Try converting .ico to .png for better Linux compatibility
- Update desktop database after changes

**Icon not showing (Windows):**
- Make sure the path in the shortcut properties is correct
- Right-click shortcut → Properties → Change Icon → Browse to calendar.ico
- Refresh desktop (F5) after changes

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- PIL/Pillow: `pip3 install pillow`

## Quick Launch Commands

**Linux/Unix:**
```bash
cd /home/user/B2.0Schedulingtool && python3 scheduler.py
```

**Windows Command Prompt:**
```cmd
cd C:\path\to\B2.0Schedulingtool
python scheduler.py
```

**Windows PowerShell:**
```powershell
cd C:\path\to\B2.0Schedulingtool
python scheduler.py
```

**Windows Silent (no console):**
```cmd
pythonw C:\path\to\B2.0Schedulingtool\scheduler.py
```

## Features

With desktop application setup, you can:
- Launch the scheduler with a single click
- Have a recognizable calendar icon in taskbar
- Pin to start menu / dock for quick access
- Launch without opening terminal/command prompt first
