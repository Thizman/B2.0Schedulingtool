import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
from collections import defaultdict
import copy

class SchedulingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("B2.0 Scheduling Tool")
        self.root.geometry("1400x900")

        # Data structures
        self.people = []  # List of person dictionaries
        self.schedule = {}  # {day: {timeslot: [person_names]}}
        self.hours_scheduled = {}  # {person_name: hours}

        # Timeslots (actual working hours 10:00-16:30)
        self.timeslots = [
            "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-16:30"
        ]
        self.timeslot_codes = ["1011", "1112", "1213", "1314", "1415", "1516", "1617"]
        self.days = ["M", "TU", "W", "TH"]
        self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday"]

        # Configuration variables
        self.csv_file_path = None
        self.week_number = tk.StringVar(value="1")
        self.desks_available = tk.StringVar(value="2")
        self.min_shift_length = tk.StringVar(value="3")

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Top section - File and Configuration
        self.setup_config_section(main_frame)

        # Middle section - Week info
        self.setup_week_section(main_frame)

        # Bottom section - Schedule and Hours display
        self.setup_display_section(main_frame)

    def setup_config_section(self, parent):
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # CSV File selection
        ttk.Label(config_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.file_label = ttk.Label(config_frame, text="No file selected", foreground="red")
        self.file_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Button(config_frame, text="Browse", command=self.load_csv).grid(row=0, column=2, padx=5)

        # Desks available
        ttk.Label(config_frame, text="Desks Available:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.desks_available, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)

        # Min shift length
        ttk.Label(config_frame, text="Min Shift Length (hours):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.min_shift_length, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)

        # Generate schedule button
        ttk.Button(config_frame, text="Generate Schedule", command=self.generate_schedule,
                   style="Accent.TButton").grid(row=3, column=0, columnspan=3, pady=10)

    def setup_week_section(self, parent):
        week_frame = ttk.LabelFrame(parent, text="Week Information", padding="10")
        week_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Week number input
        ttk.Label(week_frame, text="Week Number:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(week_frame, textvariable=self.week_number, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Button(week_frame, text="Update", command=self.update_week_display).grid(row=0, column=2, padx=5)

        # Week display
        self.week_display = ttk.Label(week_frame, text="", font=("Arial", 12, "bold"))
        self.week_display.grid(row=1, column=0, columnspan=3, pady=10)

        self.update_week_display()

    def setup_display_section(self, parent):
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Schedule tab
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Weekly Schedule")
        self.setup_schedule_display(schedule_frame)

        # Hours tracker tab
        hours_frame = ttk.Frame(notebook)
        notebook.add(hours_frame, text="Hours Tracker")
        self.setup_hours_display(hours_frame)

    def setup_schedule_display(self, parent):
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.schedule_frame = scrollable_frame

    def setup_hours_display(self, parent):
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.hours_frame = scrollable_frame

    def update_week_display(self):
        try:
            week_num = int(self.week_number.get())
            year = datetime.now().year

            # Get the first day of the year
            jan_1 = datetime(year, 1, 1)
            # Find the first Monday
            days_to_monday = (7 - jan_1.weekday()) % 7
            if days_to_monday == 0 and jan_1.weekday() != 0:
                days_to_monday = 7
            first_monday = jan_1 + timedelta(days=days_to_monday)

            # Calculate the start of the requested week
            week_start = first_monday + timedelta(weeks=week_num - 1)
            week_end = week_start + timedelta(days=3)  # Thursday

            display_text = f"Week {week_num}\n{week_start.strftime('%B %d, %Y')} - {week_end.strftime('%B %d, %Y')}"
            self.week_display.config(text=display_text)
        except ValueError:
            self.week_display.config(text="Invalid week number")

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.csv_file_path = file_path
                self.parse_csv()
                self.file_label.config(text=file_path.split('/')[-1], foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
                self.file_label.config(text="Error loading file", foreground="red")

    def parse_csv(self):
        self.people = []

        with open(self.csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                person = {
                    'name': row['name'],
                    'agreed_hours': int(row['agreed hours per week']),
                    'max_hours': int(row['max hours per week']),
                    'preferred_hours': int(row['preferred hours per week']),
                    'availability': {}
                }

                # Parse availability columns
                for day_code in self.days:
                    person['availability'][day_code] = {}
                    for i, slot_code in enumerate(self.timeslot_codes):
                        col_name = f"{day_code}{slot_code}"
                        if col_name in row:
                            person['availability'][day_code][self.timeslots[i]] = row[col_name].lower() in ['true', '1', 'yes']

                    # Whole day availability
                    whole_day_col = f"{day_code}W"
                    if whole_day_col in row:
                        person['availability'][day_code]['whole_day'] = row[whole_day_col].lower() in ['true', '1', 'yes']

                self.people.append(person)

        messagebox.showinfo("Success", f"Loaded {len(self.people)} people from CSV")

    def generate_schedule(self):
        if not self.people:
            messagebox.showerror("Error", "Please load a CSV file first")
            return

        try:
            desks = int(self.desks_available.get())
            min_shift = int(self.min_shift_length.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for desks and min shift length")
            return

        # Initialize schedule and hours
        self.schedule = {day: {slot: [] for slot in self.timeslots} for day in self.day_names}
        self.hours_scheduled = {person['name']: 0 for person in self.people}

        # Run scheduling algorithm
        self.run_scheduling_algorithm(desks, min_shift)

        # Display results
        self.display_schedule()
        self.display_hours()

    def run_scheduling_algorithm(self, desks, min_shift):
        """
        Scheduling algorithm with priorities:
        1. Equal distribution across all timeslots
        2. Fill as many desks as possible
        3. Everyone gets at least one shift
        4. Respect minimum shift length
        5. Prioritize preferred -> agreed -> max hours
        """

        # Track how many people are in each timeslot (for equal distribution)
        timeslot_counts = {day: {slot: 0 for slot in self.timeslots} for day in self.day_names}

        # Track people who haven't been scheduled yet
        unscheduled_people = set(person['name'] for person in self.people)

        # Track continuous shifts for each person (to respect min shift length)
        person_shifts = {person['name']: [] for person in self.people}

        # Phase 1: Try to give everyone at least one shift while maintaining equal distribution
        for person in sorted(self.people, key=lambda p: p['preferred_hours'], reverse=True):
            if person['name'] not in unscheduled_people:
                continue

            best_shift = self.find_best_shift(person, desks, min_shift, timeslot_counts, person_shifts)

            if best_shift:
                self.assign_shift(person, best_shift, timeslot_counts, person_shifts)
                unscheduled_people.remove(person['name'])

        # Phase 2: Fill remaining slots, prioritizing equal distribution and preferred hours
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            assigned_something = False

            for person in sorted(self.people, key=lambda p: (
                self.hours_scheduled[p['name']] < p['preferred_hours'],
                p['preferred_hours'] - self.hours_scheduled[p['name']],
                self.hours_scheduled[p['name']] < p['agreed_hours'],
                self.hours_scheduled[p['name']] < p['max_hours']
            ), reverse=True):

                # Check if person can work more hours
                if self.hours_scheduled[person['name']] >= person['max_hours']:
                    continue

                # Find the best available shift
                best_shift = self.find_best_shift(person, desks, min_shift, timeslot_counts, person_shifts)

                if best_shift:
                    self.assign_shift(person, best_shift, timeslot_counts, person_shifts)
                    assigned_something = True

            if not assigned_something:
                break

        # Phase 3: Try to fill empty slots with short shifts if necessary
        self.fill_remaining_with_short_shifts(desks, min_shift, timeslot_counts)

    def find_best_shift(self, person, desks, min_shift, timeslot_counts, person_shifts):
        """Find the best shift for a person based on availability and current distribution"""
        best_shift = None
        best_score = float('inf')

        for day_idx, day in enumerate(self.day_names):
            day_code = self.days[day_idx]

            # Check whole day availability first
            if person['availability'].get(day_code, {}).get('whole_day', False):
                available_slots = list(range(len(self.timeslots)))
            else:
                available_slots = [
                    i for i, slot in enumerate(self.timeslots)
                    if person['availability'].get(day_code, {}).get(slot, False)
                ]

            # Try to find continuous shifts of at least min_shift hours
            for start_idx in available_slots:
                for length in range(min_shift, len(self.timeslots) + 1):
                    if start_idx + length > len(self.timeslots):
                        break

                    # Check if all slots in this range are available
                    shift_slots = list(range(start_idx, start_idx + length))
                    if not all(idx in available_slots for idx in shift_slots):
                        continue

                    # Check if all slots have room
                    if not all(len(self.schedule[day][self.timeslots[idx]]) < desks for idx in shift_slots):
                        continue

                    # Check if person is already scheduled this day
                    already_scheduled = any(
                        person['name'] in self.schedule[day][self.timeslots[idx]]
                        for idx in range(len(self.timeslots))
                    )
                    if already_scheduled:
                        continue

                    # Calculate score (lower is better)
                    # Prioritize equal distribution
                    total_in_slots = sum(timeslot_counts[day][self.timeslots[idx]] for idx in shift_slots)
                    avg_in_slots = total_in_slots / len(shift_slots)

                    # Calculate shift duration (0.5 for last slot, 1 for others)
                    shift_hours = sum(0.5 if idx == 6 else 1 for idx in shift_slots)

                    # Score: prefer filling empty slots, then prefer shifts that match preferred hours
                    score = avg_in_slots * 100 - shift_hours  # Lower count is better

                    if score < best_score:
                        best_score = score
                        best_shift = {
                            'day': day,
                            'slots': shift_slots,
                            'hours': shift_hours
                        }

        return best_shift

    def assign_shift(self, person, shift, timeslot_counts, person_shifts):
        """Assign a shift to a person"""
        day = shift['day']

        for slot_idx in shift['slots']:
            slot = self.timeslots[slot_idx]
            self.schedule[day][slot].append(person['name'])
            timeslot_counts[day][slot] += 1

        self.hours_scheduled[person['name']] += shift['hours']
        person_shifts[person['name']].append(shift)

    def fill_remaining_with_short_shifts(self, desks, min_shift, timeslot_counts):
        """Try to fill empty slots with short shifts as last resort"""
        for day in self.day_names:
            day_code = self.days[self.day_names.index(day)]

            for slot_idx, slot in enumerate(self.timeslots):
                while len(self.schedule[day][slot]) < desks:
                    # Find someone available for this specific slot
                    assigned = False

                    for person in sorted(self.people,
                                       key=lambda p: self.hours_scheduled[p['name']]):

                        # Check if already scheduled this day
                        already_scheduled = any(
                            person['name'] in self.schedule[day][s]
                            for s in self.timeslots
                        )
                        if already_scheduled:
                            continue

                        # Check availability
                        if person['availability'].get(day_code, {}).get('whole_day', False) or \
                           person['availability'].get(day_code, {}).get(slot, False):

                            # Check if under max hours
                            slot_hours = 0.5 if slot_idx == 6 else 1
                            if self.hours_scheduled[person['name']] + slot_hours <= person['max_hours']:
                                self.schedule[day][slot].append(f"{person['name']} [SHORT]")
                                self.hours_scheduled[person['name']] += slot_hours
                                timeslot_counts[day][slot] += 1
                                assigned = True
                                break

                    if not assigned:
                        break

    def display_schedule(self):
        # Clear previous display
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        desks = int(self.desks_available.get())

        # Create schedule grid
        for day_idx, day in enumerate(self.day_names):
            # Day header
            day_label = ttk.Label(self.schedule_frame, text=day,
                                 font=("Arial", 12, "bold"))
            day_label.grid(row=0, column=day_idx, padx=10, pady=5, sticky=tk.W)

            # Timeslots
            for slot_idx, slot in enumerate(self.timeslots):
                scheduled = self.schedule[day][slot]

                # Create frame for this timeslot
                slot_frame = tk.Frame(self.schedule_frame, relief=tk.RIDGE, borderwidth=2)
                slot_frame.grid(row=slot_idx + 1, column=day_idx, padx=5, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))

                # Timeslot label
                tk.Label(slot_frame, text=slot, font=("Arial", 9, "bold")).pack(anchor=tk.W)

                # Check if unfilled
                if len(scheduled) < desks:
                    slot_frame.config(bg="#ffcccc")  # Light red for unfilled
                    tk.Label(slot_frame, text=f"⚠ {len(scheduled)}/{desks} filled",
                            fg="red", bg="#ffcccc").pack(anchor=tk.W)
                else:
                    slot_frame.config(bg="#ccffcc")  # Light green for filled

                # List scheduled people
                for person_name in scheduled:
                    if "[SHORT]" in person_name:
                        tk.Label(slot_frame, text=person_name, fg="orange",
                                bg=slot_frame.cget("bg")).pack(anchor=tk.W)
                    else:
                        tk.Label(slot_frame, text=person_name,
                                bg=slot_frame.cget("bg")).pack(anchor=tk.W)

    def display_hours(self):
        # Clear previous display
        for widget in self.hours_frame.winfo_children():
            widget.destroy()

        # Create headers
        headers = ["Name", "Scheduled", "Preferred", "Agreed", "Max"]
        for col, header in enumerate(headers):
            ttk.Label(self.hours_frame, text=header, font=("Arial", 10, "bold")).grid(
                row=0, column=col, padx=10, pady=5, sticky=tk.W
            )

        # Sort people by name
        sorted_people = sorted(self.people, key=lambda p: p['name'])

        # Display each person's hours
        for row, person in enumerate(sorted_people, start=1):
            name = person['name']
            scheduled = self.hours_scheduled[name]
            preferred = person['preferred_hours']
            agreed = person['agreed_hours']
            max_hours = person['max_hours']

            # Color code based on hours
            if scheduled < agreed:
                color = "red"
            elif scheduled < preferred:
                color = "orange"
            else:
                color = "green"

            ttk.Label(self.hours_frame, text=name).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Label(self.hours_frame, text=f"{scheduled:.1f}h", foreground=color).grid(
                row=row, column=1, padx=10, pady=2, sticky=tk.W
            )
            ttk.Label(self.hours_frame, text=f"{preferred}h").grid(row=row, column=2, padx=10, pady=2, sticky=tk.W)
            ttk.Label(self.hours_frame, text=f"{agreed}h").grid(row=row, column=3, padx=10, pady=2, sticky=tk.W)
            ttk.Label(self.hours_frame, text=f"{max_hours}h").grid(row=row, column=4, padx=10, pady=2, sticky=tk.W)


def main():
    root = tk.Tk()
    app = SchedulingTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
