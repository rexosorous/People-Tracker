'''
A config file of sorts to hold all constant variables used
'''

TIMEOUT = 3 # when one sensor is tripped, how long in seconds to wait for the other to sensor to trip
DUAL_TRIP_WAIT = 1 # when both sensors are tripped, how long in seconds to wait for the person to fully go through the threshold
DB_FILE = 'population.db' # filepath/filename to the database file
PINS = { # where the pins are connected for each sensor
    "ingress": { # the sensor closest to the door
        "trigger": 17,
        "echo": 18
    },
    "egress": { # the sensor farthest way from the door
        "trigger": 22,
        "echo": 23
    }
}