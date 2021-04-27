# dependencies
from gpiozero import DistanceSensor

# python standard libraries
from time import sleep

# local modules
import constants
import db_handler as dbh
import utils



class Tracker:
    '''
    Main class that handles the sensor logic

    Attributes:
        ingress_sensor (DistanceSensor): the sensor closest to the door
        egress_sensor (DistanceSensor): the sensor farthest from the door
        db (DB_Handler)
        ingress_floor (float): the distance to the nearest object from the ingress sensor in meters
        egress_floor (float): the distance to the nearest object from the egress sensor in meters
        timeout (float): when a sensor is tripped, how long to wait for the second sensor to trip (in seconds)
    '''
    def __init__(self, pins, db_filename, timeout):
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
            timeout (float): when a sensor is tripped, how long to wait for the second sensor to trip
        '''
        self.ingress_sensor = DistanceSensor(echo=pins['ingress']['echo'], trigger=pins['ingress']['trigger'])
        self.egress_sensor = DistanceSensor(echo=pins['egress']['echo'], trigger=pins['egress']['trigger'])
        self.db = dbh.DB_Handler(db_filename)
        self.timeout = timeout

        self.ingress_floor = 1  # in meters
        self.egress_floor = 1   # in meters
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
            There is an allotted time to trip the second sensor before it times out and
            "thinks" the person has turned back.
        '''
        print('tripped')
        date = utils.iso_date() # iso 8601 format (yyyy-mm-dd) because we're not savages
        start_time = utils.unix_time() # used for timeout
        while utils.unix_time() < start_time + self.timeout:  # poll the sensors until timeout
            if sensor.distance < floor:
                print('adding to db')
                self.db.increment(db_field, date)
                sensor.wait_for_out_of_range()
                return
            sleep(0.001)



    def run(self):
        '''
        Main loop

        Constantly polls both sensors with 4 possible outcomes:
            1. only the ingress sensor is tripped which indicates that someone is entering
            2. only the egress sensor is tripped which indicates that someone is exiting
            3. both sensors are tripped which indicates that someone is moving slowly through the doorway
            4. no sensors are tripped and there is no movement/people
        '''
        print('running...')
        while True:
            ingress_distance = self.ingress_sensor.distance
            egress_distance = self.egress_sensor.distance
            sleep(0.001) # for some reason, we need these sleep statements anytime we want to capture readings from the sensors
                         # we can get this to work by replacing sleeps with print statements if so desired
            if ingress_distance < self.ingress_floor and egress_distance < self.egress_floor:
                # both sensors are tripped usually when someone is moving slowly through the doorway
                # we need to ignore input from the sensors (by sleeping) for a short while to allow
                # the person to go all the way through the threshold. if we don't, then undoubtedly
                # we'll end up in a situation where one sensor is tripped, but the other isn't
                # resulting in a false positive of movement
                sleep(constants.DUAL_TRIP_WAIT)
                continue
            if ingress_distance < self.ingress_floor:
                self.process_direction(self.egress_sensor, self.egress_floor, 'ingress')
            elif egress_distance < self.egress_floor:
                self.process_direction(self.ingress_sensor, self.ingress_floor, 'egress')






if __name__ == '__main__':
    tracker = Tracker(constants.PINS, constants.DB_FILE, constants.TIMEOUT)
    tracker.run()