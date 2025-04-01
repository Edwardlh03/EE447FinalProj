import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

# Import ADC script or read data from it
from adc_script import data, SAMPLES, RATE  # Import data from the second script

# Generate time axis based on sampling rate
X = np.arange(0, SAMPLES / RATE, 1 / RATE)  # Create time vector

# Convert raw ADC data (Assuming single-ended mode, 16-bit ADC, and 4.096V reference)
Y = np.array(data) * (4.096 / 32767)  # Normalize ADC readings to voltage

# Create a dataframe
dummy_data = pd.DataFrame({'X': X, 'Y': Y})

print('Dummy dataframe: ')
print(dummy_data.head())

# Plot raw signal
plt.plot(X, Y)
plt.title('Collected Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.show()

# ----------------------------------------------------
# FFT Processing
dt = X[1] - X[0]  # Time step
n = len(X)  # Number of points

yf = fft(Y, norm='forward')  # Fourier Transform
freq = fftfreq(n, d=dt)  # Frequency axis

# Detect peaks
height_threshold = 0.05
peaks_index, properties = find_peaks(np.abs(yf), height=height_threshold)

# Print frequency peaks
print('Positions and magnitude of frequency peaks:')
for i in range(len(peaks_index)):
    print(f"{freq[peaks_index[i]]:.4f} Hz\t {properties['peak_heights'][i]:.4f}")

# Plot FFT result
plt.plot(freq, np.abs(yf), '-', freq[peaks_index], properties['peak_heights'], 'x')
plt.xlabel("Frequency [Hz]")
plt.ylabel("Amplitude")
plt.title("Frequency Spectrum")
plt.show()

