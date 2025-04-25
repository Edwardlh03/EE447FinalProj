import time
import board
import busio
import numpy as np
import math
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
from numpy.fft import fft, fftfreq
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

# === Configuration ===
SAMPLES    = 512    # power of two for FFT
RATE       = 860    # maximum for ADS1115
GAIN       = 1      # ADC gain
SEMITONE_TOLERANCE = 0.5  # ± tolerance in semitones

# Pre-compute note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

def freq_to_note(freq, tol=SEMITONE_TOLERANCE):
    """Map a frequency (Hz) to the nearest MIDI note if within tol semitones."""
    if freq <= 0:
        return None
    # MIDI note (float)
    m = 69 + 12 * math.log2(freq / 440.0)
    m_round = int(round(m))
    # How far off in semitones
    diff = abs(m - m_round)
    if diff <= tol and 100 <= freq <= 440:
        name = NOTE_NAMES[m_round % 12]
        octave = (m_round // 12) - 1
        return f"{name}{octave}"
    return None

# === Setup ADC ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.mode      = Mode.CONTINUOUS
ads.data_rate = RATE
ads.gain      = GAIN
chan          = AnalogIn(ads, ADS.P0)
_ = chan.value          # warm up
sample_interval = 1.0 / RATE

# === Setup LCD (BOARD numbering) ===
if GPIO.getmode() is None:
    GPIO.setmode(GPIO.BOARD)

lcd = CharLCD(
    pin_rs=37,
    pin_rw=None,
    pin_e=35,
    pins_data=[33, 31, 29, 23],
    numbering_mode=GPIO.BOARD,
    cols=16,
    rows=2
)

print(f"Sampling {SAMPLES} points at {RATE} SPS (~{SAMPLES/RATE:.2f}s window)")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        # — collect samples —
        data = []
        next_t = time.monotonic() + sample_interval
        for _ in range(SAMPLES):
            while time.monotonic() < next_t:
                pass
            data.append(chan.value)
            next_t += sample_interval

        # — to volts & zero-center —
        volts = np.array(data) * chan.voltage / chan.value
        volts -= volts.mean()

        # — FFT & find peak —
        spectrum = np.abs(fft(volts)[:SAMPLES//2])
        freqs    = fftfreq(SAMPLES, d=1.0/RATE)[:SAMPLES//2]
        idx      = int(np.argmax(spectrum))
        peak_hz  = freqs[idx]

        # — map to note —
        note = freq_to_note(peak_hz)
        display = note if note else "--"

        print(f"Detected: {peak_hz:.1f} Hz → {display}")

        # — update LCD —
        lcd.clear()
        lcd.write_string("Note:")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(display)

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopped.")


