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

        # Set window icon
        try:
            icon_path = "/home/user/B2.0Schedulingtool/calendar.ico"
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")

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

        # Timeslots (fixed shift times)
        # Shifts: 9:30-12:30 (3h), 10:30-12:30 (2h), 13:00-15:30 (2.5h), 13:00-17:00 (4h)
        self.timeslots = [
            "9:30", "10:30", "12:30", "13:00", "15:30", "17:00"
        ]
        self.timeslot_codes = ["0930", "1030", "1300", "1300F"]  # Start time of each shift
        self.shift_definitions = {
            "0930": {"start": "9:30", "end": "12:30", "hours": 3.0},
            "1030": {"start": "10:30", "end": "12:30", "hours": 2.0},
            "1300": {"start": "13:00", "end": "15:30", "hours": 2.5},
            "1300F": {"start": "13:00", "end": "17:00", "hours": 4.0}
        }

        # 2 weeks = 8 days (Mon-Thu, Week 1 and Week 2)
        self.days = ["M1", "TU1", "W1", "TH1", "M2", "TU2", "W2", "TH2"]
        self.day_names = [
            "Monday (Week 1)", "Tuesday (Week 1)", "Wednesday (Week 1)", "Thursday (Week 1)",
            "Monday (Week 2)", "Tuesday (Week 2)", "Wednesday (Week 2)", "Thursday (Week 2)"
        ]

        # Configuration variables
        self.csv_file_path = None
        self.week_number = tk.StringVar(value="1")
        # Desk configuration for 8 days (2 weeks)
        self.desks_m1 = tk.StringVar(value="8")
        self.desks_tu1 = tk.StringVar(value="8")
        self.desks_w1 = tk.StringVar(value="8")
        self.desks_th1 = tk.StringVar(value="8")
        self.desks_m2 = tk.StringVar(value="8")
        self.desks_tu2 = tk.StringVar(value="8")
        self.desks_w2 = tk.StringVar(value="8")
        self.desks_th2 = tk.StringVar(value="8")
        self.rigidity = tk.IntVar(value=50)  # Slider 0-100 for shift preference rigidity
        self.weekly_variance = tk.DoubleVar(value=1.0)  # Slider 0-2 (0.5h increments) for weekly hour variance tolerance
        self.total_hours_target = tk.StringVar(value="270")  # 2 weeks = 135*2

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

        # Canvas for rounded border (increased size to fit all inputs including 2 weeks and variance slider)
        canvas = tk.Canvas(config_container, width=700, height=480,
                          bg=self.colors['bg_dark'], highlightthickness=0)
        canvas.pack()

        # Draw rounded rectangle border
        self.draw_rounded_rect(canvas, 2, 2, 698, 478, 10,
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

        # Rigidity slider
        row_y += 1
        tk.Label(config_frame, text="Shift Preference Rigidity:",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=0, sticky=tk.W, padx=5, pady=3)

        rigidity_frame = tk.Frame(config_frame, bg=self.colors['bg_dark'])
        rigidity_frame.grid(row=row_y, column=1, columnspan=3, sticky=tk.W, padx=5)

        tk.Label(rigidity_frame, text="Flexible",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).pack(side=tk.LEFT)

        rigidity_slider = tk.Scale(rigidity_frame, from_=0, to=100,
                                   orient=tk.HORIZONTAL, variable=self.rigidity,
                                   bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                   highlightthickness=0, troughcolor=self.colors['bg_medium'],
                                   length=200, width=15, showvalue=0)
        rigidity_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(rigidity_frame, text="Strict",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).pack(side=tk.LEFT)

        ToolTip(rigidity_slider, "Low: Allow more 2-hour shifts\nHigh: Prefer full morning/afternoon shifts")

        # Weekly variance slider
        row_y += 1
        tk.Label(config_frame, text="Weekly Hour Variance:",
                bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                font=("Consolas", 9)).grid(row=row_y, column=0, sticky=tk.W, padx=5, pady=3)

        variance_frame = tk.Frame(config_frame, bg=self.colors['bg_dark'])
        variance_frame.grid(row=row_y, column=1, columnspan=3, sticky=tk.W, padx=5)

        tk.Label(variance_frame, text="0h",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).pack(side=tk.LEFT)

        variance_slider = tk.Scale(variance_frame, from_=0, to=2, resolution=0.5,
                                   orient=tk.HORIZONTAL, variable=self.weekly_variance,
                                   bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                                   highlightthickness=0, troughcolor=self.colors['bg_medium'],
                                   length=200, width=15, showvalue=0)
        variance_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(variance_frame, text="2h",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).pack(side=tk.LEFT)

        ToolTip(variance_slider, "Allow weekly hour variation if compensated in other week\n0: Strict weekly balance\n2: Allow up to 2h variation per week")

        # Desks per day header
        row_y += 1
        tk.Label(config_frame, text="Desks Available Per Day (2 Weeks):",
                bg=self.colors['bg_dark'], fg=self.colors['accent'],
                font=("Consolas", 9, "bold")).grid(row=row_y, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(10, 3))

        # Week 1 desks
        row_y += 1
        tk.Label(config_frame, text="Week 1:",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).grid(row=row_y, column=0, columnspan=4, sticky=tk.W, padx=5, pady=3)
        row_y += 1
        desk_vars_w1 = [
            ("Mon:", self.desks_m1),
            ("Tue:", self.desks_tu1),
            ("Wed:", self.desks_w1),
            ("Thu:", self.desks_th1)
        ]

        # Create 2x2 grid for week 1
        for i, (label, var) in enumerate(desk_vars_w1):
            grid_row = row_y + (i // 2)
            grid_col = (i % 2) * 2

            tk.Label(config_frame, text=label,
                    bg=self.colors['bg_dark'], fg=self.colors['text_primary'],
                    font=("Consolas", 9)).grid(row=grid_row, column=grid_col, sticky=tk.W, padx=5, pady=3)
            tk.Entry(config_frame, textvariable=var, width=6,
                    bg=self.colors['bg_light'], fg=self.colors['text_primary'],
                    insertbackground=self.colors['text_primary'],
                    font=("Consolas", 9), relief=tk.FLAT).grid(row=grid_row, column=grid_col+1, sticky=tk.W, padx=5)

        # Week 2 desks
        row_y += 2
        tk.Label(config_frame, text="Week 2:",
                bg=self.colors['bg_dark'], fg=self.colors['text_secondary'],
                font=("Consolas", 8)).grid(row=row_y, column=0, columnspan=4, sticky=tk.W, padx=5, pady=3)
        row_y += 1
        desk_vars_w2 = [
            ("Mon:", self.desks_m2),
            ("Tue:", self.desks_tu2),
            ("Wed:", self.desks_w2),
            ("Thu:", self.desks_th2)
        ]

        # Create 2x2 grid for week 2
        for i, (label, var) in enumerate(desk_vars_w2):
            grid_row = row_y + (i // 2)
            grid_col = (i % 2) * 2

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
        gen_btn.grid(row=row_y, column=0, columnspan=4, pady=10, sticky=tk.W)

        # Export buttons on next row
        row_y += 1
        export_png_btn = tk.Button(config_frame, text="Export as PNG", command=self.export_schedule,
                                   bg=self.colors['success'], fg=self.colors['text_primary'],
                                   font=("Consolas", 9, "bold"), relief=tk.FLAT,
                                   padx=12, pady=5, cursor="hand2")
        export_png_btn.grid(row=row_y, column=0, columnspan=2, pady=5, sticky=tk.W)

        export_csv_btn = tk.Button(config_frame, text="Export as CSV", command=self.export_csv,
                                   bg=self.colors['success'], fg=self.colors['text_primary'],
                                   font=("Consolas", 9, "bold"), relief=tk.FLAT,
                                   padx=12, pady=5, cursor="hand2")
        export_csv_btn.grid(row=row_y, column=2, columnspan=2, pady=5, sticky=tk.W, padx=(15, 0))

        # Hover effects for buttons
        def on_enter(e, btn, color):
            btn['bg'] = color
        def on_leave(e, btn, color):
            btn['bg'] = color

        browse_btn.bind("<Enter>", lambda e: on_enter(e, browse_btn, self.colors['bg_medium']))
        browse_btn.bind("<Leave>", lambda e: on_leave(e, browse_btn, self.colors['bg_light']))
        gen_btn.bind("<Enter>", lambda e: on_enter(e, gen_btn, self.colors['accent_hover']))
        gen_btn.bind("<Leave>", lambda e: on_leave(e, gen_btn, self.colors['accent']))
        export_png_btn.bind("<Enter>", lambda e: on_enter(e, export_png_btn, '#6ec57e'))
        export_png_btn.bind("<Leave>", lambda e: on_leave(e, export_png_btn, self.colors['success']))
        export_csv_btn.bind("<Enter>", lambda e: on_enter(e, export_csv_btn, '#6ec57e'))
        export_csv_btn.bind("<Leave>", lambda e: on_leave(e, export_csv_btn, self.colors['success']))


    def setup_display_section(self, parent):
        # Create container for side-by-side layout
        display_container = tk.Frame(parent, bg=self.colors['bg_dark'])
        display_container.grid(row=1, column=0, sticky=(tk.W, tk.N), padx=10, pady=(10, 20))

        # Schedule section (left side)
        schedule_container = tk.Frame(display_container, bg=self.colors['bg_dark'])
        schedule_container.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 10))

        # Create canvas border for schedule (will resize based on content)
        self.schedule_canvas_border = tk.Canvas(schedule_container,
                                               bg=self.colors['bg_dark'],
                                               highlightthickness=0)
        self.schedule_canvas_border.pack()

        # Create frame for schedule content directly (no scrolling)
        self.schedule_frame = tk.Frame(self.schedule_canvas_border, bg=self.colors['bg_dark'])

        # Placeholder will be replaced when schedule is generated
        self.schedule_content_window = None

        # Hours section (right side)
        hours_container = tk.Frame(display_container, bg=self.colors['bg_dark'])
        hours_container.grid(row=0, column=1, sticky=(tk.W, tk.N))

        # Create canvas border for hours (will resize based on content)
        self.hours_canvas_border = tk.Canvas(hours_container,
                                            bg=self.colors['bg_dark'],
                                            highlightthickness=0)
        self.hours_canvas_border.pack()

        # Create frame for hours content directly (no scrolling)
        self.hours_frame = tk.Frame(self.hours_canvas_border, bg=self.colors['bg_dark'])

        # Placeholder will be replaced when schedule is generated
        self.hours_content_window = None

        # Show placeholder initially
        self.show_placeholder(self.schedule_frame, "Load CSV and Generate Schedule")
        self.show_placeholder(self.hours_frame, "Hours Tracker")

        # Initial sizing
        self.update_schedule_canvas_size()
        self.update_hours_canvas_size()

    def update_schedule_canvas_size(self):
        """Update schedule canvas size based on content"""
        self.schedule_frame.update_idletasks()

        # Get the required size for the content
        content_width = self.schedule_frame.winfo_reqwidth()
        content_height = self.schedule_frame.winfo_reqheight()

        # Add padding for the border
        canvas_width = content_width + 40
        canvas_height = content_height + 40

        # Update canvas size
        self.schedule_canvas_border.configure(width=canvas_width, height=canvas_height)

        # Redraw border
        self.schedule_canvas_border.delete("border")
        self.draw_rounded_rect(self.schedule_canvas_border, 2, 2,
                              canvas_width-2, canvas_height-2, 10,
                              fill=self.colors['bg_dark'],
                              outline=self.colors['border'], width=2,
                              tags="border")

        # Position content window
        if self.schedule_content_window:
            self.schedule_canvas_border.delete(self.schedule_content_window)
        self.schedule_content_window = self.schedule_canvas_border.create_window(
            20, 20, window=self.schedule_frame, anchor=tk.NW)

    def update_hours_canvas_size(self):
        """Update hours canvas size based on content"""
        self.hours_frame.update_idletasks()

        # Get the required size for the content
        content_width = self.hours_frame.winfo_reqwidth()
        content_height = self.hours_frame.winfo_reqheight()

        # Add padding for the border
        canvas_width = content_width + 40
        canvas_height = content_height + 40

        # Update canvas size
        self.hours_canvas_border.configure(width=canvas_width, height=canvas_height)

        # Redraw border
        self.hours_canvas_border.delete("border")
        self.draw_rounded_rect(self.hours_canvas_border, 2, 2,
                              canvas_width-2, canvas_height-2, 10,
                              fill=self.colors['bg_dark'],
                              outline=self.colors['border'], width=2,
                              tags="border")

        # Position content window
        if self.hours_content_window:
            self.hours_canvas_border.delete(self.hours_content_window)
        self.hours_content_window = self.hours_canvas_border.create_window(
            20, 20, window=self.hours_frame, anchor=tk.NW)

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
        """Get formatted week display text for 2 weeks"""
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

            # Calculate the start of the requested week and the next week
            week1_start = first_monday + timedelta(weeks=week_num - 1)
            week2_end = week1_start + timedelta(days=10)  # End of second Thursday (2 weeks)

            return f"Week {week_num} + {week_num + 1}  •  {week1_start.strftime('%B %d')} - {week2_end.strftime('%B %d, %Y')}"
        except ValueError:
            return "Invalid week number"

    def export_csv(self):
        """Export the schedule as a CSV file with grouped dates"""
        if not self.schedule_generated:
            messagebox.showwarning("Warning", "Please generate a schedule first")
            return

        try:
            # Get week info for filename and dates
            week_num = int(self.week_number.get())
            filename = f"B2.0 Schedule week {week_num}.csv"
            year = datetime.now().year

            # Calculate dates for each day
            jan_1 = datetime(year, 1, 1)
            days_to_monday = (7 - jan_1.weekday()) % 7
            if days_to_monday == 0 and jan_1.weekday() != 0:
                days_to_monday = 7
            first_monday = jan_1 + timedelta(days=days_to_monday)

            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=filename
            )

            if not file_path:
                return

            # Create CSV with new format
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow(['Date', 'Person', 'Shift Hours', 'Hours'])

                # Process each day
                for day_idx, day in enumerate(self.day_names):
                    if day in self.schedule and self.schedule[day]:
                        # Calculate the actual date for this day
                        # Week 1 days: 0-3, Week 2 days: 4-7
                        week_offset = (week_num - 1) * 7
                        if day_idx < 4:
                            # Week 1 (Mon-Thu)
                            day_offset = day_idx
                        else:
                            # Week 2 (Mon-Thu of next week)
                            day_offset = day_idx + 3  # Skip Fri, Sat, Sun

                        current_date = first_monday + timedelta(weeks=(week_num - 1), days=day_offset)
                        date_str = current_date.strftime('%A %d %b').lower()

                        # Get all people scheduled this day, sorted by name
                        people_this_day = sorted(self.schedule[day].items())

                        # Write first person with date
                        if people_this_day:
                            first_person = True
                            for person_name, person_data in people_this_day:
                                shifts = person_data['shifts']
                                hours = person_data['hours']

                                # Format shift times
                                morning_shifts = [s for s in shifts if s in ['0930', '1030']]
                                afternoon_shifts = [s for s in shifts if s in ['1300', '1300F']]

                                shift_parts = []
                                if morning_shifts:
                                    start = self.shift_definitions[morning_shifts[0]]['start']
                                    end = self.shift_definitions[morning_shifts[-1]]['end']
                                    shift_parts.append(f"{start}-{end}")

                                if afternoon_shifts:
                                    start = self.shift_definitions[afternoon_shifts[0]]['start']
                                    end = self.shift_definitions[afternoon_shifts[-1]]['end']
                                    shift_parts.append(f"{start}-{end}")

                                shifts_str = ', '.join(shift_parts)

                                # Format hours as hours:minutes
                                hours_int = int(hours)
                                minutes = int((hours - hours_int) * 60)
                                hours_str = f"{hours_int}:{minutes:02d}"

                                # Write row (date only for first person)
                                if first_person:
                                    writer.writerow([date_str, person_name, shifts_str, hours_str])
                                    first_person = False
                                else:
                                    writer.writerow(['', person_name, shifts_str, hours_str])

            messagebox.showinfo("Success", f"Schedule exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")

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
        """Create a professional PNG export of schedule and hours using shift codes"""
        # Image dimensions (increased for 2 weeks)
        img_width = 1600
        img_height = 1400

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

        # Draw title
        draw.text((30, 30), week_text, fill=accent, font=title_font)

        # Schedule section (left side) - 8 days in 2x4 grid
        schedule_x = 30
        schedule_y = 70
        day_width = 350
        day_height = 300

        # Shift heights for drawing (proportional to hours)
        shift_heights = {"0930": 90, "1030": 60, "1300": 75, "1300F": 120}

        # Draw 2x4 grid of days (2 columns, 4 rows for 8 days)
        for day_idx, day in enumerate(self.day_names):
            col = day_idx % 2
            row = day_idx // 2
            x = schedule_x + (col * (day_width + 20))
            y = schedule_y + (row * (day_height + 20))

            # Draw day container border
            draw.rectangle([x, y, x + day_width, y + day_height],
                          outline=border, width=2)

            # Draw day header
            draw.rectangle([x, y, x + day_width, y + 30],
                          fill=bg_medium, outline=border, width=1)
            draw.text((x + 10, y + 10), day, fill=text_primary, font=header_font)

            # Get desk count for this day
            desks = self.desks_per_day[day]

            # Draw shift times and schedule
            time_x = x + 10
            content_start_y = y + 40

            # Count shift capacity
            shift_counts = {code: 0 for code in self.timeslot_codes}
            if day in self.schedule:
                for person_name, person_data in self.schedule[day].items():
                    for shift_code in person_data['shifts']:
                        shift_counts[shift_code] += 1

            # Draw shift times and warnings
            y_offset = content_start_y
            for shift_code in self.timeslot_codes:
                shift_info = self.shift_definitions[shift_code]

                # Time label (show full range for clarity)
                time_label = f"{shift_info['start']}-{shift_info['end']}"
                draw.text((time_x, y_offset), time_label, fill=text_muted, font=small_font)

                # Warning if understaffed
                if shift_counts[shift_code] < desks:
                    warning_text = f"⚠{shift_counts[shift_code]}/{desks}"
                    draw.text((time_x + 45, y_offset), warning_text, fill=error, font=small_font)

                y_offset += shift_heights[shift_code]

            # Draw schedule blocks
            if day in self.schedule:
                blocks_start_x = time_x + 90
                available_width = day_width - (blocks_start_x - x) - 10
                block_width = available_width // desks if desks > 0 else available_width

                # Track lane assignments
                shift_lanes = {code: [] for code in self.timeslot_codes}

                people_shifts = list(self.schedule[day].items())
                people_shifts.sort(key=lambda x: x[1]['shifts'])

                for person_name, person_data in people_shifts:
                    shifts = person_data['shifts']

                    # Find a lane that's free for all required shifts
                    assigned_lane = None
                    for lane_idx in range(desks):
                        lane_is_free = all(
                            lane_idx >= len(shift_lanes[shift_code]) or
                            shift_lanes[shift_code][lane_idx] is None
                            for shift_code in shifts
                        )

                        if lane_is_free:
                            assigned_lane = lane_idx
                            for shift_code in shifts:
                                while len(shift_lanes[shift_code]) <= lane_idx:
                                    shift_lanes[shift_code].append(None)
                                shift_lanes[shift_code][lane_idx] = person_name
                            break

                    if assigned_lane is None:
                        assigned_lane = 0

                    # Draw blocks for each shift
                    y_offset = content_start_y
                    for shift_code in self.timeslot_codes:
                        if shift_code in shifts:
                            shift_info = self.shift_definitions[shift_code]

                            # Calculate position
                            y1 = y_offset + 2
                            y2 = y_offset + shift_heights[shift_code] - 2
                            x1 = blocks_start_x + (assigned_lane * block_width) + 2
                            x2 = blocks_start_x + ((assigned_lane + 1) * block_width) - 2

                            # Get color
                            color = self.person_colors.get(person_name, accent)

                            # Draw block
                            draw.rectangle([x1, y1, x2, y2],
                                          fill=color, outline=border, width=2)

                            # Draw name (simplified for space)
                            display_name = self.get_display_name(person_name)
                            center_x = x1 + (x2 - x1) // 2
                            center_y = y1 + (y2 - y1) // 2

                            # Check text width and truncate if needed
                            text_bbox = draw.textbbox((0, 0), display_name, font=small_font)
                            text_width = text_bbox[2] - text_bbox[0]
                            available_width = x2 - x1 - 10

                            if text_width > available_width:
                                max_chars = int(available_width / (text_width / len(display_name))) - 3
                                if max_chars > 0:
                                    display_name = display_name[:max_chars] + "..."

                            name_bbox = draw.textbbox((0, 0), display_name, font=small_font)
                            name_width = name_bbox[2] - name_bbox[0]
                            draw.text((center_x - name_width // 2, center_y - 5),
                                     display_name, fill=bg_dark, font=small_font)

                        y_offset += shift_heights[shift_code]

        # Hours section (right side)
        hours_x = 760
        hours_y = 70
        hours_width = 500

        # Draw hours border
        draw.rectangle([hours_x, hours_y, hours_x + hours_width, hours_y + 800],
                      outline=border, width=2)

        # Draw title
        draw.text((hours_x + 20, hours_y + 15), "Hours Scheduled",
                 fill=accent, font=header_font)

        # Draw headers
        header_y = hours_y + 50
        headers = ["Name", "Scheduled"]
        header_x_positions = [hours_x + 20, hours_x + 350]

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

            # Draw person color indicator
            person_color = self.person_colors.get(name, accent)
            draw.rectangle([hours_x + 10, y, hours_x + 15, y + 15],
                          fill=person_color)

            # Draw data
            draw.text((header_x_positions[0], y), name, fill=text_primary, font=small_font)
            draw.text((header_x_positions[1], y), f"{scheduled:.1f}h", fill=text_muted, font=small_font)

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
                    # Hours are now for 2 weeks instead of 1 week
                    'agreed_hours': int(row['agreed hours per 2 weeks']),
                    'max_hours': int(row['max hours per 2 weeks']),
                    'preferred_hours': int(row['preferred hours per 2 weeks']),
                    'availability': {}
                }

                # Parse availability columns for each day and shift
                for day_code in self.days:
                    person['availability'][day_code] = {}
                    for slot_code in self.timeslot_codes:
                        col_name = f"{day_code}{slot_code}"
                        if col_name in row:
                            # Store availability by shift code
                            person['availability'][day_code][slot_code] = row[col_name].lower() in ['true', '1', 'yes']

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
            # Parse per-day desks for 2 weeks (8 days)
            self.desks_per_day = {
                'Monday (Week 1)': int(self.desks_m1.get()),
                'Tuesday (Week 1)': int(self.desks_tu1.get()),
                'Wednesday (Week 1)': int(self.desks_w1.get()),
                'Thursday (Week 1)': int(self.desks_th1.get()),
                'Monday (Week 2)': int(self.desks_m2.get()),
                'Tuesday (Week 2)': int(self.desks_tu2.get()),
                'Wednesday (Week 2)': int(self.desks_w2.get()),
                'Thursday (Week 2)': int(self.desks_th2.get())
            }
            rigidity = int(self.rigidity.get())
            weekly_variance = float(self.weekly_variance.get())
            total_hours_target = int(self.total_hours_target.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all configuration fields")
            return

        # Generate colors for people
        self.generate_person_colors()

        # Initialize schedule and hours
        # Schedule: {day: {person_name: {'shifts': [shift_codes], 'hours': float}} }
        self.schedule = {day: {} for day in self.day_names}
        self.hours_scheduled = {person['name']: 0 for person in self.people}

        # Track hours per week for variance checking
        self.week1_hours = {person['name']: 0 for person in self.people}
        self.week2_hours = {person['name']: 0 for person in self.people}

        # For algorithm: track shifts per shift code per day: {day: {shift_code: [people]}}
        self.temp_schedule = {day: {code: [] for code in self.timeslot_codes} for day in self.day_names}

        # Run scheduling algorithm with per-day desks, rigidity, weekly variance, and target hours
        self.run_scheduling_algorithm(self.desks_per_day, rigidity, weekly_variance, total_hours_target)

        # Convert temp_schedule to person-centric schedule
        self.convert_to_person_schedule()

        # Mark as generated
        self.schedule_generated = True

        # Display results
        self.display_schedule()
        self.display_hours()

    def convert_to_person_schedule(self):
        """Convert shift-code-based schedule to person-based schedule with shift grouping"""
        for day in self.day_names:
            person_shifts = {}

            # Find all shifts for each person
            for person in self.people:
                person_name = person['name']
                shifts_assigned = []

                # Find all shift codes this person is scheduled for
                for shift_code in self.timeslot_codes:
                    if person_name in self.temp_schedule[day][shift_code]:
                        shifts_assigned.append(shift_code)

                # If person has shifts, create entry
                if shifts_assigned:
                    # Calculate total hours
                    total_hours = sum(self.shift_definitions[code]['hours'] for code in shifts_assigned)

                    person_shifts[person_name] = {
                        'shifts': shifts_assigned,
                        'hours': total_hours
                    }

            self.schedule[day] = person_shifts

    def run_scheduling_algorithm(self, desks_per_day, rigidity, weekly_variance, total_hours_target):
        """
        Priority-Based Scheduling Algorithm with Fixed Shifts:

        HARD CONSTRAINTS:
        1. Never exceed desk capacity per shift (ABSOLUTE HARD LIMIT)
        2. Never schedule someone for over their max hours (ABSOLUTE HARD LIMIT)
        3. Weekly variance limit: |week_hours - preferred/2| <= weekly_variance (per week)
        4. Prevent conflicting shift assignments (overlapping time slots)

        PRIORITIES:
        1. Schedule everyone with nonzero preferred hours
        2. Get everyone to their preferred hours (can exceed total target for this)
        3. Try to meet or exceed total hours target
        4. Respect rigidity parameter for shift combinations
        5. Prefer longer shifts when possible
        """

        # Track shift filling for balance
        shift_counts = {day: {code: 0 for code in self.timeslot_codes} for day in self.day_names}

        # Get people with nonzero preferred hours
        people_to_schedule = [p for p in self.people if p['preferred_hours'] > 0]

        # Phase 1: Give everyone at least one shift combination
        for person in people_to_schedule:
            if self.hours_scheduled[person['name']] == 0:
                shift_combo = self.find_best_available_shift_combo(
                    person, desks_per_day, rigidity, shift_counts, 'initial', weekly_variance)
                if shift_combo:
                    self.assign_shift_combo_to_person(person, shift_combo, shift_counts)

        # Phase 2: AGGRESSIVELY fill everyone to their preferred hours
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            progress_made = False

            # Sort by distance from preferred hours (furthest first)
            for person in sorted(people_to_schedule,
                               key=lambda p: p['preferred_hours'] - self.hours_scheduled[p['name']],
                               reverse=True):

                # Try to get closer to preferred hours
                if self.hours_scheduled[person['name']] < person['preferred_hours']:
                    shift_combo = self.find_best_available_shift_combo(
                        person, desks_per_day, rigidity, shift_counts, 'preferred', weekly_variance)
                    if shift_combo:
                        self.assign_shift_combo_to_person(person, shift_combo, shift_counts)
                        progress_made = True

            if not progress_made:
                break

        # Phase 3: If still under target, use agreed hours tier
        total_scheduled = sum(self.hours_scheduled.values())

        if total_scheduled < total_hours_target:
            iteration = 0
            while total_scheduled < total_hours_target and iteration < max_iterations:
                iteration += 1
                progress_made = False

                for person in sorted(people_to_schedule,
                                   key=lambda p: p['agreed_hours'] - self.hours_scheduled[p['name']],
                                   reverse=True):

                    if self.hours_scheduled[person['name']] < person['agreed_hours']:
                        shift_combo = self.find_best_available_shift_combo(
                            person, desks_per_day, rigidity, shift_counts, 'agreed', weekly_variance)
                        if shift_combo:
                            self.assign_shift_combo_to_person(person, shift_combo, shift_counts)
                            total_scheduled = sum(self.hours_scheduled.values())
                            progress_made = True

                            if total_scheduled >= total_hours_target:
                                break

                if not progress_made or total_scheduled >= total_hours_target:
                    break

        # Phase 4: If still under target, use max hours tier
        if total_scheduled < total_hours_target:
            iteration = 0
            while total_scheduled < total_hours_target and iteration < max_iterations:
                iteration += 1
                progress_made = False

                for person in sorted(people_to_schedule,
                                   key=lambda p: p['max_hours'] - self.hours_scheduled[p['name']],
                                   reverse=True):

                    if self.hours_scheduled[person['name']] < person['max_hours']:
                        shift_combo = self.find_best_available_shift_combo(
                            person, desks_per_day, rigidity, shift_counts, 'max', weekly_variance)
                        if shift_combo:
                            self.assign_shift_combo_to_person(person, shift_combo, shift_counts)
                            total_scheduled = sum(self.hours_scheduled.values())
                            progress_made = True

                            if total_scheduled >= total_hours_target:
                                break

                if not progress_made or total_scheduled >= total_hours_target:
                    break

    def find_best_available_shift_combo(self, person, desks_per_day, rigidity, shift_counts, mode, weekly_variance):
        """
        Find the best available shift combination for a person based on rigidity

        Shift combinations by rigidity level:
        - High (70-100): Prefer longer single shifts (0930 or 1300F)
        - Medium (30-70): Allow mid-length shifts (1030, 1300, 1300F)
        - Low (0-30): Allow any shift, including shorter ones

        Weekly variance: Enforce weekly hour distribution constraint

        Note: Shifts can overlap (0930 overlaps with 1030, 1300F contains 1300),
        so conflicts must be prevented
        """
        best_combo = None
        best_score = float('inf')

        # Determine hours budget based on mode
        current_hours = self.hours_scheduled[person['name']]
        if mode == 'preferred' or mode == 'initial':
            hours_budget = person['preferred_hours'] - current_hours
        elif mode == 'agreed':
            hours_budget = person['agreed_hours'] - current_hours
        elif mode == 'max':
            hours_budget = person['max_hours'] - current_hours
        else:
            hours_budget = person['max_hours'] - current_hours

        # Never exceed max hours
        hours_budget = min(hours_budget, person['max_hours'] - current_hours)

        if hours_budget <= 0:
            return None

        # Define possible shift combinations by rigidity
        # Note: 0930 overlaps with 1030, 1300F overlaps with 1300
        if rigidity >= 70:
            # High rigidity: Prefer longest shifts and full day combinations
            combo_priorities = [
                ['0930', '1300F'],  # Full day: morning + long afternoon (7h)
                ['1300F'],          # Long afternoon only (4h)
                ['0930'],           # Full morning (3h)
                ['1030', '1300F'],  # Late morning + long afternoon (6h)
                ['1300'],           # Regular afternoon (2.5h)
                ['1030'],           # Late morning (2h)
            ]
        elif rigidity >= 30:
            # Medium rigidity: Allow various combinations
            combo_priorities = [
                ['0930', '1300F'],  # Full day: morning + long afternoon (7h)
                ['1030', '1300F'],  # Late morning + long afternoon (6h)
                ['0930', '1300'],   # Morning + regular afternoon (5.5h)
                ['1300F'],          # Long afternoon only (4h)
                ['0930'],           # Full morning (3h)
                ['1030', '1300'],   # Late morning + regular afternoon (4.5h)
                ['1300'],           # Regular afternoon (2.5h)
                ['1030'],           # Late morning (2h)
            ]
        else:
            # Low rigidity: Allow all valid combinations, prioritize longer shifts
            combo_priorities = [
                ['0930', '1300F'],  # Full day: morning + long afternoon (7h)
                ['1030', '1300F'],  # Late morning + long afternoon (6h)
                ['0930', '1300'],   # Morning + regular afternoon (5.5h)
                ['1030', '1300'],   # Late morning + regular afternoon (4.5h)
                ['1300F'],          # Long afternoon only (4h)
                ['0930'],           # Full morning (3h)
                ['1300'],           # Regular afternoon (2.5h)
                ['1030'],           # Late morning (2h)
            ]

        # Try each day
        for day_idx, day in enumerate(self.day_names):
            day_code = self.days[day_idx]
            desks = desks_per_day[day]

            # Check if person is already scheduled on this day
            person_already_scheduled = any(
                person['name'] in self.temp_schedule[day][code]
                for code in self.timeslot_codes
            )
            # Allow multiple shifts per day only in later phases
            if person_already_scheduled and mode == 'initial':
                continue

            # Try each shift combination in priority order
            for shift_codes in combo_priorities:
                # Calculate total hours for this combination
                combo_hours = sum(self.shift_definitions[code]['hours'] for code in shift_codes)

                # Check if within budget
                if combo_hours > hours_budget:
                    continue

                # Check if person is available for all shifts in combo
                all_available = True
                for shift_code in shift_codes:
                    if not person['availability'].get(day_code, {}).get(shift_code, False):
                        all_available = False
                        break

                if not all_available:
                    continue

                # Check if person already in any of these shifts (prevent duplicates)
                already_in_shifts = any(
                    person['name'] in self.temp_schedule[day][code]
                    for code in shift_codes
                )
                if already_in_shifts:
                    continue

                # Check for conflicting overlapping shifts
                # Morning shifts (0930 and 1030) overlap - can't have both
                # Afternoon shifts (1300 and 1300F) overlap - can't have both
                has_conflict = False
                for shift_code in shift_codes:
                    if shift_code == '0930':
                        # Check if person already has 1030
                        if person['name'] in self.temp_schedule[day]['1030']:
                            has_conflict = True
                            break
                    elif shift_code == '1030':
                        # Check if person already has 0930
                        if person['name'] in self.temp_schedule[day]['0930']:
                            has_conflict = True
                            break
                    elif shift_code == '1300':
                        # Check if person already has 1300F
                        if person['name'] in self.temp_schedule[day]['1300F']:
                            has_conflict = True
                            break
                    elif shift_code == '1300F':
                        # Check if person already has 1300
                        if person['name'] in self.temp_schedule[day]['1300']:
                            has_conflict = True
                            break

                if has_conflict:
                    continue

                # Check if all shifts have desk capacity
                all_have_room = all(
                    len(self.temp_schedule[day][code]) < desks
                    for code in shift_codes
                )
                if not all_have_room:
                    continue

                # Check weekly variance constraint
                # Determine which week this day belongs to
                # Week 1: days 0-3 (Monday-Thursday Week 1)
                # Week 2: days 4-7 (Monday-Thursday Week 2)
                week_idx = self.day_names.index(day)
                is_week1 = week_idx < 4

                # Get current week hours for this person
                current_week_hours = self.week1_hours[person['name']] if is_week1 else self.week2_hours[person['name']]

                # Calculate what total would be with this combo
                potential_week_hours = current_week_hours + combo_hours

                # Weekly target is half of preferred (preferred is for 2 weeks)
                weekly_target = person['preferred_hours'] / 2

                # Check if this would violate weekly variance constraint
                # Allow deviation up to weekly_variance hours from the weekly target
                if potential_week_hours > weekly_target + weekly_variance:
                    # This combo would violate weekly variance, skip it
                    continue

                # Calculate score - prefer balanced distribution and longer shifts
                total_fill = sum(shift_counts[day][code] for code in shift_codes)
                avg_fill = total_fill / len(shift_codes) if shift_codes else 0

                # Prefer longer combinations (lower score is better)
                length_bonus = -combo_hours * 2  # Prefer longer shifts

                # Balance score
                score = avg_fill * 5 + length_bonus

                if score < best_score:
                    best_score = score
                    best_combo = {
                        'day': day,
                        'shifts': shift_codes,
                        'hours': combo_hours
                    }

        return best_combo

    def assign_shift_combo_to_person(self, person, shift_combo, shift_counts):
        """Assign a shift combination to a person and update tracking"""
        day = shift_combo['day']
        shifts = shift_combo['shifts']
        hours = shift_combo['hours']

        # Add person to each shift
        for shift_code in shifts:
            self.temp_schedule[day][shift_code].append(person['name'])
            shift_counts[day][shift_code] += 1

        # Update person's scheduled hours
        self.hours_scheduled[person['name']] += hours

        # Update weekly hours tracking
        # Week 1: day indices 0-3 (Monday-Thursday Week 1)
        # Week 2: day indices 4-7 (Monday-Thursday Week 2)
        week_idx = self.day_names.index(day)
        if week_idx < 4:
            # Week 1
            self.week1_hours[person['name']] += hours
        else:
            # Week 2
            self.week2_hours[person['name']] += hours


    def display_schedule(self):
        # Clear previous display
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

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

        # Create vertical layout for 2 weeks
        # Week 1 section
        week1_label = tk.Label(main_container,
                              text="Week 1",
                              font=("Consolas", 12, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'],
                              pady=10)
        week1_label.pack(anchor=tk.W)

        week1_grid = tk.Frame(main_container, bg=self.colors['bg_dark'])
        week1_grid.pack(fill=tk.BOTH, expand=True, pady=(5, 20))

        # Configure week 1 grid (2x2)
        for i in range(2):
            week1_grid.columnconfigure(i, weight=1)
            week1_grid.rowconfigure(i, weight=1)

        # Week 1 days (indices 0-3)
        grid_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i in range(4):
            day = self.day_names[i]
            row, col = grid_positions[i]
            desks = self.desks_per_day[day]
            self.create_day_block(week1_grid, day, i, desks, row, col)

        # Week 2 section
        week2_label = tk.Label(main_container,
                              text="Week 2",
                              font=("Consolas", 12, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'],
                              pady=10)
        week2_label.pack(anchor=tk.W)

        week2_grid = tk.Frame(main_container, bg=self.colors['bg_dark'])
        week2_grid.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Configure week 2 grid (2x2)
        for i in range(2):
            week2_grid.columnconfigure(i, weight=1)
            week2_grid.rowconfigure(i, weight=1)

        # Week 2 days (indices 4-7)
        for i in range(4):
            day = self.day_names[i + 4]
            row, col = grid_positions[i]
            desks = self.desks_per_day[day]
            self.create_day_block(week2_grid, day, i + 4, desks, row, col)

        # Update canvas size to fit content
        self.schedule_frame.update_idletasks()
        self.update_schedule_canvas_size()

    def create_day_block(self, parent, day, day_idx, desks, row, col):
        """Create a single day schedule block using shift codes"""
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

        # Calculate heights for each shift (proportional to hours)
        shift_heights = {
            "0930": 90,   # 3h shift
            "1030": 60,   # 2h shift
            "1300": 75,   # 2.5h shift
            "1300F": 120  # 4h shift
        }
        total_height = sum(shift_heights.values())

        # Time column - use Canvas for exact positioning
        time_canvas = tk.Canvas(schedule_grid, width=60, height=total_height,
                               bg=self.colors['bg_dark'], highlightthickness=0)
        time_canvas.grid(row=0, column=0, sticky=(tk.N, tk.S), padx=(0, 5))

        # Add time labels for each shift (show full range)
        y_offset = 0
        for shift_code in self.timeslot_codes:
            shift_info = self.shift_definitions[shift_code]
            # Display full time range for clarity
            time_label = f"{shift_info['start']}-{shift_info['end']}"
            time_canvas.create_text(55, y_offset + 5, text=time_label,
                                   font=("Consolas", 8),
                                   fill=self.colors['text_muted'],
                                   anchor=tk.E)
            y_offset += shift_heights[shift_code]

        # Warning column - use Canvas for exact positioning
        warning_canvas = tk.Canvas(schedule_grid, width=50, height=total_height,
                                  bg=self.colors['bg_dark'], highlightthickness=0)
        warning_canvas.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(0, 5))

        # Calendar canvas
        canvas_frame = tk.Frame(schedule_grid, bg=self.colors['bg_dark'])
        canvas_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        schedule_grid.columnconfigure(2, weight=1)

        day_canvas = tk.Canvas(canvas_frame,
                              height=total_height,
                              bg=self.colors['bg_dark'],
                              highlightthickness=1,
                              highlightbackground=self.colors['border'])
        day_canvas.pack(fill=tk.BOTH, expand=True)

        # Count capacity and add warnings for each shift
        shift_counts = {code: 0 for code in self.timeslot_codes}

        if day in self.schedule:
            for person_name, person_data in self.schedule[day].items():
                for shift_code in person_data['shifts']:
                    shift_counts[shift_code] += 1

        # Add warning labels for understaffed shifts
        y_offset = 0
        for shift_code in self.timeslot_codes:
            if shift_counts[shift_code] < desks:
                warning_canvas.create_text(5, y_offset + 5,
                                         text=f"⚠ {shift_counts[shift_code]}/{desks}",
                                         font=("Consolas", 8),
                                         fill=self.colors['error'],
                                         anchor=tk.W)
            y_offset += shift_heights[shift_code]

        # Update canvas when it's sized
        def draw_schedule(event=None):
            canvas_width = day_canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = 400  # Default width

            day_canvas.delete("all")

            # Draw grid lines between shifts
            y_offset = 0
            for shift_code in self.timeslot_codes:
                day_canvas.create_line(0, y_offset, canvas_width, y_offset,
                                      fill=self.colors['border'],
                                      width=1)
                y_offset += shift_heights[shift_code]
            # Bottom line
            day_canvas.create_line(0, y_offset, canvas_width, y_offset,
                                  fill=self.colors['border'],
                                  width=1)

            # Draw schedule blocks
            if day in self.schedule:
                # Calculate block width
                block_width = (canvas_width - 10) / desks

                # Track lane assignments for each shift: {shift_code: [person_names]}
                shift_lanes = {code: [] for code in self.timeslot_codes}

                # Assign people to lanes
                people_shifts = list(self.schedule[day].items())
                people_shifts.sort(key=lambda x: x[1]['shifts'])

                for person_name, person_data in people_shifts:
                    shifts = person_data['shifts']

                    # Find a lane that's free for ALL shifts this person needs
                    assigned_lane = None
                    for lane_idx in range(desks):
                        # Check if this lane is free for all required shifts
                        lane_is_free = all(
                            lane_idx >= len(shift_lanes[shift_code]) or
                            shift_lanes[shift_code][lane_idx] is None
                            for shift_code in shifts
                        )

                        if lane_is_free:
                            assigned_lane = lane_idx
                            # Reserve this lane for all shifts
                            for shift_code in shifts:
                                # Extend the lane list if needed
                                while len(shift_lanes[shift_code]) <= lane_idx:
                                    shift_lanes[shift_code].append(None)
                                shift_lanes[shift_code][lane_idx] = person_name
                            break

                    if assigned_lane is None:
                        assigned_lane = 0

                    # Group non-overlapping shifts
                    # Morning shifts: 0930 (9:30-12:30), 1030 (10:30-12:30) - only one can be scheduled
                    # Afternoon shifts: 1300 (13:00-15:30), 1300F (13:00-17:00) - only one can be scheduled
                    shift_groups = []
                    morning_shifts = [s for s in shifts if s in ['0930', '1030']]
                    afternoon_shifts = [s for s in shifts if s in ['1300', '1300F']]

                    if morning_shifts:
                        shift_groups.append(morning_shifts)
                    if afternoon_shifts:
                        shift_groups.append(afternoon_shifts)

                    # Draw merged blocks for each group
                    for shift_group in shift_groups:
                        # Calculate merged block position
                        first_shift = shift_group[0]
                        last_shift = shift_group[-1]

                        # Find y positions
                        y1 = 3  # Start offset
                        for code in self.timeslot_codes:
                            if code == first_shift:
                                break
                            y1 += shift_heights[code]

                        y2 = y1
                        for shift_code in shift_group:
                            y2 += shift_heights[shift_code]
                        y2 -= 3  # End offset

                        # Calculate x position
                        x1 = 5 + (assigned_lane * block_width)
                        x2 = x1 + block_width - 5

                        # Get color
                        color = self.person_colors.get(person_name, self.colors['accent'])

                        # Draw merged rounded rectangle
                        radius = 8
                        self.draw_rounded_rect(day_canvas, x1, y1, x2, y2, radius,
                                              fill=color, outline=self.colors['border'], width=2)

                        # Add name and times
                        display_name = self.get_display_name(person_name)
                        start_time = self.shift_definitions[first_shift]['start']
                        end_time = self.shift_definitions[last_shift]['end']

                        # Calculate available space
                        available_width = x2 - x1 - 10
                        block_height = y2 - y1

                        # Font sizes
                        font_size = 9
                        font = ("Consolas", font_size, "bold")
                        time_font = ("Consolas", font_size - 1)

                        # Estimate text width
                        longest_text = max([display_name, start_time, end_time], key=len)
                        estimated_width = len(longest_text) * (font_size * 0.6)

                        # Reduce font size if needed
                        while estimated_width > available_width and font_size > 6:
                            font_size -= 1
                            font = ("Consolas", font_size, "bold")
                            time_font = ("Consolas", max(6, font_size - 1))
                            longest_text = max([display_name, start_time, end_time], key=len)
                            estimated_width = len(longest_text) * (font_size * 0.6)

                        # Truncate name if still too wide
                        final_name = display_name
                        if len(display_name) * (font_size * 0.6) > available_width:
                            max_chars = int(available_width / (font_size * 0.6)) - 3
                            if max_chars > 0:
                                final_name = display_name[:max_chars] + "..."

                        # Calculate vertical positions
                        center_x = (x1 + x2) / 2
                        line_spacing = font_size - 1

                        start_y = y1 + 8
                        name_y = start_y
                        time1_y = name_y + line_spacing + 3
                        dash_y = time1_y + line_spacing
                        time2_y = dash_y + line_spacing

                        # Draw text
                        day_canvas.create_text(center_x, name_y,
                                              text=final_name,
                                              fill=self.colors['bg_dark'],
                                              font=font)

                        day_canvas.create_text(center_x, time1_y,
                                              text=start_time,
                                              fill=self.colors['bg_dark'],
                                              font=time_font)

                        day_canvas.create_text(center_x, dash_y,
                                              text="-",
                                              fill=self.colors['bg_dark'],
                                              font=time_font)

                        day_canvas.create_text(center_x, time2_y,
                                              text=end_time,
                                              fill=self.colors['bg_dark'],
                                              font=time_font)


        day_canvas.bind('<Configure>', draw_schedule)
        day_canvas.after(100, draw_schedule)

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on canvas"""
        fill = kwargs.get('fill', '')
        outline = kwargs.get('outline', '')
        width = kwargs.get('width', 1)
        tags = kwargs.get('tags', ())

        # Draw filled rounded rectangle
        if fill:
            canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2,
                             start=90, extent=90, fill=fill, outline="", tags=tags)
            canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2,
                             start=0, extent=90, fill=fill, outline="", tags=tags)
            canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2,
                             start=180, extent=90, fill=fill, outline="", tags=tags)
            canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2,
                             start=270, extent=90, fill=fill, outline="", tags=tags)
            canvas.create_rectangle(x1+radius, y1, x2-radius, y2,
                                   fill=fill, outline="", tags=tags)
            canvas.create_rectangle(x1, y1+radius, x2, y2-radius,
                                   fill=fill, outline="", tags=tags)

        # Draw rounded outline
        if outline:
            canvas.create_arc(x1, y1, x1+radius*2, y1+radius*2,
                             start=90, extent=90, outline=outline, width=width, style='arc', tags=tags)
            canvas.create_arc(x2-radius*2, y1, x2, y1+radius*2,
                             start=0, extent=90, outline=outline, width=width, style='arc', tags=tags)
            canvas.create_arc(x1, y2-radius*2, x1+radius*2, y2,
                             start=180, extent=90, outline=outline, width=width, style='arc', tags=tags)
            canvas.create_arc(x2-radius*2, y2-radius*2, x2, y2,
                             start=270, extent=90, outline=outline, width=width, style='arc', tags=tags)
            canvas.create_line(x1+radius, y1, x2-radius, y1,
                              fill=outline, width=width, tags=tags)
            canvas.create_line(x1+radius, y2, x2-radius, y2,
                              fill=outline, width=width, tags=tags)
            canvas.create_line(x1, y1+radius, x1, y2-radius,
                              fill=outline, width=width, tags=tags)
            canvas.create_line(x2, y1+radius, x2, y2-radius,
                              fill=outline, width=width, tags=tags)

    def display_hours(self):
        # Clear previous display
        for widget in self.hours_frame.winfo_children():
            widget.destroy()

        # Calculate hours per week for each person
        week1_days = self.day_names[:4]  # Monday-Thursday Week 1
        week2_days = self.day_names[4:]  # Monday-Thursday Week 2

        hours_per_week = {}
        for person in self.people:
            name = person['name']
            week1_hours = 0
            week2_hours = 0

            for day in week1_days:
                if day in self.schedule and name in self.schedule[day]:
                    week1_hours += self.schedule[day][name]['hours']

            for day in week2_days:
                if day in self.schedule and name in self.schedule[day]:
                    week2_hours += self.schedule[day][name]['hours']

            hours_per_week[name] = {'week1': week1_hours, 'week2': week2_hours}

        # Create styled container
        container = tk.Frame(self.hours_frame, bg=self.colors['bg_dark'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Week 1 Section
        week1_title = tk.Label(container, text="Week 1 Hours",
                              font=("Consolas", 12, "bold"),
                              fg=self.colors['accent'],
                              bg=self.colors['bg_dark'])
        week1_title.grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=(0, 10))

        # Week 1 headers
        headers = ["Name", "Scheduled", "Preferred", "Agreed", "Max"]
        for col, header in enumerate(headers):
            header_label = tk.Label(container, text=header,
                                   font=("Consolas", 10, "bold"),
                                   fg=self.colors['text_secondary'],
                                   bg=self.colors['bg_dark'])
            header_label.grid(row=1, column=col, padx=15, pady=5, sticky=tk.W)

        # Week 1 separator
        separator1 = tk.Frame(container, height=1, bg=self.colors['border'])
        separator1.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 5))

        # Sort people by name
        sorted_people = sorted(self.people, key=lambda p: p['name'])

        # Display Week 1 hours
        current_row = 3
        for person in sorted_people:
            name = person['name']
            scheduled = hours_per_week[name]['week1']
            # Week hours are half of 2-week totals
            preferred = person['preferred_hours'] / 2
            agreed = person['agreed_hours'] / 2
            max_hours = person['max_hours'] / 2

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
            color_box.grid(row=current_row, column=0, sticky=tk.W, padx=(0, 5))

            # Name
            name_label = tk.Label(container, text=name,
                                 font=("Consolas", 10),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['bg_dark'])
            name_label.grid(row=current_row, column=0, padx=(10, 15), pady=4, sticky=tk.W)

            # Scheduled hours (colored)
            scheduled_label = tk.Label(container, text=f"{scheduled:.1f}h",
                                      font=("Consolas", 10, "bold"),
                                      fg=color,
                                      bg=self.colors['bg_dark'])
            scheduled_label.grid(row=current_row, column=1, padx=15, pady=4, sticky=tk.W)

            # Other hours
            for col, hours in enumerate([preferred, agreed, max_hours], start=2):
                label = tk.Label(container, text=f"{hours:.1f}h",
                               font=("Consolas", 10),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_dark'])
                label.grid(row=current_row, column=col, padx=15, pady=4, sticky=tk.W)

            current_row += 1

        # Week 2 Section (with spacing)
        current_row += 2
        week2_title = tk.Label(container, text="Week 2 Hours",
                              font=("Consolas", 12, "bold"),
                              fg=self.colors['accent'],
                              bg=self.colors['bg_dark'])
        week2_title.grid(row=current_row, column=0, columnspan=5, sticky=tk.W, pady=(10, 10))
        current_row += 1

        # Week 2 headers
        for col, header in enumerate(headers):
            header_label = tk.Label(container, text=header,
                                   font=("Consolas", 10, "bold"),
                                   fg=self.colors['text_secondary'],
                                   bg=self.colors['bg_dark'])
            header_label.grid(row=current_row, column=col, padx=15, pady=5, sticky=tk.W)
        current_row += 1

        # Week 2 separator
        separator2 = tk.Frame(container, height=1, bg=self.colors['border'])
        separator2.grid(row=current_row, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 5))
        current_row += 1

        # Display Week 2 hours
        for person in sorted_people:
            name = person['name']
            scheduled = hours_per_week[name]['week2']
            # Week hours are half of 2-week totals
            preferred = person['preferred_hours'] / 2
            agreed = person['agreed_hours'] / 2
            max_hours = person['max_hours'] / 2

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
            color_box.grid(row=current_row, column=0, sticky=tk.W, padx=(0, 5))

            # Name
            name_label = tk.Label(container, text=name,
                                 font=("Consolas", 10),
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['bg_dark'])
            name_label.grid(row=current_row, column=0, padx=(10, 15), pady=4, sticky=tk.W)

            # Scheduled hours (colored)
            scheduled_label = tk.Label(container, text=f"{scheduled:.1f}h",
                                      font=("Consolas", 10, "bold"),
                                      fg=color,
                                      bg=self.colors['bg_dark'])
            scheduled_label.grid(row=current_row, column=1, padx=15, pady=4, sticky=tk.W)

            # Other hours
            for col, hours in enumerate([preferred, agreed, max_hours], start=2):
                label = tk.Label(container, text=f"{hours:.1f}h",
                               font=("Consolas", 10),
                               fg=self.colors['text_secondary'],
                               bg=self.colors['bg_dark'])
                label.grid(row=current_row, column=col, padx=15, pady=4, sticky=tk.W)

            current_row += 1

        # Total Hours Section
        current_row += 1
        separator3 = tk.Frame(container, height=2, bg=self.colors['border'])
        separator3.grid(row=current_row, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 10))
        current_row += 1

        week1_total = sum(hours_per_week[p['name']]['week1'] for p in self.people)
        week2_total = sum(hours_per_week[p['name']]['week2'] for p in self.people)
        total_scheduled = week1_total + week2_total

        # Week 1 Total
        week1_label = tk.Label(container, text="Week 1 Total:",
                              font=("Consolas", 10, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'])
        week1_label.grid(row=current_row, column=0, padx=(10, 15), pady=4, sticky=tk.W)

        week1_value = tk.Label(container, text=f"{week1_total:.1f}h",
                              font=("Consolas", 10, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'])
        week1_value.grid(row=current_row, column=1, padx=15, pady=4, sticky=tk.W)
        current_row += 1

        # Week 2 Total
        week2_label = tk.Label(container, text="Week 2 Total:",
                              font=("Consolas", 10, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'])
        week2_label.grid(row=current_row, column=0, padx=(10, 15), pady=4, sticky=tk.W)

        week2_value = tk.Label(container, text=f"{week2_total:.1f}h",
                              font=("Consolas", 10, "bold"),
                              fg=self.colors['text_secondary'],
                              bg=self.colors['bg_dark'])
        week2_value.grid(row=current_row, column=1, padx=15, pady=4, sticky=tk.W)
        current_row += 1

        # Total (2 Weeks)
        total_label = tk.Label(container, text="Total (2 Weeks):",
                              font=("Consolas", 11, "bold"),
                              fg=self.colors['accent'],
                              bg=self.colors['bg_dark'])
        total_label.grid(row=current_row, column=0, padx=(10, 15), pady=8, sticky=tk.W)

        # Total hours value
        total_value = tk.Label(container, text=f"{total_scheduled:.1f}h",
                              font=("Consolas", 10, "bold"),
                              fg=self.colors['accent_hover'],
                              bg=self.colors['bg_dark'])
        total_value.grid(row=current_row, column=1, padx=15, pady=8, sticky=tk.W)

        # Update canvas size to fit content
        self.hours_frame.update_idletasks()
        self.update_hours_canvas_size()


def main():
    root = tk.Tk()
    app = SchedulingTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
