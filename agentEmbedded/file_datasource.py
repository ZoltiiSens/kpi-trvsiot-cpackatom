from csv import reader
from domain.accelerometer import Accelerometer


class FileDatasource:
    def __init__(self, accelerometer_filename: str) -> None:
        # filenames
        self.accelerometer_filename = accelerometer_filename
        # data
        self.accelerometer_data = None
        # index tracker
        self.accelerometer_index = 0

    def read(self) -> Accelerometer:
        """Метод повертає дані отримані з датчиків"""
        if self.accelerometer_index >= len(self.accelerometer_data) - 1:
            self.accelerometer_index = 0

        self.accelerometer_index += 1

        return Accelerometer(*self.accelerometer_data[self.accelerometer_index])

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        with open(self.accelerometer_filename, 'r') as csvfile:
            self.accelerometer_data = list(reader(csvfile))

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        self.accelerometer_data = None