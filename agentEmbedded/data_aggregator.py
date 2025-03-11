from file_datasource import FileDatasource
from gpsfake import GpsPoller
from datetime import datetime
from schema.aggregated_data_schema import AggregatedDataSchema
from domain.aggregated_data import AggregatedData


def aggregate_data(accelerometer, gps):
    data = AggregatedData(accelerometer, gps, datetime.now())
    return AggregatedDataSchema().dumps(data)
