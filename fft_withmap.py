import time, board, busio 
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
from numpy.fft import fft, fftfreq


# === Configuration (must be first!) ===
SAMPLES = 512
RATE    = 860
GAIN    = 1
SEMITONE_TOLERANCE = 0.5 
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

print("A: imports and config done")

# === Setup ADC ===
print("B: initializing I2C…")
i2c = busio.I2C(board.SCL, board.SDA)
print("C: I2C ready")

print("D: initializing ADS1115…")
ads = ADS.ADS1115(i2c)
print("E: ADS ready — setting mode & rate")
ads.mode      = Mode.CONTINUOUS
ads.data_rate = RATE       # now RATE is defined
ads.gain      = GAIN
chan          = AnalogIn(ads, ADS.P0)
print("F: ADS configured, now LCD…")




print("I: preparing GPIO/LCD setup")
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

# No explicit setmode(); Blinka set BCM already.

lcd = CharLCD(
    pin_rs=26,           # BCM 26 = physical 37
    pin_rw=None,
    pin_e=19,            # BCM 19 = physical 35
    pins_data=[13, 6, 5, 11],  # BCM 13,6,5,11 = physical 33,31,29,23
    numbering_mode=GPIO.BCM,
    cols=16,
    rows=2,
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
