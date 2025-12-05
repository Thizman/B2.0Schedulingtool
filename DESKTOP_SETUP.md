# Desktop Application Setup

The B2.0 Scheduling Tool can now be run as a desktop application with a custom grey and green calendar icon.

## Files Created

- `scheduler_icon.png` - Large icon (256x256) for desktop launcher
- `scheduler_icon_small.png` - Small icon (32x32) for window
- `run_scheduler.sh` - Shell script to launch the application
- `B2_Scheduler.desktop` - Desktop entry file for Linux
- `create_icon.py` - Script used to generate the icons

## Setup Instructions

### Option 1: Desktop Shortcut (Quick Access)

1. **Copy the .desktop file to your Desktop:**
   ```bash
   cp /home/user/B2.0Schedulingtool/B2_Scheduler.desktop ~/Desktop/
   ```

2. **Make it trusted (if needed):**
   - Right-click on the icon on your desktop
   - Select "Allow Launching" or "Trust and Launch"
   - Or use: `gio set ~/Desktop/B2_Scheduler.desktop metadata::trusted true`

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

## Icon Features

The calendar icon features:
- **Grey background** - Professional, clean look
- **Green accents** - Calendar header and scheduled day markers
- **Calendar design** - Recognizable binding rings and grid layout
- Matches the application's color scheme

## Customization

If you want to customize the icon:
1. Edit `create_icon.py` to change colors or design
2. Run `python3 create_icon.py` to regenerate
3. The application will use the new icon on next launch

## Troubleshooting

**Icon doesn't appear:**
- Ensure the icon files exist in `/home/user/B2.0Schedulingtool/`
- Check file permissions: `ls -l scheduler_icon.png`

**Can't launch from desktop:**
- Make sure the .desktop file is executable: `chmod +x ~/Desktop/B2_Scheduler.desktop`
- Trust the launcher (see Option 1, step 2)

**Application doesn't start:**
- Check that Python 3 is installed: `python3 --version`
- Verify all dependencies are installed: `pip3 install pillow`
- Run from terminal to see error messages: `./run_scheduler.sh`
