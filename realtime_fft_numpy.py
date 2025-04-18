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


import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD

print("I: preparing GPIO/LCD setup")
# Optional: clear out any previous state so we can set mode cleanly
GPIO.cleanup()

# Try to set BOARD mode, but if it was already set by blinka or another import, ignore the error
try:
    GPIO.setmode(GPIO.BOARD)
    print("J: GPIO mode set to BOARD")
except ValueError:
    # mode was already set to something—just reuse it
    current = GPIO.getmode()
    print(f"J: GPIO mode already set (mode={current}), skipping setmode()")

# Now instantiate the LCD using that same numbering mode
mode = GPIO.getmode() or GPIO.BOARD
lcd = CharLCD(
    pin_rs=37,
    pin_rw=None,            # if RW is not wired
    pin_e=35,
    pins_data=[33, 31, 29, 23],
    numbering_mode=mode,
    cols=16,
    rows=2,
)
print("K: LCD ready!")



# Warm-up read
_ = chan.value
sample_interval = 1.0 / RATE

print(f"Sampling {SAMPLES} points at {RATE} sps (approx. {SAMPLES / RATE:.2f} seconds window)")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        # === Collect Samples ===
        data = []
        next_sample_time = time.monotonic() + sample_interval
        for _ in range(SAMPLES):
            # Wait until it's time for the next sample
            while time.monotonic() < next_sample_time:
                pass
            val = chan.value
            data.append(val)
            next_sample_time += sample_interval

        # === Convert raw data to voltage (optional conversion) ===
        # Here, we use the relation: raw_value * (chan.voltage / chan.value)
        # This scaling assumes linearity across the ADC range.
        voltages = [v * chan.voltage / chan.value for v in data]

        # === Preprocess: Zero-center the signal ===
        samples = np.array(voltages)
        samples -= np.mean(samples)

        # === Compute FFT using NumPy ===
        fft_vals = fft(samples)
        fft_vals = np.abs(fft_vals[:SAMPLES // 2])  # Single-sided FFT (magnitude)
        freqs = fftfreq(SAMPLES, d=1.0 / RATE)[:SAMPLES // 2]  # Frequency bins

        # === Identify Peak Frequency ===
        peak_idx = np.argmax(fft_vals)
        peak_freq = freqs[peak_idx]
        print(f"Peak frequency: {peak_freq:.2f} Hz")
        temp_freq = str(round(peak_freq, 1))
        lcd.write_string("frequency:" + temp_freq)
        # === Optional: Plot the FFT Spectrum ===
        #if PLOT:
         #   plt.clf()
          #  plt.plot(freqs, fft_vals)
           # plt.title(f"Live Spectrum - Peak: {peak_freq:.2f} Hz")
            #plt.xlabel("Frequency (Hz)")
            #plt.ylabel("Amplitude")
            #plt.grid(True)
            #plt.pause(0.01)

        # Short pause between iterations
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopped.")

