from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class SensorWriter:
    '''
    Wrapper class for writing sensor data to InfluxDB
    '''

    def __init__(self, url: str, org: str, bucket: str, token: str):
        '''
        Args:
            url: The URL of the InfluxDB to write to
            org: The organization to write data to
            bucket: The data bucket to write to
            token: API authentication token
        '''
        self.db_url = url
        self.org = org
        self.bucket = bucket
        self.token = token

        self.client = InfluxDBClient(url=url, token=token, org=org)

    def write(self, label: str, id: int, data: list):
        '''
        Write a batch of data to InfluxDB.

        Args:
            label: Data label. What is this data describing.
            id: ID to discriminate different data series with, should be unique.
            data: A list of sets, each containing a timestamp and a dictionary of labeled data points.

        Example:
            writer.write(
                label='example_data',
                id=324723,
                data=[
                    (1646212483818387061, {'voltage': 1.3, 'temperature': 13.45}),
                    (164621248381838834, {'voltage': 1.376, 'temperature': 13.412})
                ]
            )
        '''
        api = self.client.write_api(write_options=SYNCHRONOUS)

        records = []
        for measurement in data:
            p = Point(label).tag('id', id).time(measurement[0])
            for k,v in measurement[1].items():
                p.field(k, v)
            records.append(p)

        api.write(bucket=self.bucket, org=self.org, record=records)
