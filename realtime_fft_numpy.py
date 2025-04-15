import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
from numpy.fft import fft, fftfreq  # Use numpy's FFT functions
from RPLCD import CharLCD

# === Configuration ===
SAMPLES = 512        # Must be a power of 2 for FFT
RATE = 860           # Maximum for ADS1115
GAIN = 1             # Gain setting for ADS1115 (adjust if needed)
PLOT = False         # Set to True to display the FFT spectrum

# === Setup ADC ===
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE
ads.gain = GAIN
chan = AnalogIn(ads, ADS.P0)
lcd = CharLCD(Cols=16, rows=2, pins_rs=37, pin_e=35, pins_data= [33, 31, 29, 23])
lcd.write_string(u'initial')
time.sleep(0.5)
lcd.clear()
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
	temp_freq = str(round(f,1))
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

