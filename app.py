# dependencies
from gpiozero import DistanceSensor

# python standard libraries
import time

# local modules
import db_handler as dbh



class Tracker:
    '''
    Main class that handles the sensor logic

    Attributes:
        ingress_sensor (DistanceSensor): the sensor closest to the door
        egress_sensor (DistanceSensor): the sensor farthest from the door
        db (DB_Handler)
        ingress_floor (float): the distance to the nearest object from the ingress sensor in meters
        egress_floor (float): the distance to the nearest object from the egress sensor in meters
    '''
    def __init__(self, pins, db_filename):
        '''
        Args:
            pins (dict): a dict that contains info about the pins that the sensors are connected to.
                         should be of form:
                         {
                            "ingress": {
                                "trigger": 17,
                                "echo": 18
                            },
                            "egress": {
                                "trigger": 22,
                                "echo": 23
                            }
                        }
            db_filename (str): database filename
        '''
        self.ingress_sensor = DistanceSensor(echo=pins['ingress']['echo'], trigger=pins['ingress']['trigger'])
        self.egress_sensor = DistanceSensor(echo=pins['egress']['echo'], trigger=pins['egress']['trigger'])
        self.db = dbh.DB_Handler(db_filename)

        self.ingress_floor = 1 # in meters
        self.egress_floor = 1
        self.init_distance()



    def init_distance(self):
        '''
        Polls both sensors 10 times to find out what the distance is to the nearest object,
        then sets the floors to the smallest of these values

        In most cases this is used to find the nearest wall. So if the sensors find something
        at a closer distance than the wall (or floor value), then we know someone has passed
        in front of it.

        Note:
            Sensors only scan up to 1 meter (3.3 feet). They can be configured to scan farther,
            but for this use case, 1 meter is plenty.
        '''
        for _ in range(10):
            ingress_distance = self.ingress_sensor.distance
            egress_distance = self.egress_sensor.distance

            if ingress_distance < self.ingress_floor:
                self.ingress_floor = ingress_distance

            if egress_distance < self.egress_floor:
                self.egress_floor = egress_distance



    def process_direction(self, sensor: DistanceSensor, floor: float, db_field: str):
        '''
        When a sensor is tripped, detremines if the person went all the way through, or
        turned back before tripping the second sensor.

        Note:
            People have 3 seconds to trip the second sensor before it times out and
            "thinks" the person has turned back.
        '''
        date = time.strftime("%Y-%m-%d")    # iso 8601 format (yyyy-mm-dd) because we're not savages
        start_time = time.time()
        while time.time() < start_time + 3: # 3 second timeout
            if sensor.distance < floor:
                self.db.increment(db_field, date)
                sensor.wait_for_out_of_range()
                return



    def run(self):
        '''
        Main loop

        Constantly polls both sensors with 4 possible outcomes:
            1. only the ingress sensor is tripped which indicates that someone is entering
            2. only the egress sensor is tripped which indicates that someone is exiting
            3. both sensors are tripped which indicates that someone is moving slowly through the doorway
            4. no sensors are tripped and there is no movement/people
        '''
        while True:
            ingress_distance = self.ingress_sensor.distance
            egress_distance = self.egress_sensor.distance
            if ingress_distance < self.ingress_floor and egress_distance < self.egress_floor:
                time.sleep(1)
                continue
            if ingress_distance < self.ingress_floor:
                self.ingress(self.egress_sensor, self.egress_floor, 'ingress')
            elif egress_distance < self.egress_floor:
                self.egress(self.ingress_sensor, self.ingress_floor, 'egress')






if __name__ == '__main__':
    PINS = {
        "ingress": {
            "trigger": 17,
            "echo": 18
        },
        "egress": {
            "trigger": 22,
            "echo": 23
        }
    }

    DB_FILENAME = 'population.db'

    tracker = Tracker(PINS, DB_FILENAME)
    tracker.run()