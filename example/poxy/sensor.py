from influxdbwriter.sensorwriter import SensorWriter
from max30102.heartrate_monitor import HeartRateMonitor
import time
import numpy as np
import sys
sys.path.append('../')

writer = SensorWriter(
    url='url',
    org='Eksperter i Team Gruppe 2',
    bucket='Test',
    token='token',
    id=42069,
    commit_interval=2,
)
writer.start()

hrm = HeartRateMonitor()
hrm.start_sensor()

try:
    while True:
        time.sleep(1)

        spo2 = hrm.latest_spo2()
        if spo2 is None:
            continue
        print('SpO2:', spo2)

        writer.add_data('spo2', spo2)
        t = time.time_ns()
        writer.add_data('rando', 36.5 + (0.5 * np.sin((t / 1e9) / 50)) + np.random.uniform(-0.5, 0.5))

except KeyboardInterrupt:
    print('keyboard interrupt detected, exiting...')

hrm.stop_sensor()
writer.stop()