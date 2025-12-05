import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
from collections import defaultdict
import copy
import random
from PIL import Image, ImageDraw, ImageFont
import io

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#2a2a2a", foreground="#e8e8e8",
                        relief=tk.SOLID, borderwidth=1,
                        font=("Consolas", 9), padx=8, pady=6)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class SchedulingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("B2.0 Scheduling Tool")
        self.root.geometry("1600x900")

        # Claude-inspired color scheme (adjusted hierarchy)
        self.colors = {
            'bg_dark': '#2a2a2a',      # Main background (day blocks)
            'bg_medium': '#3a3a3a',    # Lighter background
            'bg_light': '#4a4a4a',     # Lightest background
            'accent': '#d4734b',
            'accent_hover': '#e38a61',
            'text_primary': '#e8e8e8',
            'text_secondary': '#b8b8b8',
            'text_muted': '#808080',
            'success': '#5eb56e',
            'warning': '#d4734b',
            'error': '#d44747',
            'border': '#5a5a5a'        # Lightest grey for borders
        }

        # Track if schedule has been generated
        self.schedule_generated = False

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
        self.desks_monday = tk.StringVar(value="8")
        self.desks_tuesday = tk.StringVar(value="8")
        self.desks_wednesday = tk.StringVar(value="8")
        self.desks_thursday = tk.StringVar(value="8")
        self.min_shift_length = tk.StringVar(value="3")
        self.total_hours_target = tk.StringVar(value="135")

        self.setup_styles()
        self.setup_ui()

    def get_display_name(self, full_name):
        """Get display name: first name only, or first name + last initial if duplicate"""
        parts = full_name.split()
        first_name = parts[0] if parts else full_name

        # Check if there are other people with the same first name
        same_first_name = [p for p in self.people if p['name'].split()[0] == first_name]

        if len(same_first_name) > 1 and len(parts) > 1:
            # Add last initial
            return f"{first_name} {parts[-1][0]}."
        return first_name

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
                       foreground=self.colors['text_secondary'],
                       focuscolor='')  # Remove dotted focus outline
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_light'])],
                 foreground=[('selected', self.colors['accent'])])

    def setup_ui(self):
        # Configure grid weights for root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Create main scrollable canvas
        main_canvas = tk.Canvas(self.root, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)

        # Scrollable frame inside canvas
        self.scrollable_frame = ttk.Frame(main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows/MacOS
        main_canvas.bind_all("<Button-4>", lambda e: main_canvas.yview_scroll(-1, "units"))  # Linux
        main_canvas.bind_all("<Button-5>", lambda e: main_canvas.yview_scroll(1, "units"))  # Linux

        main_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure scrollable frame
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Top section - File and Configuration
        self.setup_config_section(self.scrollable_frame)

        # Bottom section - Schedule and Hours display (week info will be inside)
        self.setup_display_section(self.scrollable_frame)

    def setup_config_section(self, parent):
        # Create a canvas-based rounded frame for configuration
        config_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        config_container.grid(row=0, column=0, sticky=tk.W, pady=(10, 10), padx=10)

        # Canvas for rounded border (increased size to fit all inputs)
        canvas = tk.Canvas(config_container, width=700, height=280,
                          bg=self.colors['bg_dark'], highlightthickness=0)
        canvas.pack()

        # Draw rounded rectangle border
        self.draw_rounded_rect(canvas, 2, 2, 698, 278, 10,
                              fill=self.colors['bg_dark'],
                              outline=self.colors['border'], width=2)

        # Title
        canvas.create_text(20, 15, text="Configuration",
                          font=("Consolas", 11, "bold"),
                          fill=self.colors['accent'], anchor=tk.W)

        # Create frame for inputs inside canvas
        config_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        canvas.create_window(20, 40, window=config_frame, anchor=tk.NW)

        # CSV File selection
        row_y = 0
        tk.Label(config_frame, text="CSV File:",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=0, sticky=tk.W, padx=5, pady=3)
        self.file_label = tk.Label(config_frame, text="No file selected",
                                   fg=self.colors['error'], bg=self.colors['bg_dark'],
                                   font=("Consolas", 9))
        self.file_label.grid(row=row_y, column=1, columnspan=2, sticky=tk.W, padx=5)

        browse_btn = tk.Button(config_frame, text="Browse", command=self.load_csv,
                              bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                              font=("Consolas", 9), relief=tk.FLAT, padx=10, pady=3,
                              cursor="hand2")
        browse_btn.grid(row=row_y, column=3, padx=5)

        # Week number and Total hours target in same row
        row_y += 1
        tk.Label(config_frame, text="Week Number:",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=0, sticky=tk.W, padx=5, pady=3)
        tk.Entry(config_frame, textvariable=self.week_number, width=8,
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                insertbackground=self.colors['text_primary'],
                font=("Consolas", 9), relief=tk.FLAT).grid(row=row_y, column=1, sticky=tk.W, padx=5)

        tk.Label(config_frame, text="Total Hours Target:",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=2, sticky=tk.W, padx=(15, 5), pady=3)
        tk.Entry(config_frame, textvariable=self.total_hours_target, width=8,
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                insertbackground=self.colors['text_primary'],
                font=("Consolas", 9), relief=tk.FLAT).grid(row=row_y, column=3, sticky=tk.W, padx=5)

        # Min shift length
        row_y += 1
        tk.Label(config_frame, text="Min Shift Length (hours):",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=0, sticky=tk.W, padx=5, pady=3)
        tk.Entry(config_frame, textvariable=self.min_shift_length, width=8,
                bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                insertbackground=self.colors['text_primary'],
                font=("Consolas", 9), relief=tk.FLAT).grid(row=row_y, column=1, sticky=tk.W, padx=5)

        # Desks per day header
        row_y += 1
        tk.Label(config_frame, text="Desks Available Per Day:",
                bg=self.colors['bg_dark'], fg=self.colors['accent'],
                font=("Consolas", 9, "bold")).grid(row=row_y, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(10, 3))

        # Desks for each day in 2x2 grid
        row_y += 1
        desk_vars = [
            ("Monday:", self.desks_monday),
            ("Tuesday:", self.desks_tuesday),
            ("Wednesday:", self.desks_wednesday),
            ("Thursday:", self.desks_thursday)
        ]

        # Create 2x2 grid: row 0 = Monday, Tuesday; row 1 = Wednesday, Thursday
        for i, (label, var) in enumerate(desk_vars):
            grid_row = row_y + (i // 2)  # Row 0 for first 2, row 1 for last 2
            grid_col = (i % 2) * 2  # Column 0 or 2 (label), then +1 for entry

            tk.Label(config_frame, text=label,
                    bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                    font=("Consolas", 9)).grid(row=grid_row, column=grid_col, sticky=tk.W, padx=5, pady=3)
            tk.Entry(config_frame, textvariable=var, width=6,
                    bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                    insertbackground=self.colors['text_primary'],
                    font=("Consolas", 9), relief=tk.FLAT).grid(row=grid_row, column=grid_col+1, sticky=tk.W, padx=5)

        # Generate and Export buttons
        row_y += 2
        gen_btn = tk.Button(config_frame, text="Generate Schedule", command=self.generate_schedule,
                           bg=self.colors['accent'], fg=self.colors['text_primary'],
                           font=("Consolas", 10, "bold"), relief=tk.FLAT,
                           padx=15, pady=6, cursor="hand2")
        gen_btn.grid(row=row_y, column=0, columnspan=2, pady=10, sticky=tk.W)

        export_btn = tk.Button(config_frame, text="Export as PNG", command=self.export_schedule,
                              bg=self.colors['success'], fg=self.colors['text_primary'],
                              font=("Consolas", 10, "bold"), relief=tk.FLAT,
                              padx=15, pady=6, cursor="hand2")
        export_btn.grid(row=row_y, column=2, columnspan=2, pady=10, sticky=tk.W, padx=(15, 0))

        # Hover effects for buttons
        def on_enter(e, btn, color):
            btn['bg'] = color
        def on_leave(e, btn, color):
            btn['bg'] = color

        browse_btn.bind("<Enter>", lambda e: on_enter(e, browse_btn, self.colors['bg_medium']))
        browse_btn.bind("<Leave>", lambda e: on_leave(e, browse_btn, self.colors['bg_light']))
        gen_btn.bind("<Enter>", lambda e: on_enter(e, gen_btn, self.colors['accent_hover']))
        gen_btn.bind("<Leave>", lambda e: on_leave(e, gen_btn, self.colors['accent']))
        export_btn.bind("<Enter>", lambda e: on_enter(e, export_btn, '#6ec57e'))
        export_btn.bind("<Leave>", lambda e: on_leave(e, export_btn, self.colors['success']))


    def setup_display_section(self, parent):
        # Create container for side-by-side layout
        display_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        display_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(10, 20))

        # Configure grid weights
        display_container.columnconfigure(0, weight=2)  # Schedule gets more space
        display_container.columnconfigure(1, weight=1)  # Hours gets less space

        # Schedule section (left side) with scrollable canvas
        schedule_container = tk.Frame(display_container, bg=self.colors['bg_dark'])
        schedule_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Create outer canvas with rounded border for schedule
        schedule_canvas_width = 950
        schedule_canvas_height = 850
        self.schedule_canvas_border = tk.Canvas(schedule_container,
                                               width=schedule_canvas_width,
                                               height=schedule_canvas_height,
                                               bg=self.colors['bg_dark'],
                                               highlightthickness=0)
        self.schedule_canvas_border.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Draw rounded border for schedule
        self.draw_rounded_rect(self.schedule_canvas_border, 2, 2,
                              schedule_canvas_width-2, schedule_canvas_height-2, 10,
                              fill=self.colors['bg_dark'],
                              outline=self.colors['border'], width=2)

        # Create scrollable inner canvas for schedule content
        inner_canvas_width = schedule_canvas_width - 50
        inner_canvas_height = schedule_canvas_height - 40

        self.schedule_inner_canvas = tk.Canvas(self.schedule_canvas_border,
                                              bg=self.colors['bg_dark'],
                                              width=inner_canvas_width,
                                              height=inner_canvas_height,
                                              highlightthickness=0)

        schedule_scrollbar = ttk.Scrollbar(self.schedule_canvas_border,
                                          orient="vertical",
                                          command=self.schedule_inner_canvas.yview)

        # Position scrollbar on the right side
        self.schedule_canvas_border.create_window(schedule_canvas_width - 30, 20,
                                                 window=schedule_scrollbar,
                                                 width=15,
                                                 height=schedule_canvas_height - 40,
                                                 anchor=tk.NW)

        # Position inner canvas
        self.schedule_canvas_border.create_window(20, 20,
                                                 window=self.schedule_inner_canvas,
                                                 anchor=tk.NW)

        self.schedule_frame = tk.Frame(self.schedule_inner_canvas, bg=self.colors['bg_dark'])
        self.schedule_frame.bind("<Configure>",
                                lambda e: self.schedule_inner_canvas.configure(scrollregion=self.schedule_inner_canvas.bbox("all")))

        self.schedule_inner_canvas.create_window((0, 0), window=self.schedule_frame, anchor=tk.NW)
        self.schedule_inner_canvas.configure(yscrollcommand=schedule_scrollbar.set)

        # Hours section (right side) with scrollable canvas
        hours_container = tk.Frame(display_container, bg=self.colors['bg_dark'])
        hours_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create outer canvas with rounded border for hours
        hours_canvas_width = 420
        hours_canvas_height = 850
        self.hours_canvas_border = tk.Canvas(hours_container,
                                            width=hours_canvas_width,
                                            height=hours_canvas_height,
                                            bg=self.colors['bg_dark'],
                                            highlightthickness=0)
        self.hours_canvas_border.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Draw rounded border for hours
        self.draw_rounded_rect(self.hours_canvas_border, 2, 2,
                              hours_canvas_width-2, hours_canvas_height-2, 10,
                              fill=self.colors['bg_dark'],
                              outline=self.colors['border'], width=2)

        # Create scrollable inner canvas for hours content
        hours_inner_width = hours_canvas_width - 50
        hours_inner_height = hours_canvas_height - 40

        self.hours_inner_canvas = tk.Canvas(self.hours_canvas_border,
                                           bg=self.colors['bg_dark'],
                                           width=hours_inner_width,
                                           height=hours_inner_height,
                                           highlightthickness=0)

        hours_scrollbar = ttk.Scrollbar(self.hours_canvas_border,
                                       orient="vertical",
                                       command=self.hours_inner_canvas.yview)

        # Position scrollbar on the right side
        self.hours_canvas_border.create_window(hours_canvas_width - 30, 20,
                                              window=hours_scrollbar,
                                              width=15,
                                              height=hours_canvas_height - 40,
                                              anchor=tk.NW)

        # Position inner canvas
        self.hours_canvas_border.create_window(20, 20,
                                              window=self.hours_inner_canvas,
                                              anchor=tk.NW)

        self.hours_frame = tk.Frame(self.hours_inner_canvas, bg=self.colors['bg_dark'])
        self.hours_frame.bind("<Configure>",
                             lambda e: self.hours_inner_canvas.configure(scrollregion=self.hours_inner_canvas.bbox("all")))

        self.hours_inner_canvas.create_window((0, 0), window=self.hours_frame, anchor=tk.NW)
        self.hours_inner_canvas.configure(yscrollcommand=hours_scrollbar.set)

        # Show placeholder initially
        self.show_placeholder(self.schedule_frame, "Load CSV and Generate Schedule")
        self.show_placeholder(self.hours_frame, "Hours Tracker")

    def show_placeholder(self, parent, message):
        """Show a placeholder message in empty frames"""
        for widget in parent.winfo_children():
            widget.destroy()

        placeholder = tk.Label(parent, text=message,
                              font=("Consolas", 12),
                              fg=self.colors['text_muted'],
                              bg=self.colors['bg_dark'],
                              pady=50)
        placeholder.pack(expand=True)

    def get_week_display_text(self):
        """Get formatted week display text"""
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

            return f"Week {week_num}  •  {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"
        except ValueError:
            return "Invalid week number"

    def export_schedule(self):
        """Export the schedule and hours tracker as PNG"""
        if not self.schedule_generated:
            messagebox.showwarning("Warning", "Please generate a schedule first")
            return

        try:
            # Get week info for filename
            week_num = int(self.week_number.get())
            week_text = self.get_week_display_text()
            # Extract dates from week text
            import re
            dates_match = re.search(r'(\w+ \d+) - (\w+ \d+, \d+)', week_text)
            if dates_match:
                start_date = dates_match.group(1).replace(' ', '-')
                end_date = dates_match.group(2).replace(' ', '-').replace(',', '')
                filename = f"B2.0 Schedule week {week_num} ({start_date}_{end_date}).png"
            else:
                filename = f"B2.0 Schedule week {week_num}.png"

            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=filename
            )

            if not file_path:
                return

            # Create image programmatically
            self.create_export_image(file_path, week_text)

            messagebox.showinfo("Success", f"Schedule exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export schedule: {str(e)}")

    def create_export_image(self, file_path, week_text):
        """Create a professional PNG export of schedule and hours"""
        # Image dimensions
        img_width = 1400
        img_height = 1000

        # Create image with dark background
        img = Image.new('RGB', (img_width, img_height), color='#2a2a2a')
        draw = ImageDraw.Draw(img)

        try:
            # Try to load fonts
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 16)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 13)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 9)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Colors
        bg_dark = '#2a2a2a'
        bg_medium = '#3a3a3a'
        text_primary = '#e8e8e8'
        text_muted = '#808080'
        accent = '#d4734b'
        border = '#5a5a5a'
        error = '#d44747'
        success = '#5eb56e'
        warning_color = '#d4734b'

        # Draw title
        draw.text((30, 30), week_text, fill=accent, font=title_font)

        # Schedule section (left side)
        schedule_x = 30
        schedule_y = 70
        day_width = 330
        day_height = 400

        # Draw 2x2 grid of days
        positions = [(0, 0), (1, 0), (0, 1), (1, 1)]

        for idx, day in enumerate(self.day_names):
            row, col = positions[idx]
            x = schedule_x + (col * (day_width + 20))
            y = schedule_y + (row * (day_height + 20))

            # Draw day container border
            draw.rectangle([x, y, x + day_width, y + day_height],
                          outline=border, width=2)

            # Draw day header
            draw.rectangle([x, y, x + day_width, y + 35],
                          fill=bg_medium, outline=border, width=1)
            draw.text((x + 10, y + 10), day, fill=text_primary, font=header_font)

            # Get desk count for this day
            desks = self.desks_per_day[day]
            min_shift = int(self.min_shift_length.get())

            # Draw timeslots and schedule
            slot_height = 40
            time_x = x + 10
            content_start_y = y + 45

            # Count slot capacity
            slot_counts = {i: 0 for i in range(len(self.timeslots) - 1)}
            if day in self.schedule:
                for person_name, shift in self.schedule[day].items():
                    for i in range(shift['start'], shift['end']):
                        if i in slot_counts:
                            slot_counts[i] += 1

            # Draw time labels and warnings
            for i, time in enumerate(self.timeslots[:-1]):
                time_y = content_start_y + (i * slot_height)

                # Time label
                draw.text((time_x, time_y), time, fill=text_muted, font=small_font)

                # Warning if understaffed
                if slot_counts[i] < desks:
                    warning_text = f"⚠ {slot_counts[i]}/{desks}"
                    draw.text((time_x + 50, time_y), warning_text, fill=error, font=small_font)

            # Draw schedule blocks
            if day in self.schedule:
                block_width = (day_width - 120) // desks
                lanes = [[] for _ in range(desks)]

                people_shifts = list(self.schedule[day].items())
                people_shifts.sort(key=lambda x: (x[1]['start'], x[1]['end']))

                for person_name, shift in people_shifts:
                    start_idx = shift['start']
                    end_idx = shift['end']
                    is_short = shift.get('is_short', False)

                    # Find available lane
                    assigned_lane = None
                    for lane_idx in range(desks):
                        overlaps = False
                        for existing_start, existing_end in lanes[lane_idx]:
                            if not (end_idx <= existing_start or start_idx >= existing_end):
                                overlaps = True
                                break
                        if not overlaps:
                            assigned_lane = lane_idx
                            lanes[lane_idx].append((start_idx, end_idx))
                            break

                    if assigned_lane is None:
                        assigned_lane = 0

                    # Calculate position
                    block_x1 = time_x + 100 + (assigned_lane * block_width)
                    block_y1 = content_start_y + (start_idx * slot_height) + 2
                    block_x2 = block_x1 + block_width - 4
                    block_y2 = content_start_y + (end_idx * slot_height) - 2

                    # Get color
                    color = self.person_colors.get(person_name, accent)

                    # Draw block
                    draw.rectangle([block_x1, block_y1, block_x2, block_y2],
                                  fill=color, outline=border, width=2)

                    # Draw name
                    display_name = self.get_display_name(person_name)
                    if is_short:
                        display_name += " ⚠"

                    # Center text in block
                    text_bbox = draw.textbbox((0, 0), display_name, font=small_font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_x = block_x1 + (block_x2 - block_x1 - text_width) // 2
                    text_y = block_y1 + (block_y2 - block_y1 - text_height) // 2

                    draw.text((text_x, text_y), display_name, fill=bg_dark, font=small_font)

        # Hours section (right side)
        hours_x = 720
        hours_y = 70
        hours_width = 650

        # Draw hours border
        draw.rectangle([hours_x, hours_y, hours_x + hours_width, schedule_y + day_height * 2 + 20],
                      outline=border, width=2)

        # Draw title
        draw.text((hours_x + 20, hours_y + 15), "Hours Tracker",
                 fill=accent, font=header_font)

        # Draw headers
        header_y = hours_y + 50
        headers = ["Name", "Scheduled", "Preferred", "Agreed", "Max"]
        header_x_positions = [hours_x + 20, hours_x + 220, hours_x + 350, hours_x + 450, hours_x + 550]

        for i, header in enumerate(headers):
            draw.text((header_x_positions[i], header_y), header,
                     fill=accent, font=normal_font)

        # Draw separator line
        draw.line([hours_x + 20, header_y + 25, hours_x + hours_width - 20, header_y + 25],
                 fill=border, width=2)

        # Draw people data
        sorted_people = sorted(self.people, key=lambda p: p['name'])
        row_height = 25
        data_y = header_y + 35

        for idx, person in enumerate(sorted_people):
            y = data_y + (idx * row_height)
            name = person['name']
            scheduled = self.hours_scheduled[name]
            preferred = person['preferred_hours']
            agreed = person['agreed_hours']
            max_hours = person['max_hours']

            # Color code based on hours
            if scheduled < agreed:
                sched_color = error
            elif scheduled < preferred:
                sched_color = warning_color
            else:
                sched_color = success

            # Draw person color indicator
            person_color = self.person_colors.get(name, accent)
            draw.rectangle([hours_x + 10, y, hours_x + 15, y + 15],
                          fill=person_color)

            # Draw data
            draw.text((header_x_positions[0], y), name, fill=text_primary, font=small_font)
            draw.text((header_x_positions[1], y), f"{scheduled:.1f}h", fill=sched_color, font=small_font)
            draw.text((header_x_positions[2], y), f"{preferred}h", fill=text_muted, font=small_font)
            draw.text((header_x_positions[3], y), f"{agreed}h", fill=text_muted, font=small_font)
            draw.text((header_x_positions[4], y), f"{max_hours}h", fill=text_muted, font=small_font)

        # Save image
        img.save(file_path, 'PNG')


    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.csv_file_path = file_path
                self.parse_csv()
                self.file_label.config(text=file_path.split('/')[-1], fg=self.colors['success'])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
                self.file_label.config(text="Error loading file", fg=self.colors['error'])

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
            # Parse per-day desks
            self.desks_per_day = {
                'Monday': int(self.desks_monday.get()),
                'Tuesday': int(self.desks_tuesday.get()),
                'Wednesday': int(self.desks_wednesday.get()),
                'Thursday': int(self.desks_thursday.get())
            }
            min_shift = int(self.min_shift_length.get())
            total_hours_target = int(self.total_hours_target.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all configuration fields")
            return

        # Generate colors for people
        self.generate_person_colors()

        # Initialize schedule and hours (new structure: person-centric)
        self.schedule = {day: {} for day in self.day_names}
        self.hours_scheduled = {person['name']: 0 for person in self.people}

        # For algorithm: track old style (slot: [people])
        self.temp_schedule = {day: {i: [] for i in range(len(self.timeslots) - 1)} for day in self.day_names}

        # Run scheduling algorithm with per-day desks and target hours
        self.run_scheduling_algorithm(self.desks_per_day, min_shift, total_hours_target)

        # Convert temp_schedule to person-centric schedule
        self.convert_to_person_schedule(min_shift)

        # Mark as generated
        self.schedule_generated = True

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

    def run_scheduling_algorithm(self, desks_per_day, min_shift, total_hours_target):
        """
        Scheduling algorithm with priorities:
        1. Equal distribution across all timeslots
        2. Fill as many desks as possible (per day)
        3. Everyone gets at least one shift
        4. Respect minimum shift length
        5. Try to reach total hours target
        6. Prioritize preferred -> agreed -> max hours
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

            best_shift = self.find_best_shift(person, desks_per_day, min_shift, timeslot_counts, person_shifts)

            if best_shift:
                self.assign_shift(person, best_shift, timeslot_counts, person_shifts)
                unscheduled_people.remove(person['name'])

        # Phase 2: Fill remaining slots, prioritizing equal distribution and preferred hours
        # Continue until target hours reached or no more assignments possible
        max_iterations = 100
        iteration = 0
        total_hours_scheduled = sum(self.hours_scheduled.values())

        while iteration < max_iterations and total_hours_scheduled < total_hours_target:
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
                best_shift = self.find_best_shift(person, desks_per_day, min_shift, timeslot_counts, person_shifts)

                if best_shift:
                    self.assign_shift(person, best_shift, timeslot_counts, person_shifts)
                    assigned_something = True
                    total_hours_scheduled = sum(self.hours_scheduled.values())

                    # Check if target reached
                    if total_hours_scheduled >= total_hours_target:
                        break

            if not assigned_something:
                break

        # Phase 3: Try to fill empty slots with short shifts if necessary (only if under target)
        if total_hours_scheduled < total_hours_target:
            self.fill_remaining_with_short_shifts(desks_per_day, min_shift, timeslot_counts, total_hours_target)

    def find_best_shift(self, person, desks_per_day, min_shift, timeslot_counts, person_shifts):
        """Find the best shift for a person based on availability and current distribution"""
        best_shift = None
        best_score = float('inf')

        for day_idx, day in enumerate(self.day_names):
            day_code = self.days[day_idx]
            desks = desks_per_day[day]  # Get desk count for this specific day

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

                    # Check if this shift would exceed max hours
                    if self.hours_scheduled[person['name']] + shift_hours > person['max_hours']:
                        continue

                    # Score: prefer filling empty slots, prioritize matching preferred hours
                    # Lower score is better
                    current_hours = self.hours_scheduled[person['name']]
                    hours_gap_from_preferred = abs(person['preferred_hours'] - (current_hours + shift_hours))
                    score = avg_in_slots * 100 + hours_gap_from_preferred

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

    def fill_remaining_with_short_shifts(self, desks_per_day, min_shift, timeslot_counts, total_hours_target):
        """Try to fill empty slots with short shifts as last resort"""
        for day in self.day_names:
            day_code = self.days[self.day_names.index(day)]
            desks = desks_per_day[day]  # Get desk count for this specific day

            for slot_idx in range(len(self.timeslots) - 1):
                # Check if we've reached the target
                total_hours_scheduled = sum(self.hours_scheduled.values())
                if total_hours_scheduled >= total_hours_target:
                    return

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

        min_shift = int(self.min_shift_length.get())

        # Main container
        main_container = tk.Frame(self.schedule_frame, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Week information at top
        week_info = tk.Label(main_container,
                            text=self.get_week_display_text(),
                            font=("Consolas", 14, "bold"),
                            fg=self.colors['accent'],
                            bg=self.colors['bg_dark'],
                            pady=15)
        week_info.pack(anchor=tk.W)

        # 2x2 grid for days (more width per day)
        days_grid = tk.Frame(main_container, bg=self.colors['bg_dark'])
        days_grid.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Configure grid to expand equally
        for i in range(2):
            days_grid.columnconfigure(i, weight=1)
            days_grid.rowconfigure(i, weight=1)

        # Create each day block in 2x2 grid
        grid_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for day_idx, day in enumerate(self.day_names):
            row, col = grid_positions[day_idx]
            desks = self.desks_per_day[day]  # Get desk count for this specific day
            self.create_day_block(days_grid, day, day_idx, desks, min_shift, row, col)

    def create_day_block(self, parent, day, day_idx, desks, min_shift, row, col):
        """Create a single day schedule block"""
        # Day container with rounded appearance
        day_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        day_container.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S),
                          padx=5, pady=5)

        # Day header
        header = tk.Frame(day_container, bg=self.colors['bg_medium'],
                         height=40)
        header.pack(fill=tk.X, pady=(0, 5))

        tk.Label(header, text=day,
                font=("Consolas", 13, "bold"),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_medium'],
                pady=10).pack()

        # Schedule grid frame (time + warnings + calendar)
        schedule_grid = tk.Frame(day_container, bg=self.colors['bg_dark'])
        schedule_grid.pack(fill=tk.BOTH, expand=True)

        # Time column
        time_col = tk.Frame(schedule_grid, bg=self.colors['bg_dark'], width=60)
        time_col.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=(0, 5))

        # Warning column
        warning_col = tk.Frame(schedule_grid, bg=self.colors['bg_dark'], width=50)
        warning_col.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(0, 5))

        # Calendar canvas
        canvas_frame = tk.Frame(schedule_grid, bg=self.colors['bg_dark'])
        canvas_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        schedule_grid.columnconfigure(2, weight=1)

        # Create canvas with reduced height
        SLOT_HEIGHT = 45  # Reduced from ~64 to 45 pixels per slot
        canvas_height = len(self.timeslots[:-1]) * SLOT_HEIGHT

        day_canvas = tk.Canvas(canvas_frame,
                              height=canvas_height,
                              bg=self.colors['bg_dark'],
                              highlightthickness=1,
                              highlightbackground=self.colors['border'])
        day_canvas.pack(fill=tk.BOTH, expand=True)

        # Add time labels with matching spacing
        for i, time in enumerate(self.timeslots[:-1]):
            tk.Label(time_col, text=time,
                    font=("Consolas", 9),
                    fg=self.colors['text_muted'],
                    bg=self.colors['bg_dark'],
                    anchor=tk.E).grid(row=i, column=0, sticky=tk.E, pady=(0, SLOT_HEIGHT-12))

        # Count capacity and add warnings
        slot_counts = {i: 0 for i in range(len(self.timeslots) - 1)}

        if day in self.schedule:
            for person_name, shift in self.schedule[day].items():
                for i in range(shift['start'], shift['end']):
                    if i in slot_counts:
                        slot_counts[i] += 1

        # Add warning labels with matching spacing
        for i in range(len(self.timeslots) - 1):
            if slot_counts[i] < desks:
                warning_label = tk.Label(warning_col,
                                        text=f"⚠ {slot_counts[i]}/{desks}",
                                        font=("Consolas", 8),
                                        fg=self.colors['error'],
                                        bg=self.colors['bg_dark'])
                warning_label.grid(row=i, column=0, pady=(0, SLOT_HEIGHT-12))
                # Add tooltip explaining the warning
                ToolTip(warning_label, f"Understaffed: Only {slot_counts[i]} of {desks} desks filled")

        # Update canvas when it's sized
        def draw_schedule(event=None):
            canvas_width = day_canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = 400  # Default width

            day_canvas.delete("all")

            # Draw time grid lines
            for i in range(len(self.timeslots)):
                y = i * SLOT_HEIGHT
                day_canvas.create_line(0, y, canvas_width, y,
                                      fill=self.colors['border'],
                                      width=1)

            # Draw schedule blocks
            if day in self.schedule:
                # Calculate block width
                block_width = (canvas_width - 10) / desks

                # Track lane assignments: {lane: [(start, end), ...]}
                lanes = [[] for _ in range(desks)]

                people_shifts = list(self.schedule[day].items())
                people_shifts.sort(key=lambda x: (x[1]['start'], x[1]['end']))

                for person_name, shift in people_shifts:
                    start_idx = shift['start']
                    end_idx = shift['end']
                    is_short = shift.get('is_short', False)

                    # Find first available lane where this shift doesn't overlap
                    assigned_lane = None
                    for lane_idx in range(desks):
                        # Check if this shift overlaps with any shift in this lane
                        overlaps = False
                        for existing_start, existing_end in lanes[lane_idx]:
                            # Check for overlap: shifts overlap if one starts before the other ends
                            if not (end_idx <= existing_start or start_idx >= existing_end):
                                overlaps = True
                                break

                        if not overlaps:
                            assigned_lane = lane_idx
                            lanes[lane_idx].append((start_idx, end_idx))
                            break

                    if assigned_lane is None:
                        # Shouldn't happen if desk count is correct, but fallback to lane 0
                        assigned_lane = 0

                    # Calculate position
                    y1 = start_idx * SLOT_HEIGHT + 3
                    y2 = end_idx * SLOT_HEIGHT - 3
                    x1 = 5 + (assigned_lane * block_width)
                    x2 = x1 + block_width - 5

                    # Get color
                    color = self.person_colors.get(person_name, self.colors['accent'])

                    # Draw rounded rectangle with rounded border
                    radius = 8
                    self.draw_rounded_rect(day_canvas, x1, y1, x2, y2, radius,
                                          fill=color, outline=self.colors['border'], width=2)

                    # Add name with adaptive font size to ensure it fits
                    display_name = self.get_display_name(person_name)
                    if is_short:
                        display_name += " ⚠"

                    # Calculate available width
                    available_width = x2 - x1 - 10  # 5px padding on each side
                    text_y = (y1 + y2) / 2

                    # Try different font sizes to fit the text
                    font_size = 10
                    font = ("Consolas", font_size, "bold")

                    # Estimate text width (rough approximation: 0.6 * font_size per character)
                    estimated_width = len(display_name) * (font_size * 0.6)

                    # Reduce font size if text is too wide
                    while estimated_width > available_width and font_size > 6:
                        font_size -= 1
                        font = ("Consolas", font_size, "bold")
                        estimated_width = len(display_name) * (font_size * 0.6)

                    # If still too wide, truncate with ellipsis
                    final_name = display_name
                    if estimated_width > available_width:
                        max_chars = int(available_width / (font_size * 0.6)) - 3
                        if max_chars > 0:
                            final_name = display_name[:max_chars] + "..."

                    day_canvas.create_text((x1 + x2) / 2, text_y,
                                          text=final_name,
                                          fill=self.colors['bg_dark'],
                                          font=font)

        day_canvas.bind('<Configure>', draw_schedule)
        day_canvas.after(100, draw_schedule)

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on canvas"""
        fill = kwargs.get('fill', '')
        outline = kwargs.get('outline', '')
        width = kwargs.get('width', 1)

        # Draw filled rounded rectangle
        if fill:
            canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2,
                             start=90, extent=90, fill=fill, outline="")
            canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2,
                             start=0, extent=90, fill=fill, outline="")
            canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2,
                             start=180, extent=90, fill=fill, outline="")
            canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2,
                             start=270, extent=90, fill=fill, outline="")
            canvas.create_rectangle(x1+radius, y1, x2-radius, y2,
                                   fill=fill, outline="")
            canvas.create_rectangle(x1, y1+radius, x2, y2-radius,
                                   fill=fill, outline="")

        # Draw rounded outline
        if outline:
            canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2,
                             start=90, extent=90, outline=outline, width=width, style='arc')
            canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2,
                             start=0, extent=90, outline=outline, width=width, style='arc')
            canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2,
                             start=180, extent=90, outline=outline, width=width, style='arc')
            canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2,
                             start=270, extent=90, outline=outline, width=width, style='arc')
            canvas.create_line(x1+radius, y1, x2-radius, y1,
                              fill=outline, width=width)
            canvas.create_line(x1+radius, y2, x2-radius, y2,
                              fill=outline, width=width)
            canvas.create_line(x1, y1+radius, x1, y2-radius,
                              fill=outline, width=width)
            canvas.create_line(x2, y1+radius, x2, y2-radius,
                              fill=outline, width=width)

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
