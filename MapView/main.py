import csv
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
import json
import threading
from kivy.properties import NumericProperty
from websocket import create_connection
from scipy.signal import find_peaks


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ws = None
        self.accel_data = []
        self.gps_data = []

        self.current_index = 0
        self.batch_size_for_analysis = 100
        self.accel_buffer = []
        self.line_layer = None
        self.next_index = 0
        self.car_lat = NumericProperty(0)
        self.car_lon = NumericProperty(0)

        self.car_marker = None

    def websocket_listener(self):
        """Функція для прослуховування WebSocket у фоні."""
        while True:
            try:
                result = self.ws.recv()
                result2 = json.loads(result)

                def update_data():
                    for line in result2[::-1]:
                        self.gps_data.append([line['longitude'], line['latitude']])
                        self.accel_data.append([line['x'], line['y'], line['z']])

                Clock.schedule_once(lambda dt: update_data(), 0)
            except Exception as e:
                print("WebSocket Error:", e)
                break

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        """

        self.mapview = MapView(zoom=14, lat=50.4501, lon=30.5234)
        return self.mapview

    def on_start(self):
        """
        Викликається при старті застосунку.
        Зчитуємо дані і починаємо оновлювати мапу за розкладом
        """

        self.ws = create_connection("ws://localhost:8000/ws/")
        print('Connected to WebSocket:', self.ws)

        self.ws_thread = threading.Thread(target=self.websocket_listener, daemon=True)
        self.ws_thread.start()

        self.line_layer = LineMapLayer()
        self.mapview.add_layer(self.line_layer, mode="scatter")

        Clock.schedule_interval(self.update, 0.1)

    def read_accel_data(self, filename):
        """Читає дані акселерометра з CSV-файлу"""
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                x = float(row["X"])
                y = float(row["Y"])
                z = float(row["Z"])
                self.accel_data.append((x, y, z))

    def read_gps_data(self, filename):
        """Читає GPS-координати з CSV-файлу"""
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lat = float(row["lat"])
                lon = float(row["lon"])
                self.gps_data.append((lat, lon))

    def update(self, *args):
        """
        Викликається регулярно (за розкладом Clock).
        - Оновлюємо позицію машини.
        - Накопичуємо буфер акселерометра і час від часу викликаємо check_road_quality().
        """

        if self.current_index < len(self.gps_data):
            print(self.current_index)
            lat, lon = self.gps_data[self.current_index]
            print(lat, lon)
            Clock.schedule_once(lambda dt: self.update_car_marker((lat, lon)), 0)

            self.line_layer.add_point([lat, lon])

            self.current_index += 1
        else:

            return

        if len(self.accel_buffer) < self.batch_size_for_analysis:
            if len(self.gps_data) <= self.current_index:
                return
            else:
                self.accel_buffer.append(self.accel_data[self.current_index])
        else:
            self.check_road_quality()
            self.accel_buffer = []

    def check_road_quality(self):
        """
        Аналізує дані акселерометра (тільки по осі z).
        Шукає піки (лежачі поліцейські) і провали (ями).
        Встановлює відповідні маркери на мапі.
        """
        z_values = [d[2] for d in self.accel_buffer]

        peak_distance = 5
        peak_height = 16670
        peak_prominence = 5

        peaks_max, _ = find_peaks(
            z_values,
            distance=peak_distance,
            height=peak_height,
            prominence=peak_prominence
        )

        inverted_z = [-1 * z for z in z_values]
        pit_height = -16660
        pits_min, _ = find_peaks(
            inverted_z,
            distance=peak_distance,
            height=(-1) * pit_height,
            prominence=peak_prominence
        )

        if self.current_index < len(self.gps_data):
            lat, lon = self.gps_data[self.current_index]
        else:

            lat, lon = self.gps_data[-1]

        if len(peaks_max) > 0:
            self.set_bump_marker((lat, lon))

        if len(pits_min) > 0:
            self.set_pothole_marker((lat, lon))

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: (lat, lon)
        """
        lat, lon = point
        self.car_lat = lat
        self.car_lon = lon
        if self.car_marker:

            self.car_marker.lat = self.car_lat
            self.car_marker.lon = self.car_lon
        else:

            self.car_marker = MapMarker(lat=self.car_lat, lon=self.car_lon, source="images/car.png")
            self.mapview.add_widget(self.car_marker)
        self.mapview.trigger_update(True)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: (lat, lon)
        """
        lat, lon = point
        pothole_marker = MapMarker(lat=lat, lon=lon, source="images/pothole.png")
        self.mapview.add_widget(pothole_marker)

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського (або бордюру)
        :param point: (lat, lon)
        """
        lat, lon = point
        bump_marker = MapMarker(lat=lat, lon=lon, source="images/bump.png")
        self.mapview.add_widget(bump_marker)


if __name__ == '__main__':
    MapViewApp().run()
