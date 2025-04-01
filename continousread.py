import time
import board
import busio
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.ads1x15 import Mode
from adafruit_ads1x15.analog_in import AnalogIn

# Sampling configuration
RATE = 1000  # Sampling rate in Hz
DURATION = 5  # Collect data for 5 seconds
SAMPLES = RATE * DURATION  # Total samples per cycle

# Initialize I2C and ADC
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
ads = ADS.ADS1115(i2c)
chan0 = AnalogIn(ads, ADS.P0)

# Configure ADC
ads.mode = Mode.CONTINUOUS
ads.data_rate = RATE

# Initial read to configure the ADC
_ = chan0.value
sample_interval = 1.0 / RATE

while True:
    data = np.zeros(SAMPLES)  # Initialize data array
    start_time = time.monotonic()
    time_next_sample = start_time + sample_interval

    print("Collecting data for 5 seconds...")

    for i in range(SAMPLES):
        while time.monotonic() < time_next_sample:
            pass  # Wait for the next sample time

        data[i] = chan0.value  # Read ADC value
        time_next_sample += sample_interval

    end_time = time.monotonic()
    print(f"Data collection complete in {end_time - start_time:.2f} seconds.")

    # Convert ADC values to voltage
    voltage_data = data * (4.096 / 32767)

    # Save or pass data for FFT analysis
    np.savetxt("adc_data.csv", voltage_data, delimiter=",")
    
    # Call FFT script automatically (optional, can be done externally)
    import subprocess
    subprocess.run(["python3", "peakfreqfinder.py"])

    # Pause for a moment before next cycle (if needed)
    time.sleep(1)


