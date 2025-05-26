import time
from gpiozero import DistanceSensor

class UltrasonicSensor:
    def __init__(self, trigger_pin, echo_pin, name="Sensor"):
        """
        Initialize the ultrasonic sensor with the specified trigger and echo pins.

        Args:
            trigger_pin (int): GPIO pin connected to the trigger.
            echo_pin (int): GPIO pin connected to the echo.
            name (str): Optional name for the sensor (useful for debugging).
        """
        #self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
        self.name = name

    def get_distance(self):
        """
        Get the distance measured by the sensor in centimeters.

        Returns:
            float: Distance in centimeters.
        """
        distance_cm = self.sensor.distance * 100
        print(f"{self.name} Distance: {distance_cm:.2f} cm")
        return distance_cm

    def is_object_within_range(self, threshold_cm):
        """
        Check if an object is within a specified range.

        Args:
            threshold_cm (float): The distance threshold in centimeters.

        Returns:
            bool: True if an object is within the threshold, False otherwise.
        """
        distance_cm = self.get_distance()
        return distance_cm <= threshold_cm