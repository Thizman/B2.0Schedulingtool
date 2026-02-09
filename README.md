# B2.0 Scheduling Tool

A comprehensive 2-week scheduling application for managing student shifts with fixed time slots, built with Python and Tkinter.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting the Application](#getting-the-application)
- [Setting Up the Application](#setting-up-the-application)
- [Troubleshooting](#troubleshooting)
- [Application Features](#application-features)

---

## Features

✅ **2-Week Scheduling** - Schedule across 8 days (Monday-Thursday for 2 consecutive weeks)
✅ **Fixed Time Slots** - 4 predefined shifts: 9:30-12:30, 10:30-12:30, 13:00-15:30, 13:00-17:00
✅ **Mandatory Break** - Automatic 30-minute break (12:30-13:00) between morning and afternoon
✅ **Smart Algorithm** - Priority-based scheduling with configurable rigidity
✅ **Weekly Variance Control** - Balance hours across both weeks (0-2h variance)
✅ **Visual Interface** - Clean, dark-themed GUI with color-coded warnings
✅ **Export Options** - Export to PNG or CSV with proper formatting
✅ **Desktop Application** - Run as a native app with custom icon

---

## Prerequisites

Before installing the B2.0 Scheduling Tool, you'll need to install several software components. Follow the instructions for your operating system.

### Required Software

1. **Python 3.6 or higher**
2. **Git** (for downloading the application)
3. **pip** (Python package manager - usually comes with Python)
4. (optional) A code editor of choice.
---

## Installation

### currently only explained for Windows installation

#### Step 1: Install Python

1. **Download Python:**
   - Go to the Microsoft Store app
   - Search for "Python"
   - install the newest version (version 3.13.12 as of the 9th of february 2026)

2. **Verify Python Installation:**
   - Open Command Prompt (Press `Win + R`, type `cmd`, press Enter)
   - Type: `python --version`
   - You should see: `Python 3.x.x`

#### Step 2: Install Git

1. **Download Git:**
   - Go to [git-scm.com/download/win](https://git-scm.com/download/win)
   - Click "Git for Windows/x64 Setup"
   - Download will start automatically

2. **Run the Installer:**
   - Open the downloaded file (e.g., `Git-2.x.x-64-bit.exe`)
   - Click "Next" through the installation wizard
   - Keep all default settings
   - Click "Install"
   - Click "Finish"

3. **Verify Git Installation:**
   - Open Command Prompt
   - Type: `git --version`
   - You should see: `git version 2.x.x`

#### Step 3: Install Visual Studio Code (Optional but Recommended)

1. **Download VS Code:**
   - Open the Microsoft Store app
   - Search for "vscode"
   - Click "install"
   - Note: having vscode installed is not strictly necessary, but if you want to view/edit the code, this is the easiest code editor (at least for me) to use
   - 

#### Step 4: Install PIL/Pillow (Python Image Library)

1. **Open Command Prompt**

2. **Install Pillow:**
   ```cmd
   py -m pip install Pillow
   ```

3. **Wait for installation to complete**
   - You should see: "Successfully installed pillow-x.x.x"

---

## Getting the Application

Now that you have all prerequisites installed, let's download the B2.0 Scheduling Tool.

### Step 1: Choose a Location

Decide where you want to store the application. I recommend:
-`C:\Users\YourName\Documents\SchedulingTool`

### Step 2: Clone the Repository

#### Using Terminal/Command Prompt:

**Windows:**
1. Open Command Prompt
2. Navigate to your desired location:
   ```cmd
   cd C:\Users\YourName\Documents
   ```
3. Clone the repository:
   ```cmd
   git clone https://github.com/Thizman/B2.0Schedulingtool Schedulingtool
   ```
4. Navigate into the folder:
   ```cmd
   cd B2.0Schedulingtool
   ```
5. make sure you are on the main branch:
   ```cmd
   git checkout main
   ```

## Setting Up the Application

### Step 1: Verify Files

Make sure you have these files in your folder:
- `scheduler.py` - Main application file
- `calendar.ico` - Application icon
- `run_scheduler.sh` - Linux launcher
- `run_scheduler.bat` - Windows launcher
- `run_scheduler_silent.vbs` - Windows silent launcher
- `B2_Scheduler.desktop` - Linux desktop entry
- Sample CSV files (sample_mean10_sd2.csv, etc.)

### Step 2: Test the Application

Let's make sure everything works before creating shortcuts.

**Windows:**
1. Open Command Prompt in the application folder
2. Run:
   ```cmd
   python scheduler.py
   ```

**Linux/Mac:**
1. Open Terminal in the application folder
2. Make the script executable:
   ```bash
   chmod +x run_scheduler.sh
   ```
3. Run:
   ```bash
   ./run_scheduler.sh
   ```
   Or:
   ```bash
   python3 scheduler.py
   ```

**Expected Result:**
- A window should open with the B2.0 Scheduling Tool interface
- The calendar icon should appear in the window titlebar
- If you see the interface, everything is working! 🎉

### Step 3: Test with Sample Data

1. **In the application:**
   - Click "Browse" next to "CSV File"
   - Navigate to the application folder
   - Select `sample_mean10_sd2.csv`
   - Click "Open"

2. **Generate a schedule:**
   - Adjust settings if desired (or keep defaults)
   - Click "Generate Schedule"
   - You should see the schedule appear with colored blocks

3. **Success!** Your application is working correctly.

---

## Creating a Desktop Shortcut

Now let's create a convenient desktop shortcut so you can launch the app with one click.

### Windows Desktop Shortcut

#### Method 1: Using the Shortcut Wizard

1. **Right-click on your Desktop**
   - Select "New" → "Shortcut"

2. **Enter the location:**
   - Browse to your Python installation (usually: `C:\Windows\System32\pythonw.exe`)
   - Or type the full path:
   ```
   C:\Windows\System32\pythonw.exe "C:\Users\YourName\Documents\B2.0Schedulingtool\scheduler.py"
   ```
   - Replace `YourName` with your actual username
   - Click "Next"

3. **Name your shortcut:**
   - Type: `B2.0 Scheduler`
   - Click "Finish"

4. **Add the custom icon:**
   - Right-click the new shortcut
   - Select "Properties"
   - Click "Change Icon..." button
   - Click "Browse..."
   - Navigate to: `C:\Users\YourName\Documents\B2.0Schedulingtool\calendar.ico`
   - Click "OK"
   - Click "Apply"
   - Click "OK"

5. **Done!** Double-click the shortcut to launch the app.

#### Method 2: Using the Batch File

1. **Navigate to your application folder in File Explorer**

2. **Find `run_scheduler_silent.vbs`**
   - Right-click it
   - Select "Send to" → "Desktop (create shortcut)"

3. **Rename the shortcut** (optional):
   - Right-click the desktop shortcut
   - Select "Rename"
   - Type: `B2.0 Scheduler`

4. **Add icon** (optional):
   - Right-click the shortcut → Properties
   - Click "Change Icon..."
   - Browse to `calendar.ico`
   - Click OK

---

### Linux Desktop Shortcut

#### Method 1: Using the .desktop File

1. **Open Terminal**

2. **Copy the desktop file:**
   ```bash
   cp ~/Documents/B2.0Schedulingtool/B2_Scheduler.desktop ~/Desktop/
   ```

3. **Make it executable:**
   ```bash
   chmod +x ~/Desktop/B2_Scheduler.desktop
   ```

4. **Trust the launcher** (if prompted):
   ```bash
   gio set ~/Desktop/B2_Scheduler.desktop metadata::trusted true
   ```

5. **Double-click the icon on your desktop to launch!**

#### Method 2: Add to Applications Menu

1. **Open Terminal**

2. **Copy to applications folder:**
   ```bash
   mkdir -p ~/.local/share/applications
   cp ~/Documents/B2.0Schedulingtool/B2_Scheduler.desktop ~/.local/share/applications/
   ```

3. **Update desktop database:**
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

4. **Find the app:**
   - Open your application launcher (Activities/Start Menu)
   - Search for "B2.0 Scheduler"
   - Right-click → "Add to Favorites" to pin it

---

### macOS Desktop Shortcut

#### Method 1: Create an Application

1. **Open Automator** (in Applications → Utilities)

2. **Create a new Application:**
   - Select "Application"
   - Click "Choose"

3. **Add a Run Shell Script action:**
   - In the search bar, type "Run Shell Script"
   - Drag "Run Shell Script" to the right panel
   - In the script box, enter:
   ```bash
   cd ~/Documents/B2.0Schedulingtool
   python3 scheduler.py
   ```

4. **Save the application:**
   - File → Save
   - Name: `B2.0 Scheduler`
   - Location: Desktop (or Applications folder)
   - Click "Save"

5. **Add the icon** (optional):
   - Get Info on the new app (Cmd + I)
   - Open `calendar.ico` in Preview
   - Edit → Select All (Cmd + A)
   - Edit → Copy (Cmd + C)
   - Click the small icon in Get Info window
   - Edit → Paste (Cmd + V)

---

## Usage Guide

### Loading a CSV File

1. **Click "Browse"** next to "CSV File"
2. **Select your CSV file** (see [CSV Format](#csv-format) below)
3. **File name turns green** when loaded successfully

### Configuring Settings

**Week Number:**
- Enter the starting week number (e.g., 1 for week 1+2)

**Total Hours Target:**
- Total hours needed across all people for 2 weeks
- Default: 270 hours

**Shift Preference Rigidity:**
- Slider from Flexible (0) to Strict (100)
- **Low (0-30):** Allows more 2-hour individual shifts
- **Medium (30-70):** Balanced mix of shift lengths
- **High (70-100):** Prefers full morning/afternoon shifts

**Weekly Hour Variance:**
- Slider from 0h to 2h (in 0.5h increments)
- Controls how much hours can vary between weeks
- **0h:** Strict balance (exactly 50/50 split)
- **1h:** Moderate flexibility (±1h per week)
- **2h:** Maximum flexibility (±2h per week)

**Desks Available Per Day:**
- Set the number of available desks for each day
- Week 1: Monday through Thursday
- Week 2: Monday through Thursday

### Generating a Schedule

1. **Load your CSV file**
2. **Adjust settings as needed**
3. **Click "Generate Schedule"**
4. **View results:**
   - Schedule appears in the left panel (2 weeks, 8 days)
   - Hours breakdown appears in the right panel
   - Color-coded warnings show understaffing

### Understanding the Display

**Schedule View:**
- **Week 1** (top): Monday-Thursday of first week
- **Week 2** (bottom): Monday-Thursday of second week
- **Colored blocks:** Each person has a unique color
- **Merged blocks:** Consecutive shifts shown as one block
- **Split at break:** Morning and afternoon separated by break line

**Hours View:**
- **Week 1 Hours:** Individual hours for first week
- **Week 2 Hours:** Individual hours for second week
- **Week 1 Total:** Sum for first week
- **Week 2 Total:** Sum for second week
- **Total (2 Weeks):** Combined totals
- **Color coding:**
  - 🟢 Green: At or above preferred hours
  - 🟠 Orange: Below preferred, at or above agreed
  - 🔴 Red: Below agreed hours

**Warnings:**
- ⚠️ Red: Less than 2 desks filled (critical)
- ⚠️ Yellow: 2+ desks filled but not all (moderate)

### Exporting

**Export as PNG:**
- Creates a high-resolution image of the complete schedule
- Includes both weeks and hours breakdown
- Perfect for printing or sharing

**Export as CSV:**
- Creates a formatted spreadsheet
- Columns: Date, Person, Shift Hours, Hours
- Dates grouped (shown once per day)
- Second person marked as "[responsible person]"
- Opens in Excel or any spreadsheet software

---

## Sample Data

The application includes three sample CSV files for testing:

1. **sample_mean10_sd2.csv**
   - Mean: 10 hours per week (20 total)
   - Standard deviation: 2 hours
   - Most people get 10h/week, some 8-12h, few 6-14h

2. **sample_mean8_sd2.csv**
   - Mean: 8 hours per week (16 total)
   - Standard deviation: 2 hours
   - Similar distribution, lower baseline

3. **sample_mean10_sd4.csv**
   - Mean: 10 hours per week (20 total)
   - Standard deviation: 4 hours
   - Wider spread (6-14h more common)

### CSV Format

Your CSV file must have these columns:

**Required Columns:**
- `name` - Person's full name
- `agreed hours per 2 weeks` - Agreed total hours
- `max hours per 2 weeks` - Maximum allowed hours
- `preferred hours per 2 weeks` - Preferred total hours

**Availability Columns:**
For each day (M1, TU1, W1, TH1, M2, TU2, W2, TH2) and each shift (0930, 1030, 1300, 1300F):
- Column format: `[DAY][SHIFT]` (e.g., `M10930`, `TU11030`, `M11300`, `M11300F`)
- Values: `1` (available), `0` (not available)

**Example:**
```csv
name,agreed hours per 2 weeks,max hours per 2 weeks,preferred hours per 2 weeks,M10930,M11030,M11300,M11300F,...
John Smith,20,24,20,1,1,0,1,...
Jane Doe,18,22,18,0,1,1,0,...
```

---

## Troubleshooting

### Application Won't Start

**Problem:** Double-clicking does nothing or shows an error

**Solutions:**
1. **Check Python installation:**
   ```
   python --version 
   ```

2. **Check if Python is in PATH:**
   - Windows: Open Command Prompt, type `python`
   - If it opens Microsoft Store, Python is not in PATH
   - Reinstall Python with "Add to PATH" checked

3. **Check file location:**
   - Make sure `scheduler.py` is in the correct folder
   - Check the path in your shortcut

4. **Run from terminal to see errors:**
   ```cmd
   python scheduler.py
   ```

### ModuleNotFoundError: No module named 'PIL'

**Problem:** Application crashes with PIL/Pillow error

**Solution:**
```bash
pip install pillow
```

### Icon Not Showing

- Right-click shortcut → Properties → Change Icon
- Browse to `calendar.ico` in application folder
- Click OK, Apply, OK
- Refresh desktop (F5)

### Schedule Generation Fails

**Problem:** Clicking "Generate Schedule" shows an error

**Solutions:**
1. **Check CSV file format**
   - Ensure all required columns exist
   - Check column names match exactly
   - Verify shift codes (0930, 1030, 1300, 1300F)
   - Ensure day codes (M1, TU1, W1, TH1, M2, TU2, W2, TH2)

2. **Check CSV values**
   - Hours must be numbers (not text)
   - Availability must be 1 or 0
   - No empty required fields

3. **Check total hours target**
   - Must be achievable with available people and desks
   - Reduce target if generation fails

### Export Fails

**Problem:** Export button does nothing or shows an error

**Solutions:**
1. **Generate schedule first**
   - You must generate before exporting

2. **Check file permissions**
   - Make sure you can write to the save location
   - Try saving to Desktop or Documents

3. **Check Pillow installation**
   ```bash
   pip install --upgrade pillow
   ```

### Application Crashes

**Problem:** Application closes unexpectedly

**Solutions:**
1. **Run from terminal to see error:**
   ```
   python scheduler.py
   ```

2. **Check tkinter installation:**
   - **Linux:** `sudo apt install python3-tk`
   - **Mac:** Reinstall Python from python.org

3. **Update dependencies:**
   ```bash
   pip install --upgrade pillow
   ```

---

## Application Features

### Scheduling Algorithm

**Priority Order:**
1. Everyone gets at least one shift
2. Fill to preferred hours (can exceed target)
3. Meet total hours target if possible
4. Respect rigidity parameter for shift lengths
5. Use agreed hours tier if needed
6. Use max hours tier as last resort

**Hard Constraints:**
- Never exceed desk capacity per shift
- Never exceed maximum hours per person
- Prevent conflicting overlapping shifts
- Enforce weekly variance limits

**Soft Preferences:**
- Prefer longer shifts when rigidity is high
- Balance hours across both weeks
- Distribute people evenly across days
- Minimize understaffing warnings

### Shift Structure

**Fixed Shifts:**
- **9:30-12:30** (3 hours) - Full morning shift
- **10:30-12:30** (2 hours) - Late morning shift
- **13:00-15:30** (2.5 hours) - Regular afternoon shift
- **13:00-17:00** (4 hours) - Extended afternoon shift

**Mandatory Break:**
- **12:30-13:00** (30 minutes)
- No shifts cover this time period
- Automatic break for anyone working morning + afternoon shifts

**Shift Overlap Notes:**
- Morning shifts overlap: 9:30-12:30 contains 10:30-12:30
- Afternoon shifts overlap: 13:00-17:00 contains 13:00-15:30
- A person cannot be assigned both overlapping shifts on the same day

**Common Combinations:**
- Full day (long): 9:30-12:30 + 13:00-17:00 (7 hours with 30-min break)
- Full day (regular): 9:30-12:30 + 13:00-15:30 (5.5 hours with 30-min break)
- Late start (long): 10:30-12:30 + 13:00-17:00 (6 hours with 30-min break)
- Late start (regular): 10:30-12:30 + 13:00-15:30 (4.5 hours with 30-min break)

### Color Scheme

**Interface:**
- Dark theme for reduced eye strain
- Orange accents for important elements
- Color-coded person blocks for easy identification

**Status Colors:**
- 🟢 Green: Good (target met)
- 🟠 Orange: Warning (below target)
- 🔴 Red: Critical (significantly below target or understaffed)
- 🟡 Yellow: Moderate warning (understaffed but manageable)

---

## Additional Resources

**Need Help?**
- Check the DESKTOP_SETUP.md file for detailed launcher setup
- Check the REFACTOR_SUMMARY.md for technical details
- Report issues on the GitHub repository

**Generating New Sample Data:**
```bash
python3 generate_sample_csvs.py
```

This creates 3 new sample CSV files with different distributions.

---

## System Requirements

**Minimum:**
- Python 3.6 or higher
- 2 GB RAM
- 100 MB disk space
- Screen resolution: 1366x768

**Recommended:**
- Python 3.9 or higher
- 4 GB RAM
- 200 MB disk space
- Screen resolution: 1920x1080

**Operating Systems:**
- Windows 7 or higher
- Ubuntu 18.04 or higher
- macOS 10.12 or higher

---

## Tips and Best Practices

### For Best Results:

1. **Ensure good availability:**
   - People should have availability for at least 2-3 days per week
   - Mix of morning and afternoon availability helps

2. **Set realistic targets:**
   - Total hours target should be achievable
   - Consider: (people × average hours) ≈ target

3. **Adjust rigidity based on needs:**
   - High rigidity: Fewer scheduling options but cleaner shifts
   - Low rigidity: More flexibility but potentially fragmented schedules

4. **Use weekly variance wisely:**
   - 0h: Perfect balance but harder to schedule
   - 1-2h: More flexibility, easier to meet targets

5. **Check warnings:**
   - Red warnings indicate critical understaffing
   - Try to resolve by adjusting availability or desk numbers

### CSV Preparation:

1. **Use provided samples as templates**
2. **Keep hours divisible by shift lengths** (0.5, 1, 1.5, 2, 2.5, 3, etc.)
3. **Ensure preferred ≤ agreed ≤ max** for each person
4. **Double-check shift codes** (0930, 1030, 1300, 1300F)
5. **Verify day codes** (M1, TU1, W1, TH1, M2, TU2, W2, TH2)

---

## Quick Reference Card

**Launch App:**
- Windows: Double-click desktop shortcut or `run_scheduler_silent.vbs`
- Linux: Double-click desktop icon or `./run_scheduler.sh`
- Any: `python scheduler.py` or `python3 scheduler.py`

**Generate Schedule:**
1. Load CSV → 2. Adjust settings → 3. Click Generate

**Export:**
- PNG: Full visual schedule
- CSV: Spreadsheet format with dates and hours

**Common Issues:**
- App won't start → Check Python installation and PATH
- Module error → `pip install pillow`
- CSV error → Check format matches examples

**Key Settings:**
- Rigidity: 0 (flexible) to 100 (strict)
- Variance: 0h (strict balance) to 2h (flexible)
- Target: Total hours needed for 2 weeks

---

**Enjoy scheduling with B2.0!** 📅
