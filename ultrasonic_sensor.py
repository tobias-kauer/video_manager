import time
from gpiozero import DistanceSensor

sensor = DistanceSensor(echo=24, trigger=23)