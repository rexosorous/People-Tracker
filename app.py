# dependencies
from gpiozero import DistanceSensor

# standard libraries
from time import sleep
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



def set_nominal_distance() -> (float, float):
    s1_values = []
    s2_values = []
    for _ in range(10):
        s1_values.append(sens1.distance)
        s2_values.append(sens2.distance)
    return ( sum(s1_values) / len(s1_values) , sum(s2_values) / len(s2_values) )



if __name__ == "__main__":
    s1_avg_val, s2_avg_val = set_nominal_distance()
    print('completed init')
    people_inside = 0
    
    while True:
        if sens1.distance < s1_avg_val:
            print(f'detected!\t{randint(10,99)}')
        sleep(0.00001)
