from time import time, sleep
from sensorwriter import SensorWriter
import sensor_readers as sr

if __name__ == '__main__':
    # Hopefully more efficient than using dicts?
    sensor_fns = list(sr.SENSOR_READER_INTERVALS.keys())
    sensor_intervals = list(sr.SENSOR_READER_INTERVALS.values())
    next_read_times = [0] * len(sensor_intervals)

    min_interval = min(sensor_intervals)

    writer = SensorWriter(
        url=sr.DATABASE_URL,
        org=sr.DATABASE_ORG,
        bucket=sr.DATABASE_BUCKET,
        token=sr.DATABASE_TOKEN,
        id=sr.SENSOR_ID,
        commit_interval=sr.SENSOR_PUSH_INTERVAL,
        aggregate_window=min_interval,
    )
    print('Starting sensor data transmission')
    writer.start()

    try:
        print('Beginning sensor data reading...')
        while True:
            now = time()
            for i, nrt in enumerate(next_read_times):
                if now >= nrt:
                    next_read_times[i] = now + sensor_intervals[i]
                    sensor_fns[i](writer, now)
            sleep(min_interval)
    except KeyboardInterrupt:
        print('Keyboard interrupt detected, exiting...')

    sr.stop_reading()
    writer.stop()
