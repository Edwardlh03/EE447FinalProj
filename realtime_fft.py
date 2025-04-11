import time
import board
import busio
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

# === Config ===
SAMPLES = 512        # Must be power of 2 for FFT
RATE = 860           # Max for ADS1115
GAIN = 1             # Gain for ADS1115 (adjust if needed)
PLOT = False         # Set to True to visualize the spectrum

# === Setup ADC ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE
ads.gain = GAIN
chan = AnalogIn(ads, ADS.P0)

# Warm-up read
_ = chan.value
sample_interval = 1.0 / RATE

print(f"Sampling {SAMPLES} points at {RATE} sps (approx. {SAMPLES/RATE:.2f} seconds window)")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        # === Collect Samples ===
        data = []
        next_sample_time = time.monotonic() + sample_interval
        for _ in range(SAMPLES):
            while time.monotonic() < next_sample_time:
                pass
            val = chan.value
            data.append(val)
            next_sample_time += sample_interval

        # === Convert to volts (optional) ===
        voltages = [v * chan.voltage / chan.value for v in data]

        # === Preprocess ===
        samples = np.array(voltages)
        samples -= np.mean(samples)  # Zero-center

        # === FFT ===
        fft_vals = fft(samples)
        fft_vals = np.abs(fft_vals[:SAMPLES // 2])
        freqs = np.fft.fftfreq(SAMPLES, d=1.0 / RATE)[:SAMPLES // 2]

        # === Peak Frequency ===
        peak_idx = np.argmax(fft_vals)
        peak_freq = freqs[peak_idx]
        print(f"Peak frequency: {peak_freq:.2f} Hz")

        # === Optional: Plot FFT ===
        if PLOT:
            plt.clf()
            plt.plot(freqs, fft_vals)
            plt.title(f"Live Spectrum - Peak: {peak_freq:.2f} Hz")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel("Amplitude")
            plt.grid(True)
            plt.pause(0.01)

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nStopped.")


