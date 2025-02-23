from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking
import config


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        # filenames
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

        # data
        self.accelerometer_data = None
        self.gps_data = None
        self.parking_data = None

        self.accelerometer_index = 0
        self.gps_index = 0
        self.parking_index = 0

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""

        if self.accelerometer_index >= len(self.accelerometer_data) - 1:
            self.accelerometer_index = 0
        if self.gps_index >= len(self.gps_data) - 1:
            self.gps_index = 0
        if self.parking_index >= len(self.parking_data) - 1:
            self.parking_index = 0

        self.accelerometer_index += 1
        self.gps_index += 1
        self.parking_index += 1

        accelerometer_data = Accelerometer(*self.accelerometer_data[self.accelerometer_index])
        gps_data = Gps(*self.gps_data[self.gps_index])
        parking_data = Parking(*self.parking_data[self.parking_index], Gps(*config.PARKING_SPOT))
        return AggregatedData(accelerometer_data, gps_data, parking_data, datetime.now())

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        with open(self.accelerometer_filename, 'r') as csvfile:
            self.accelerometer_data = list(reader(csvfile))
        with open(self.gps_filename, 'r') as csvfile:
            self.gps_data = list(reader(csvfile))
        with open(self.parking_filename, 'r') as csvfile:
            self.parking_data = list(reader(csvfile))

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        pass
