from example_data import example_ecg, example_temperature, example_sao2

def stop_reading():
    '''
    Called automatically when the sensor reading stops
    You can e.g. stop sensors here.
    '''
    pass

def read_ecg_sensor(writer, now):
    '''
    Read ECG values
    '''
    writer.add_data('ecg', example_ecg(now))


def read_misc_sensors(writer, now):
    '''
    Read misc. sensor values
    '''
    writer.add_data('temperature', example_temperature(now))
    sao2 = example_sao2(now)
    writer.add_data('sao2_arterial', sao2['arterial'])
    writer.add_data('sao2_venous', sao2['venous'])


DATABASE_URL         = 'influxdburl.com:8086'
DATABASE_ORG         = 'organization name'
DATABASE_BUCKET      = 'bucket name'
DATABASE_TOKEN       = 'api token'
SENSOR_ID            = 69535
# Gather data for 2 seconds before writing in batch to the database
SENSOR_PUSH_INTERVAL = 2

# Define how often each sensor reading function should run (in seconds) here
# For example, you could add:
#     read_ultrasonic_sensor: 5,
# And define a 'read_ultrasonic_sensor' function to have it be run every 5 seconds
SENSOR_READER_INTERVALS = {
    read_ecg_sensor:   (2.8 / 1000), # every 2.8ms
    read_misc_sensors: 1,            # every 1 second
}
