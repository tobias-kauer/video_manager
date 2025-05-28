from gpiozero import PWMLED
from time import sleep
import math

GIPO_PIN = 17
mosfet = PWMLED(GIPO_PIN)

def pulse_smooth(duration=10, steps=100):
    for i in range(steps):
        brightness = (math.sin(i / steps * 2 * math.pi) + 1) / 2
        mosfet.value = brightness
        sleep(duration / steps)

    try:
        while True:
            pulse_smooth()
    except KeyboardInterrupt:
        pass



def blink():

    while True:
        print("Light on")
        mosfet.on()
        sleep(2)

        print("Light off")
        mosfet.off()
        sleep(2)