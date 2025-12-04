import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
from collections import defaultdict
import copy
import random

class SchedulingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("B2.0 Scheduling Tool")
        self.root.geometry("1600x900")

        # Claude-inspired color scheme
        self.colors = {
            'bg_dark': '#1a1a1a',
            'bg_medium': '#2a2a2a',
            'bg_light': '#3a3a3a',
            'accent': '#d4734b',
            'accent_hover': '#e38a61',
            'text_primary': '#e8e8e8',
            'text_secondary': '#b8b8b8',
            'text_muted': '#808080',
            'success': '#5eb56e',
            'warning': '#d4734b',
            'error': '#d44747',
            'border': '#4a4a4a'
        }

        # Configure root window
        self.root.configure(bg=self.colors['bg_dark'])

        # Data structures
        self.people = []  # List of person dictionaries
        self.schedule = {}  # {day: {person_name: {'start': slot_idx, 'end': slot_idx, 'hours': float}}}
        self.hours_scheduled = {}  # {person_name: hours}
        self.person_colors = {}  # {person_name: color}

        # Timeslots (actual working hours 10:00-16:30)
        self.timeslots = [
            "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "16:30"
        ]
        self.timeslot_codes = ["1011", "1112", "1213", "1314", "1415", "1516", "1617"]
        self.days = ["M", "TU", "W", "TH"]
        self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday"]

        # Configuration variables
        self.csv_file_path = None
        self.week_number = tk.StringVar(value="1")
        self.desks_available = tk.StringVar(value="2")
        self.min_shift_length = tk.StringVar(value="3")

        self.setup_styles()
        self.setup_ui()

    def setup_styles(self):
        """Setup ttk styles with Claude-inspired theme"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('.',
                       background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'],
                       fieldbackground=self.colors['bg_medium'])

        style.configure('TFrame', background=self.colors['bg_dark'])
        style.configure('TLabel', background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'])
        style.configure('TButton', background=self.colors['bg_light'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'],
                       focuscolor=self.colors['accent'])
        style.map('TButton',
                 background=[('active', self.colors['accent'])],
                 foreground=[('active', self.colors['text_primary'])])

        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text_primary'])
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover'])])

        style.configure('TEntry',
                       fieldbackground=self.colors['bg_light'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'],
                       insertcolor=self.colors['text_primary'])

        style.configure('TLabelframe', background=self.colors['bg_dark'],
                       foreground=self.colors['text_primary'],
                       bordercolor=self.colors['border'])
        style.configure('TLabelframe.Label', background=self.colors['bg_dark'],
                       foreground=self.colors['accent'])

        style.configure('TNotebook', background=self.colors['bg_dark'],
                       bordercolor=self.colors['border'])
        style.configure('TNotebook.Tab',
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_secondary'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_light'])],
                 foreground=[('selected', self.colors['accent'])])

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

    def generate_person_colors(self):
        """Generate distinct colors for each person"""
        # Predefined color palette (warm tones to match Claude theme)
        palette = [
            '#d4734b', '#e38a61', '#c95d3a', '#b85a3d',
            '#8b7355', '#a68a6d', '#7d9e7f', '#6b8e7d',
            '#7a8fa3', '#8b9eb8', '#a37d9e', '#b88ba3'
        ]

        random.shuffle(palette)

        for i, person in enumerate(self.people):
            self.person_colors[person['name']] = palette[i % len(palette)]

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

        # Generate colors for people
        self.generate_person_colors()

        # Initialize schedule and hours (new structure: person-centric)
        self.schedule = {day: {} for day in self.day_names}
        self.hours_scheduled = {person['name']: 0 for person in self.people}

        # For algorithm: track old style (slot: [people])
        self.temp_schedule = {day: {i: [] for i in range(len(self.timeslots) - 1)} for day in self.day_names}

        # Run scheduling algorithm
        self.run_scheduling_algorithm(desks, min_shift)

        # Convert temp_schedule to person-centric schedule
        self.convert_to_person_schedule(min_shift)

        # Display results
        self.display_schedule()
        self.display_hours()

    def convert_to_person_schedule(self, min_shift):
        """Convert slot-based schedule to person-based blocks"""
        for day in self.day_names:
            person_shifts = {}

            # Find continuous blocks for each person
            for person in self.people:
                person_name = person['name']
                person_slots = []

                # Find all slots this person is scheduled
                for slot_idx in range(len(self.timeslots) - 1):
                    if person_name in self.temp_schedule[day][slot_idx]:
                        person_slots.append(slot_idx)

                # If person has slots, create a block
                if person_slots:
                    start = min(person_slots)
                    end = max(person_slots) + 1
                    hours = sum(0.5 if i == 6 else 1 for i in person_slots)
                    is_short = hours < min_shift

                    person_shifts[person_name] = {
                        'start': start,
                        'end': end,
                        'hours': hours,
                        'is_short': is_short
                    }

            self.schedule[day] = person_shifts

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
        timeslot_counts = {day: {i: 0 for i in range(len(self.timeslots) - 1)} for day in self.day_names}

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
                    if not all(len(self.temp_schedule[day][idx]) < desks for idx in shift_slots):
                        continue

                    # Check if person is already scheduled this day
                    already_scheduled = any(
                        person['name'] in self.temp_schedule[day][idx]
                        for idx in range(len(self.timeslots) - 1)
                    )
                    if already_scheduled:
                        continue

                    # Calculate score (lower is better)
                    # Prioritize equal distribution
                    total_in_slots = sum(timeslot_counts[day][idx] for idx in shift_slots)
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
            self.temp_schedule[day][slot_idx].append(person['name'])
            timeslot_counts[day][slot_idx] += 1

        self.hours_scheduled[person['name']] += shift['hours']
        person_shifts[person['name']].append(shift)

    def fill_remaining_with_short_shifts(self, desks, min_shift, timeslot_counts):
        """Try to fill empty slots with short shifts as last resort"""
        for day in self.day_names:
            day_code = self.days[self.day_names.index(day)]

            for slot_idx in range(len(self.timeslots) - 1):
                while len(self.temp_schedule[day][slot_idx]) < desks:
                    # Find someone available for this specific slot
                    assigned = False

                    for person in sorted(self.people,
                                       key=lambda p: self.hours_scheduled[p['name']]):

                        # Check if already scheduled this day
                        already_scheduled = any(
                            person['name'] in self.temp_schedule[day][i]
                            for i in range(len(self.timeslots) - 1)
                        )
                        if already_scheduled:
                            continue

                        # Check availability
                        slot = self.timeslots[slot_idx] + "-" + self.timeslots[slot_idx + 1]
                        if person['availability'].get(day_code, {}).get('whole_day', False) or \
                           person['availability'].get(day_code, {}).get(slot, False):

                            # Check if under max hours
                            slot_hours = 0.5 if slot_idx == 6 else 1
                            if self.hours_scheduled[person['name']] + slot_hours <= person['max_hours']:
                                self.temp_schedule[day][slot_idx].append(person['name'])
                                self.hours_scheduled[person['name']] += slot_hours
                                timeslot_counts[day][slot_idx] += 1
                                assigned = True
                                break

                    if not assigned:
                        break

    def display_schedule(self):
        # Clear previous display
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        desks = int(self.desks_available.get())
        min_shift = int(self.min_shift_length.get())

        # Create main grid
        grid_frame = tk.Frame(self.schedule_frame, bg=self.colors['bg_dark'])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Time labels column
        time_col = tk.Frame(grid_frame, bg=self.colors['bg_dark'], width=80)
        time_col.grid(row=1, column=0, sticky=(tk.N, tk.S))

        # Add time labels
        for i, time in enumerate(self.timeslots[:-1]):  # Exclude 16:30 from labels
            time_label = tk.Label(time_col, text=time,
                                font=("Consolas", 10),
                                fg=self.colors['text_muted'],
                                bg=self.colors['bg_dark'],
                                anchor=tk.E,
                                padx=10)
            time_label.grid(row=i, column=0, sticky=tk.E, pady=(0, 40))

        # Create columns for each day
        for day_idx, day in enumerate(self.day_names):
            # Day header
            day_header = tk.Frame(grid_frame, bg=self.colors['bg_medium'],
                                height=50, width=300)
            day_header.grid(row=0, column=day_idx + 1, sticky=(tk.W, tk.E),
                          padx=5, pady=(0, 10))
            day_header.grid_propagate(False)

            day_label = tk.Label(day_header, text=day,
                                font=("Consolas", 14, "bold"),
                                fg=self.colors['text_primary'],
                                bg=self.colors['bg_medium'])
            day_label.pack(expand=True)

            # Create canvas for this day's schedule
            day_canvas = tk.Canvas(grid_frame,
                                  width=300,
                                  height=500,
                                  bg=self.colors['bg_medium'],
                                  highlightthickness=1,
                                  highlightbackground=self.colors['border'])
            day_canvas.grid(row=1, column=day_idx + 1, sticky=(tk.N, tk.S),
                          padx=5)

            # Draw time grid lines
            for i in range(len(self.timeslots)):
                y = i * 60
                day_canvas.create_line(0, y, 300, y,
                                      fill=self.colors['border'],
                                      width=1)

            # Get people scheduled for this day
            if day in self.schedule:
                # Count people per timeslot for capacity tracking
                slot_counts = {i: 0 for i in range(len(self.timeslots) - 1)}

                # Draw blocks for each person
                x_offset = 5
                block_width = (300 - 10) // desks  # Divide width by number of desks

                # Group by start time for positioning
                people_shifts = list(self.schedule[day].items())
                people_shifts.sort(key=lambda x: x[1]['start'])

                # Track which "lane" each person should be in
                lanes_used = {}  # {start_slot: lane_number}

                for person_name, shift in people_shifts:
                    start_idx = shift['start']
                    end_idx = shift['end']
                    hours = shift['hours']
                    is_short = shift.get('is_short', False)

                    # Find which lane to put this person in
                    lane = 0
                    for i in range(start_idx, end_idx):
                        if i in slot_counts:
                            lane = max(lane, slot_counts[i])
                            slot_counts[i] += 1

                    # Calculate position
                    y1 = start_idx * 60 + 5
                    y2 = end_idx * 60 - 5
                    x1 = x_offset + (lane * block_width)
                    x2 = x1 + block_width - 5

                    # Get color for this person
                    color = self.person_colors.get(person_name, self.colors['accent'])

                    # Draw block
                    block = day_canvas.create_rectangle(x1, y1, x2, y2,
                                                       fill=color,
                                                       outline=self.colors['border'],
                                                       width=2)

                    # Add name label
                    name_text = person_name
                    if is_short:
                        name_text += " ⚠"

                    text_y = (y1 + y2) / 2
                    name_label = day_canvas.create_text((x1 + x2) / 2, text_y,
                                                       text=name_text,
                                                       fill=self.colors['bg_dark'],
                                                       font=("Consolas", 9, "bold"),
                                                       width=block_width - 10)

                # Check for unfilled slots
                for i in range(len(self.timeslots) - 1):
                    if slot_counts[i] < desks:
                        # Draw warning indicator
                        y = i * 60 + 30
                        day_canvas.create_text(150, y,
                                             text=f"⚠ {slot_counts[i]}/{desks}",
                                             fill=self.colors['error'],
                                             font=("Consolas", 9))

    def display_hours(self):
        # Clear previous display
        for widget in self.hours_frame.winfo_children():
            widget.destroy()

        # Create styled container
        container = tk.Frame(self.hours_frame, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create headers
        headers = ["Name", "Scheduled", "Preferred", "Agreed", "Max"]
        for col, header in enumerate(headers):
            header_label = tk.Label(container, text=header,
                                   font=("Consolas", 11, "bold"),
                                   fg=self.colors['accent'],
                                   bg=self.colors['bg_dark'])
            header_label.grid(row=0, column=col, padx=15, pady=10, sticky=tk.W)

        # Add separator
        separator = tk.Frame(container, height=2, bg=self.colors['border'])
        separator.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))

        # Sort people by name
        sorted_people = sorted(self.people, key=lambda p: p['name'])

        # Display each person's hours
        for row, person in enumerate(sorted_people, start=2):
            name = person['name']
            scheduled = self.hours_scheduled[name]
            preferred = person['preferred_hours']
            agreed = person['agreed_hours']
            max_hours = person['max_hours']

            # Color code based on hours
            if scheduled < agreed:
                color = self.colors['error']
            elif scheduled < preferred:
                color = self.colors['warning']
            else:
                color = self.colors['success']

            # Get person's color for visual consistency
            person_color = self.person_colors.get(name, self.colors['accent'])

            # Color indicator
            color_box = tk.Frame(container, width=4, height=20, bg=person_color)
            color_box.grid(row=row, column=0, sticky=tk.W, padx=(0, 5))

            # Name
            name_label = tk.Label(container, text=name,
                                 font=("Consolas", 10),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['bg_dark'])
            name_label.grid(row=row, column=0, padx=(10, 15), pady=4, sticky=tk.W)

            # Scheduled hours (colored)
            scheduled_label = tk.Label(container, text=f"{scheduled:.1f}h",
                                      font=("Consolas", 10, "bold"),
                                      fg=color,
                                      bg=self.colors['bg_dark'])
            scheduled_label.grid(row=row, column=1, padx=15, pady=4, sticky=tk.W)

            # Other hours
            for col, hours in enumerate([preferred, agreed, max_hours], start=2):
                label = tk.Label(container, text=f"{hours}h",
                               font=("Consolas", 10),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_dark'])
                label.grid(row=row, column=col, padx=15, pady=4, sticky=tk.W)


def main():
    root = tk.Tk()
    app = SchedulingTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
