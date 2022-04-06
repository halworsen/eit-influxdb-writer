
from .max30102 import MAX30102
from .hrcalc import calc_hr_and_spo2
import threading
import time
import numpy as np

class RingBuffer:
    def __init__(self, size):
        if size is None:
            raise ValueError('Buffer size must be specified')
        self.size = size
        self.buf = [None] * size
        self.head = 0
    
    def push(self, val):
        self.buf[self.head] = val
        self.head = (self.head + 1) % self.size

    def pop(self):
        val = self.buf[self.head]
        if val is None:
            return None
        self.buf[self.head] = None
        self.head = (self.head - 1) % self.size
        return val

class HeartRateMonitor(object):
    """
    A class that encapsulates the max30102 device into a thread
    """

    LOOP_TIME = 0.01

    def __init__(self):
        self.bpm = 0
        self.buffer = RingBuffer(10)
    
    def latest_spo2(self):
        return self.buffer.pop()

    def run_sensor(self):
        sensor = MAX30102()
        ir_data = []
        red_data = []
        bpms = []

        # run until told to stop
        while not self._thread.stopped:
            # check if any data is available
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                        self.bpm = 0
                        self.buffer.push(0)
                    else:
                        bpm, valid_bpm, spo2, valid_spo2 = calc_hr_and_spo2(ir_data, red_data)
                        if valid_bpm:
                            bpms.append(bpm)
                            while len(bpms) > 4:
                                bpms.pop(0)
                            self.bpm = np.mean(bpms)

                            if valid_spo2:
                                # Push SpO2 value to buffer
                                self.buffer.push(spo2)

            time.sleep(self.LOOP_TIME)

        sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.bpm = 0
        self._thread.join(timeout)
