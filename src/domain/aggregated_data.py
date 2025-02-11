from dataclasses import dataclass
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    time: datetime

