#!/bin/bash
# Launcher script for B2.0 Scheduling Tool (Linux/Unix)

# Change to the application directory
cd "$(dirname "$0")"

# Run the scheduler
python3 scheduler.py
