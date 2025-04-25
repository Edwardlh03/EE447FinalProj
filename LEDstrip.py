import time, board, busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
from numpy.fft import fft, fftfreq
import math
import neopixel   # <--- new
import colorsys   # <--- for rainbow

# === Configuration (must be first!) ===
SAMPLES = 512
RATE = 860
GAIN = 1
PIXEL_PIN = board.D18       # GPIO18 (physical 12) is common for Neopixels
NUM_PIXELS = 144             # Set to however many LEDs are in your strip

# WS2812B strip setup
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5, auto_write=False)

# Tolerance and lookup for note mapping
SEMITONE_TOLERANCE = 0.5
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(freq, tol=SEMITONE_TOLERANCE):
    """Map a frequency (Hz) to the nearest note name within tol semitones, if 100–440 Hz."""
    if freq <= 0:
        return None
    m = 69 + 12 * math.log2(freq / 440.0)
    m_round = int(round(m))
    if abs(m - m_round) <= tol and 100 <= freq <= 440:
        name = NOTE_NAMES[m_round % 12]
        octave = (m_round // 12) - 1
        return f"{name}{octave}"
    return None

print("A: imports and config done")

# === Setup ADC ===
print("B: initializing I2C…")
i2c = busio.I2C(board.SCL, board.SDA)
print("C: I2C ready")

print("D: initializing ADS1115…")
ads = ADS.ADS1115(i2c)
print("E: ADS ready — setting mode & rate")
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE
ads.gain = GAIN
chan = AnalogIn(ads, ADS.P0)
print("F: ADS configured, now LCD…")

print("I: preparing GPIO/LCD setup")
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

lcd = CharLCD(
    pin_rs=26,
    pin_rw=None,
    pin_e=19,
    pins_data=[13, 6, 5, 11],
    numbering_mode=GPIO.BCM,
    cols=16, rows=2,
)

print("K: LCD ready!")

# Warm-up read
_ = chan.value
sample_interval = 1.0 / RATE

print(f"Sampling {SAMPLES} points at {RATE} sps (approx. {SAMPLES / RATE:.2f} seconds window)")
print("Press Ctrl+C to stop.\n")

print("H: entering while")
try:
    while True:
        # === Collect Samples ===
        data = []
        next_sample_time = time.monotonic() + sample_interval
        for _ in range(SAMPLES):
            while time.monotonic() < next_sample_time:
                pass
            data.append(chan.value)
            next_sample_time += sample_interval

        # === Convert to volts & zero-center ===
        voltages = np.array(data) * chan.voltage / chan.value
        voltages -= voltages.mean()

        # === FFT & find peak ===
        fft_vals = np.abs(fft(voltages)[:SAMPLES // 2])
        freqs = fftfreq(SAMPLES, d=1.0 / RATE)[:SAMPLES // 2]
        peak_idx = int(np.argmax(fft_vals))
        peak_freq = freqs[peak_idx]

        # === Map frequency to note (or “--” if out of range) ===
        note = freq_to_note(peak_freq)
        display = note if note else "--"

        print(f"Detected: {peak_freq:.1f} Hz → {display}")

        # === Update LCD ===
        lcd.clear()
        time.sleep(0.05)
        lcd.write_string(display.ljust(16))
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"{peak_freq:5.1f} Hz".ljust(16))

        # === Update LEDs based on frequency ===
        # Map frequency (0–430 Hz) to number of pixels lit
        if peak_freq < 0:
            peak_freq = 0
        if peak_freq > 430:
            peak_freq = 430
        fraction = peak_freq / 430
        num_lit = int(fraction * NUM_PIXELS)

        # Fill LEDs with rainbow
        for i in range(NUM_PIXELS):
            hue = i / NUM_PIXELS  # 0 to 1 across strip
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(r*255), int(g*255), int(b*255))
            if i < num_lit:
                pixels[i] = color
            else:
                pixels[i] = (0, 0, 0)  # off

        pixels.show()

        # Short pause between iterations
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopped.")
    pixels.fill((0, 0, 0))
    pixels.show()
