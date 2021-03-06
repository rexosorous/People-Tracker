# dependencies
from gpiozero import DistanceSensor

# standard libraries
import time
from random import randint



# GLOBAL VARIABLES
SENSOR1_PINS = {
	"trigger": 17,
	"echo": 18
}

SENSOR2_PINS = {
	"trigger": 22, 
	"echo": 23
}

sens1 = DistanceSensor(echo=SENSOR1_PINS["echo"], trigger=SENSOR1_PINS["trigger"])
sens2 = DistanceSensor(echo=SENSOR2_PINS["echo"], trigger=SENSOR2_PINS["trigger"])
inside = 0


def set_nominal_distance() -> (float, float):
    s1_values = []
    s2_values = []
    for _ in range(10):
        s1_values.append(sens1.distance)
        s2_values.append(sens2.distance)
    return ( sum(s1_values) / len(s1_values) , sum(s2_values) / len(s2_values) )


def enter(s2_avg_val):
    global inside
    start_time = time.time()
    while time.time() < start_time+5:
        if sens2.distance < s2_avg_val:
            inside += 1
            sens2.wait_for_out_of_range()    # should probably set some timeout and re-calc the avg_val in case something is placed by the sensor
            return
        time.sleep(0.0001)
        
def leave(s1_avg_val):
    global inside
    start_time = time.time()
    while time.time() < start_time+5:
        if sens1.distance < s1_avg_val:
            inside -= 1
            sens1.wait_for_out_of_range()
            return
        time.sleep(0.0001)


if __name__ == "__main__":
    s1_avg_val, s2_avg_val = set_nominal_distance()
    while True:
        print(f'{inside}\t{randint(11,99)}')
        s1d = sens1.distance
        s2d = sens2.distance
        if s1d < s1_avg_val and s2d < s2_avg_val:
            print('double')
            time.sleep(1)
        elif s1d < s1_avg_val:
            enter(s2_avg_val)
        elif s2d < s2_avg_val:
            leave(s1_avg_val)