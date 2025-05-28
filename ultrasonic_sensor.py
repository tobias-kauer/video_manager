import time
from gpiozero import DistanceSensor
import random
import keyboard 

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
    

class MockUltrasonicSensor:
    def __init__(self, trigger_pin, echo_pin, name="Mock Sensor", trigger_key="space"):
        """
        Initialize the mock ultrasonic sensor.

        Args:
            trigger_pin (int): Mock trigger pin (not used in mock).
            echo_pin (int): Mock echo pin (not used in mock).
            name (str): Name of the sensor.
            trigger_key (str): The keyboard key to simulate an object within range.
        """
        self.name = name
        self.trigger_key = trigger_key
        self.mock_distance = random.uniform(10, 100)  # Initial random distance

    def get_distance(self):
        """
        Mock the distance measurement.

        Returns:
            float: A random distance value between 10 and 100 cm.
        """
        # Simulate random distance changes
        self.mock_distance = random.uniform(10, 100)
        print(f"{self.name} (Mock) Distance: {self.mock_distance:.2f} cm")
        return self.mock_distance

    def is_object_within_range(self, threshold_cm):
        """
        Check if an object is within a specified range or if the trigger key is pressed.

        Args:
            threshold_cm (float): The distance threshold in centimeters.

        Returns:
            bool: True if an object is within the threshold or the trigger key is pressed.
        """
        # Check if the trigger key is pressed
        if keyboard.is_pressed(self.trigger_key):
            print(f"{self.name}: Trigger key '{self.trigger_key}' pressed! Simulating object within range.")
            return True

        return False