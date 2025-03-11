from config import GPSD_PORT
from domain.gps import Gps
import gps
import threading
    
class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd_client = gps.gps(port=GPSD_PORT, mode=gps.WATCH_ENABLE)    # вказати потрібний порт
        self.current_gps = None     # поточні координати
        self.running = True        

    def get_gps_data(self) -> Gps:
        if (self.current_gps is not None):
            return Gps(*self.current_gps)
        
    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            response = self.gpsd_client.next()
            # print('response:', response)
            if response['class'] == 'DEVICE':
                is_activated = getattr(response, 'activated')
                if is_activated == 0:    # коли logfile з координатами був повністю прочитаний
                    self.running = False
                    return

            if response['class'] == 'TPV' and hasattr(response, 'lat'):
                # print("Your position: lat = " + str(response.lat) + ", lon = " + str(response.lon))
                self.current_gps = [response.lat, response.lon]
                