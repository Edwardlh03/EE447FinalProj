import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

# Load the latest ADC data
data = np.loadtxt("adc_data.csv", delimiter=",")

# Generate time axis
RATE = 1000  # Same sampling rate as ADC script
SAMPLES = len(data)
X = np.linspace(0, SAMPLES / RATE, SAMPLES)  # Time vector

# Normalize voltage data
Y = np.array(data)

# FFT Analysis
dt = X[1] - X[0]
yf = fft(Y, norm='forward')
freq = fftfreq(SAMPLES, d=dt)

# Detect peaks
height_threshold = 0.05
peaks_index, properties = find_peaks(np.abs(yf), height=height_threshold)

# Print frequency peaks
print('Peak Frequencies:')
for i in range(len(peaks_index)):
    print(f"{freq[peaks_index[i]]:.4f} Hz\t {properties['peak_heights'][i]:.4f}")

# Plot Results
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(X, Y)
plt.title("Time-Domain Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")

plt.subplot(1, 2, 2)
plt.plot(freq, np.abs(yf), '-', freq[peaks_index], properties['peak_heights'], 'x')
plt.xlabel("Frequency [Hz]")
plt.ylabel("Amplitude")
plt.title("Frequency Spectrum")

plt.tight_layout()
plt.show()


