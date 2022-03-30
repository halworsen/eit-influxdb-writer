from scipy.misc import electrocardiogram
import numpy as np

# load an example ECG. the example is 5 minutes long and recorded at 360Hz
ecg = electrocardiogram()
ecg_ts = np.arange(ecg.size) / 360

# simulation of reading from the ecg sensor. in reality, time wouldn't be relevant
def example_ecg(t):
    # modulo into range
    ecg_t = t % (5 * 60)
    # read the value that's closest in time
    closest_idx = np.abs(ecg_ts - ecg_t).argmin()
    return ecg[closest_idx]

# simulate reading temperature
# just a sine wave around 36.5C with some random noise
example_temperature = lambda t: 36.5 + (0.5 * np.sin(t / 50)) + np.random.uniform(-0.5, 0.5)

# simulate reading oxygen saturation
def example_sao2(t):
    arterial = 97.5 + 1 * np.sin(t/10) + np.random.uniform(-1, 1)
    venous = 75 + 3 * np.sin(t/10) + np.random.uniform(-3, 3)
    return {'arterial': arterial, 'venous': venous}
