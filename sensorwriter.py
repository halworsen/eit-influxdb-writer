from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import threading

class SensorWriter:
    '''
    Wrapper class for writing sensor data to InfluxDB
    '''

    def __init__(self,
        url: str,
        org: str,
        bucket: str,
        token: str,
        id: int,
        commit_interval: int,
        aggregate_window: int,
    ):
        '''
        Args:
            url: The URL of the InfluxDB to write to
            org: The organization to write data to
            bucket: The data bucket to write to
            token: API authentication token
            id: Sensor pack ID
            commit_interval: How often to write data batches to the database
            aggregate_window: All added data within this time interval are aggregated together. In seconds.
        '''
        self.db_url = url
        self.org = org
        self.bucket = bucket
        self.token = token
        self.sensor_id = id
        self.commit_interval = commit_interval
        self.aggregate_window = aggregate_window
        self.measurement_name = 'sensorpack'

        self.cur_timestamp = 0
        self.cur_data = {}
        self.data = []

        self._thread = None
        self.client = InfluxDBClient(url=url, token=token, org=org)

    def start(self):
        '''
        Start writing data to the database
        '''
        self._thread = threading.Thread(target=self._write_loop)
        self._thread.stopped = False
        self._thread.start()

    def stop(self):
        '''
        Stop writing data to the database
        '''
        self._thread.stopped = True
        self._thread.join(self.commit_interval + 1.0)

    def _write_loop(self):
        '''
        INTERNAL: Continually send data in batch to InfluxDB
        '''
        while not self._thread.stopped:
            time.sleep(self.commit_interval)

            if not len(self.data):
                continue

            api = self.client.write_api(write_options=SYNCHRONOUS)

            records = []
            for measurement in self.data:
                p = Point(self.measurement_name).tag('id', self.sensor_id).time(measurement[0])
                for k,v in measurement[1].items():
                    p.field(k, v)
                records.append(p)

            api.write(bucket=self.bucket, org=self.org, record=records)
            self.data = []

    def add_data(self, label: str, value: int):
        '''
        Add a single data point

        Args:
            label: Data label. What sensor is this from?
            value: Actual data. The associated sensor value
        '''
        value = float(value)
        # Round the nanosecond timestamp down to the start of the current aggregate window
        window_ns = self.aggregate_window / 1e9
        now = int((time.time_ns() // window_ns) * window_ns)
        if self.cur_timestamp != now:
            if len(self.cur_data):
                data_point = (self.cur_timestamp, self.cur_data)
                self.data.append(data_point)

            self.cur_data = {}
            self.cur_timestamp = now

        self.cur_data[label] = value
