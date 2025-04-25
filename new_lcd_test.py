from PIL import Image
from ST7735 import ST7735  # Make sure you installed the right st7735 library
import RPi.GPIO as GPIO
import time

# Software SPI pin setup
DC = 19       # Data/Command
RST = 26      # Reset
CS = 13       # Chip Select
SCLK = 6      # Clock
MOSI = 5      # Data

# Create ST7735 display instance with software SPI
disp = ST7735(
    port=None,    # None means software SPI
    cs=CS,
    dc=DC,
    rst=RST,
    sclk=SCLK,
    mosi=MOSI,
    spi_speed_hz=4000000,  # 4 MHz, safe
    width=128,
    height=160,
    rotation=0,
    invert=False
)

# Initialize the display
disp.begin()

# Create a blank image (solid color)
image = Image.new('RGB', (128, 160), (0, 255, 0))  # Green screen

# Display the image
disp.display(image)

print("Screen should now be solid GREEN.")
time.sleep(10)  # Hold screen for 10 seconds
