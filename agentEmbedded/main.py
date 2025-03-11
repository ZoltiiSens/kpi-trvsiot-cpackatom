from paho.mqtt import client as mqtt_client
from subprocess import PIPE, Popen
from threading import Thread
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC, DELAY, GPSD_PORT
from data_aggregator import aggregate_data
from file_datasource import FileDatasource
from gpsfake import GpsPoller
import time


def start_gpsfake() -> (Thread, GpsPoller, Thread):
    # Start gpsfake
    def open_gpsfake():
        command = f"gpsfake -c {DELAY} -P {GPSD_PORT} data/gpsdata"
        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = proc.communicate()
        print(output, error)
    
    gpsfake_t = Thread(target=open_gpsfake)
    gpsfake_t.start()
    
    # Start gpsd
    while True:
        try:
            gpsd_poller = GpsPoller()
            break
        except ConnectionRefusedError:
            time.sleep(2)
            
    gpsd_t = Thread(target=gpsd_poller.run)
    gpsd_t.start()
    
    return gpsfake_t, gpsd_poller, gpsd_t


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client
    
    
def publish(client, topic, delay, datasource, gps):
    while True:
        time.sleep(delay)
        msg = aggregate_data(datasource.read(), gps.get_gps_data())
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            pass
            # print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
    datasource.stopReading()
    gps.stop()


def run():
    # Prepare mqtt client
    client = connect_mqtt(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    # Prepare datasource
    datasource = FileDatasource("data/accelerometer.csv")
    # Read datasource
    datasource.startReading()
    # Start gpsfake
    gpsfake_t, gpsd, gpsd_t = start_gpsfake()
    # Wait for gps to return something
    while True:
        if gpsd.get_gps_data() is not None:
            # print(gpsd.get_gps_data())
            break
        time.sleep(0.2)
    # Infinity publish data
    publish(client, MQTT_TOPIC, DELAY, datasource, gpsd)
    # Join threads
    gpsfake_t.join()
    gpsd_t.join()


if __name__ == '__main__':
    run()
