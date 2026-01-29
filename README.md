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
✅ **Fixed Time Slots** - 4 predefined shifts: 9:30-10:30, 10:30-12:45, 13:15-15:30, 15:30-17:00
✅ **Mandatory Break** - Automatic 30-minute break enforcement (12:45-13:15)
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
   - Go to [python.org/downloads](https://www.python.org/downloads/)
   - Click the yellow "Download Python 3.x.x" button (get the latest version)

2. **Run the Installer:**
   - Open the downloaded file (e.g., `python-3.11.x-amd64.exe`)
   - ⚠️ **IMPORTANT:** Check the box "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete
   - Click "Close"

3. **Verify Python Installation:**
   - Open Command Prompt (Press `Win + R`, type `cmd`, press Enter)
   - Type: `python --version`
   - You should see: `Python 3.x.x`

#### Step 2: Install Git

1. **Download Git:**
   - Go to [git-scm.com/download/win](https://git-scm.com/download/win)
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
   - Go to [code.visualstudio.com](https://code.visualstudio.com/)
   - Click "Download for Windows"

2. **Run the Installer:**
   - Open the downloaded file
   - Accept the agreement
   - Keep default settings
   - **Check:** "Add to PATH"
   - Click "Install"
   - Click "Finish"

#### Step 4: Install PIL/Pillow (Python Image Library)

1. **Open Command Prompt**

2. **Install Pillow:**
   ```py -m pip install Pillow
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
1. Open the file folder, right click an empty space in the folder and click "open in terminal"
2. Run:
   ```cmd
   python scheduler.py
   ```

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
   - Verify shift codes (0930, 1030, 1315, 1530)
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
- Never violate 2-hour minimum shift length
- Respect mandatory break (12:45-13:15)
- Enforce weekly variance limits

**Soft Preferences:**
- Prefer longer shifts when rigidity is high
- Balance hours across both weeks
- Distribute people evenly across days
- Minimize understaffing warnings

### Shift Structure

**Fixed Shifts:**
- **9:30-10:30** (1 hour) - Early morning
- **10:30-12:45** (2.25 hours) - Mid-morning
- **13:15-15:30** (2.25 hours) - Mid-afternoon
- **15:30-17:00** (1.5 hours) - Late afternoon

**Mandatory Break:**
- **12:45-13:15** (30 minutes)
- No one can work through this period
- If working morning + afternoon, shown as 2 separate blocks

**Common Combinations:**
- Full morning: 9:30-12:45 (3.25 hours)
- Full afternoon: 13:15-17:00 (3.75 hours)
- Full day: 9:30-12:45 + 13:15-17:00 (7 hours with break)
- Cross-break: 10:30-12:45 + 13:15-15:30 (4.5 hours with break)

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
2. **Keep hours divisible by shift lengths** (0.25, 0.5, 0.75, 1, etc.)
3. **Ensure preferred ≤ agreed ≤ max** for each person
4. **Double-check shift codes** (0930, 1030, 1315, 1530)
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
