from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        pass

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
