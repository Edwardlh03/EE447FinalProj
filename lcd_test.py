from PIL import Image, ImageDraw, ImageFont
from st7735 import ST7735
import time
import spidev
import RPi.GPIO as GPIO

# Pin configuration (change if you used different GPIOs)
DC = 24      # Data/Command
RST = 25     # Reset
CS = 8       # SPI0 CE0

# Create ST7735 LCD display class
disp = ST7735(
    port=0,
    cs=CS,
    dc=DC,
    rst=RST,
    backlight=None,  # Set to GPIO if using a GPIO to control backlight
    width=128,
    height=160,
    rotation=90,     # or 0 or 180 depending on your wiring
    invert=False
)

# Initialize display
disp.begin()

# Clear display (black)
img = Image.new('RGB', (128, 160), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw red rectangle
draw.rectangle((10, 10, 100, 50), fill=(255, 0, 0))

# Draw text
font = ImageFont.load_default()
draw.text((15, 20), "Hello, world!", font=font, fill=(255, 255, 255))

# Display image
disp.display(img)

# Keep it on screen
time.sleep(10)