#!/usr/bin/env python3
"""Convert PNG icon to ICO format for Windows shortcuts."""

from PIL import Image

# Load the PNG icon
img = Image.open('/home/user/B2.0Schedulingtool/scheduler_icon.png')

# Windows ICO format supports multiple sizes
# Create different sizes for better display at different resolutions
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# Resize and save as ICO with multiple sizes
icon_images = []
for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icon_images.append(resized)

# Save as ICO file
icon_images[0].save(
    '/home/user/B2.0Schedulingtool/scheduler_icon.ico',
    format='ICO',
    sizes=[(img.width, img.height) for img in icon_images],
    append_images=icon_images[1:]
)

print("Windows icon created: scheduler_icon.ico")
print("You can now use this .ico file for Windows shortcuts!")
