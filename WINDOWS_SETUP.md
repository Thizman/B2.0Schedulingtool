# Windows Desktop Setup

Easy setup instructions for running B2.0 Scheduling Tool on Windows with the grey and green calendar icon.

## Quick Setup (Recommended)

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
   - Click "Browse..." and navigate to: `C:\path\to\B2.0Schedulingtool\scheduler_icon.png`
   - **Note:** Windows shortcuts need .ico files, so convert the PNG first (see below)
   - Or use the Windows default calendar icon for now

6. **Double-click to launch!**

### Option 2: Convert PNG to ICO (For Custom Icon)

Windows shortcuts need .ico format. You can:

**A) Use an online converter:**
1. Go to: https://convertio.co/png-ico/
2. Upload `scheduler_icon.png`
3. Download the .ico file
4. Use it in the shortcut icon settings

**B) Use Python to convert:**
Run this in your terminal:
```bash
python create_icon_windows.py
```
(I'll create this script for you)

### Option 3: Simple Batch File

1. **Navigate to the folder** in File Explorer:
   ```
   C:\path\to\B2.0Schedulingtool
   ```

2. **Double-click** `run_scheduler.bat` to launch

3. **Pin to Taskbar** (optional):
   - Right-click `run_scheduler.bat`
   - Select "Pin to taskbar"

## For WSL (Windows Subsystem for Linux) Users

If you're using WSL, use the Linux instructions from DESKTOP_SETUP.md:

```bash
# In your WSL terminal:
cd /home/user/B2.0Schedulingtool
./run_scheduler.sh
```

Or copy the .desktop file to your WSL desktop:
```bash
cp B2_Scheduler.desktop ~/Desktop/
chmod +x ~/Desktop/B2_Scheduler.desktop
```

## Troubleshooting

**Python not found:**
- Make sure Python is installed: Open Command Prompt and type `python --version`
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"

**Script won't run:**
- Right-click the .bat file → "Run as administrator"
- Or open Command Prompt in the folder and run: `python scheduler.py`

**No icon showing:**
- Windows shortcuts require .ico format (not .png)
- Use the PNG to ICO converter method above
- Or use a Windows default icon temporarily

## Quick Launch Commands

Open Command Prompt or PowerShell in the application folder and run:

**Command Prompt:**
```cmd
python scheduler.py
```

**PowerShell:**
```powershell
python scheduler.py
```

**Silent mode (no console window):**
```cmd
pythonw scheduler.py
```
Or double-click: `run_scheduler_silent.vbs`
