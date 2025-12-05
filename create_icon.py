#!/usr/bin/env python3
"""Generate a grey and green calendar icon for the scheduling application."""

from PIL import Image, ImageDraw, ImageFont

# Create a 256x256 icon (good resolution for desktop icons)
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Colors
grey = '#4a4a4a'
dark_grey = '#2a2a2a'
green = '#5eb56e'
white = '#e8e8e8'

# Draw calendar background (rounded rectangle)
padding = 20
calendar_rect = [padding, padding + 30, size - padding, size - padding]
draw.rounded_rectangle(calendar_rect, radius=20, fill=grey, outline=dark_grey, width=4)

# Draw calendar header (green bar at top)
header_rect = [padding, padding + 30, size - padding, padding + 80]
draw.rounded_rectangle(header_rect, radius=20, fill=green)
# Cover bottom corners of header to make it rectangular
draw.rectangle([padding, padding + 60, size - padding, padding + 80], fill=green)

# Draw binding rings at top (two small circles)
ring1_center = (size // 2 - 40, padding + 15)
ring2_center = (size // 2 + 40, padding + 15)
ring_radius = 12
draw.ellipse([ring1_center[0] - ring_radius, ring1_center[1] - ring_radius,
              ring1_center[0] + ring_radius, ring1_center[1] + ring_radius],
             fill=green, outline=dark_grey, width=3)
draw.ellipse([ring2_center[0] - ring_radius, ring2_center[1] - ring_radius,
              ring2_center[0] + ring_radius, ring2_center[1] + ring_radius],
             fill=green, outline=dark_grey, width=3)

# Draw grid lines for calendar days (3x3 grid)
grid_start_y = padding + 100
grid_height = size - padding - grid_start_y - 20
cell_width = (size - 2 * padding - 40) / 3
cell_height = grid_height / 3

for i in range(1, 3):
    # Vertical lines
    x = padding + 20 + i * cell_width
    draw.line([(x, grid_start_y), (x, size - padding - 20)], fill=dark_grey, width=2)
    # Horizontal lines
    y = grid_start_y + i * cell_height
    draw.line([(padding + 20, y), (size - padding - 20, y)], fill=dark_grey, width=2)

# Draw some dots in calendar cells (representing scheduled days)
dot_positions = [
    (1, 0), (2, 0),  # Top row
    (0, 1), (1, 1),  # Middle row
    (1, 2), (2, 2)   # Bottom row
]
for col, row in dot_positions:
    center_x = padding + 20 + col * cell_width + cell_width / 2
    center_y = grid_start_y + row * cell_height + cell_height / 2
    dot_radius = 8
    draw.ellipse([center_x - dot_radius, center_y - dot_radius,
                  center_x + dot_radius, center_y + dot_radius],
                 fill=green)

# Save as PNG (for Linux desktop icon)
img.save('/home/user/B2.0Schedulingtool/scheduler_icon.png')
print("Icon created: scheduler_icon.png")

# Create smaller version for window icon (32x32)
img_small = img.resize((32, 32), Image.Resampling.LANCZOS)
img_small.save('/home/user/B2.0Schedulingtool/scheduler_icon_small.png')
print("Small icon created: scheduler_icon_small.png")
