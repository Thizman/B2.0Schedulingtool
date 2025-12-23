#!/usr/bin/env python3
"""Generate sample CSV files with different hour distributions"""

import csv
import random
from datetime import datetime

# Set seed for reproducibility
random.seed(42)

# Student names
names = [
    "Emma Johnson", "Liam Smith", "Olivia Brown", "Noah Davis", "Ava Wilson",
    "Ethan Martinez", "Sophia Anderson", "Mason Taylor", "Isabella Thomas",
    "Lucas Hall", "Mia Garcia", "Charlotte Allen", "James Young"
]

# Days and shifts
days = ["M1", "TU1", "W1", "TH1", "M2", "TU2", "W2", "TH2"]
shifts = ["0930", "1030", "1315", "1530"]

def generate_hours(mean, std_dev, num_students):
    """Generate hours using normal distribution, rounded to nearest 2"""
    import math
    hours = []

    # Generate twice as many samples to ensure good distribution
    samples = []
    for _ in range(num_students * 2):
        # Box-Muller transform for normal distribution
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        h = mean + std_dev * z
        # Round to nearest 2
        h = round(h / 2) * 2
        # Keep within reasonable bounds (at least 4, at most mean + 3*std_dev)
        h = max(4, min(h, int(mean + 3 * std_dev)))
        samples.append(h)

    # Sort samples and pick evenly distributed ones to ensure good spread
    samples.sort()
    step = len(samples) / num_students
    for i in range(num_students):
        idx = int(i * step)
        hours.append(samples[idx])

    return hours

def generate_availability():
    """Generate random availability pattern"""
    # Bias towards having availability (70% chance)
    return random.random() < 0.7

def create_csv(filename, preferred_hours_list):
    """Create a CSV file with the given preferred hours"""
    with open(filename, 'w', newline='') as f:
        # Build header
        header = ['name', 'agreed hours per 2 weeks', 'max hours per 2 weeks', 'preferred hours per 2 weeks']
        for day in days:
            for shift in shifts:
                header.append(f"{day}{shift}")

        writer = csv.writer(f)
        writer.writerow(header)

        # Write student data
        for i, name in enumerate(names):
            preferred = preferred_hours_list[i]
            # Agreed hours: slightly higher than preferred (add 0-4 hours)
            agreed = preferred + random.choice([0, 2, 2, 4])
            # Max hours: higher than agreed (add 2-6 hours)
            max_hours = agreed + random.choice([2, 4, 4, 6])

            row = [name, agreed, max_hours, preferred]

            # Generate availability for each shift
            for day in days:
                for shift in shifts:
                    row.append('1' if generate_availability() else '0')

            writer.writerow(row)

# Generate the three CSVs
print("Generating sample CSV files...")

# CSV 1: Mean 10h, SD 2h
hours1 = generate_hours(10, 2, len(names))
create_csv('/home/user/B2.0Schedulingtool/sample_mean10_sd2.csv', hours1)
print(f"Created sample_mean10_sd2.csv (mean={sum(hours1)/len(hours1):.1f}, std≈2)")

# CSV 2: Mean 8h, SD 2h
hours2 = generate_hours(8, 2, len(names))
create_csv('/home/user/B2.0Schedulingtool/sample_mean8_sd2.csv', hours2)
print(f"Created sample_mean8_sd2.csv (mean={sum(hours2)/len(hours2):.1f}, std≈2)")

# CSV 3: Mean 10h, SD 4h
hours3 = generate_hours(10, 4, len(names))
create_csv('/home/user/B2.0Schedulingtool/sample_mean10_sd4.csv', hours3)
print(f"Created sample_mean10_sd4.csv (mean={sum(hours3)/len(hours3):.1f}, std≈4)")

print("\nAll CSV files created successfully!")
