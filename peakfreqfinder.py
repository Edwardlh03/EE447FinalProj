import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

# First: Let's generate a dummy dataframe with X,Y
# The signal consists in 3 cosine signals with noise added. We terminate by creating
# a pandas dataframe.

import numpy as np
X=np.arange(start=0,stop=20,step=0.01) # 20 seconds long signal sampled every 0.01[s]

# Signal components given by [frequency, phase shift, Amplitude]
GeneratedSignal=np.array([[5.50, 1.60, 1.0], [10.2, 0.25, 0.5], [18.3, 0.70, 0.2]])

Y=np.zeros(len(X))
# Let's add the components one by one
for P in GeneratedSignal:
    Y+=np.cos(2*np.pi*P[0]*X-P[1])*P[2] 

# Let's add some gaussian random noise (mu=0, sigma=noise):
noise=0.5
Y+=np.random.randn(len(X))*noise

# Let's build the dataframe:
dummy_data=pd.DataFrame({'X':X,'Y':Y})
print('Dummy dataframe: ')
print(dummy_data.head())

# Figure-1: The dummy data

plt.plot(X,Y)
plt.title('Dummy data')
plt.xlabel('time [s]')
plt.ylabel('Amplitude')
plt.show()

# ----------------------------------------------------
# Processing:

headers = ["X","Y"]

#original_data = pd.read_csv("testdata.csv",names=headers)
# Let's take our dummy data:

original_data = dummy_data

x = np.array(original_data["X"])
y = np.array(original_data["Y"])


# Assuming the time step is constant:
# (otherwise you'll need to resample the data at a constant rate).
dt=x[1]-x[0]  # time step of the data

# The fourier transform of y:
yf=fft(y, norm='forward')  
# Note: see  help(fft) --> norm. I chose 'forward' because it gives the amplitudes we put in.
# Otherwise, by default, yf will be scaled by a factor of n: the number of points


# The frequency scale
n = x.size   # The number of points in the data
freq = fftfreq(n, d=dt)

# Let's find the peaks with height_threshold >=0.05
# Note: We use the magnitude (i.e the absolute value) of the Fourier transform

height_threshold=0.05 # We need a threshold. 


# peaks_index contains the indices in x that correspond to peaks:

peaks_index, properties = find_peaks(np.abs(yf), height=height_threshold)

# Notes: 
# 1) peaks_index does not contain the frequency values but indices
# 2) In this case, properties will contain only one property: 'peak_heights'
#    for each element in peaks_index (See help(find_peaks) )

# Let's first output the result to the terminal window:
print('Positions and magnitude of frequency peaks:')
[print("%4.4f    \t %3.4f" %(freq[peaks_index[i]], properties['peak_heights'][i])) for i in range(len(peaks_index))]


# Figure-2: The frequencies

plt.plot(freq, np.abs(yf),'-', freq[peaks_index],properties['peak_heights'],'x')
plt.xlabel("Frequency")
plt.ylabel("Amplitude")
plt.show()
