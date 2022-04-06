from heartrate_monitor import HeartRateMonitor
import time
import argparse

parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true",
                    help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=30,
                    help="duration in seconds to read from sensor, default 30")
args = parser.parse_args()

print('sensor starting...')
hrm = HeartRateMonitor()
hrm.start_sensor()
try:
    for i in range(10):
        spo2 = hrm.latest_spo2()
        if spo2 is None:
            time.sleep(args.time / 10)
            continue
        print('SpO2:', hrm.latest_spo2())
        time.sleep(args.time / 10)
except KeyboardInterrupt:
    print('keyboard interrupt detected, exiting...')

hrm.stop_sensor()
print('sensor stoped!')