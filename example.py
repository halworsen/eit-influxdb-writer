from time import time_ns, sleep
from sensorwriter import SensorWriter
from scipy.misc import electrocardiogram
import numpy as np

# load an example ECG. the example is 5 minutes long and recorded at 360Hz
ecg = electrocardiogram()
ecg_ts = np.arange(ecg.size) / 360

# simulation of reading from the ecg sensor. in reality, time wouldn't be relevant
def read_ecg(t):
    # modulo into range
    ecg_t = (t / 1e9) % (5 * 60)
    # read the value that's closest in time
    closest_idx = np.abs(ecg_ts - ecg_t).argmin()
    return ecg[closest_idx]

# simulate reading temperature
# just a sine wave around 36.5C with some random noise
read_temperature = lambda t: 36.5 + (0.5 * np.sin((t / 1e9) / 50)) + np.random.uniform(-0.5, 0.5)

# simulate reading oxygen saturation
def read_sao2(t):
    arterial = 97.5 + 1 * np.sin((t/1e9)/10) + np.random.uniform(-1, 1)
    venous = 75 + 3 * np.sin((t/1e9)/10) + np.random.uniform(-3, 3)
    return {'arterial': arterial, 'venous': venous}

###############################################################
### Everything above this is not relevant to database usage ###
### It's just for generating random sensor "readings"       ###
###############################################################

writer = SensorWriter(
    'influxdburl.com:8086',
    'organization name',
    'data bucket name',
    'api token'
)

# This patient ID is just an arbitrary example
patient_id = 69535

# Buffer the data to send it in batch at regular intervals
data_buffer = []
next_write = 0
next_misc_read = 0

while True:
    now = time_ns()
    measurements = {}

    # Dump the data buffer into the database if it's time to do so
    if now >= next_write:
        # Write once every 2 seconds
        next_write = now + (2 * 1e9)
        writer.write('patient_vitals', patient_id, data_buffer)
        # Clear the buffer
        data_buffer = []

    # "Read" ECG all the time
    measurements['ecg'] = read_ecg(now)

    # Read other stuff less frequently
    if now >= next_misc_read:
        next_misc_read = now + (1 * 1e9)
        # "Read" temperature
        measurements['temperature'] = read_temperature(now)
        # Same thing for oxygen saturation
        sao2 = read_sao2(now)
        measurements['sao2_arterial'] = sao2['arterial']
        measurements['sao2_venous'] = sao2['venous']

    # Add the timestamp and add the readings to the buffer
    data_point = (now, measurements)
    data_buffer.append(data_point)

    # Sleep a *little*. It's important that we don't sleep for too long, or it will harm ECG time resolution.
    # In this case, the ECG is captured at 360Hz.
    # This means that to get full resolution, we can't sleep for longer than 1/360s ~ 2.8ms
    sleep(2.8 / 1000)
