from gpiozero import PWMLED
from time import sleep
import math


class Mosfet:
    def __init__(self, gpio_pin=17, frequency=1500):
        """
        Initialize the Mosfet object with the specified GPIO pin.

        Args:
            gpio_pin (int): The GPIO pin connected to the MOSFET.
        """
        self.mosfet = PWMLED(gpio_pin, frequency=frequency)
        

    def on(self):
        """
        Turn the MOSFET on (full brightness).
        """
        print("Mosfet ON")
        self.mosfet.on()

    def off(self):
        """
        Turn the MOSFET off.
        """
        print("Mosfet OFF")
        self.mosfet.off()

    def pulse_smooth(self, duration=10, steps=100):
        """
        Smoothly pulse the MOSFET brightness using a sine wave.

        Args:
            duration (int): Total duration of the pulse in seconds.
            steps (int): Number of steps for the pulse.
        """
        # Precompute brightness values
        brightness_values = [(math.sin(i / steps * 2 * math.pi) + 1) / 2 for i in range(steps)]
        step_duration = duration / steps

        print(f"Starting smooth pulse for {duration} seconds with {steps} steps.")
        
        # Gradually apply brightness values
        for brightness in brightness_values:
            self.mosfet.value = brightness
            sleep(step_duration)
        
        # Ensure the MOSFET returns to a stable state
        self.mosfet.value = 0
        print("Smooth pulse complete.")

    def pulse_smooth_with_range(self, duration=10, steps=100, min_brightness=0.2, max_brightness=0.8):
        """
        Smoothly pulse the MOSFET brightness between a specified range using a sine wave.

        Args:
            duration (int): Total duration of the pulse in seconds.
            steps (int): Number of steps for the pulse.
            min_brightness (float): Minimum brightness value (0 to 1).
            max_brightness (float): Maximum brightness value (0 to 1).
        """
        if not (0 <= min_brightness <= 1 and 0 <= max_brightness <= 1):
            raise ValueError("Brightness values must be between 0 and 1.")
        if min_brightness >= max_brightness:
            raise ValueError("min_brightness must be less than max_brightness.")

        print(f"Starting smooth pulse with range ({min_brightness}, {max_brightness}) for {duration} seconds with {steps} steps.")
        for i in range(steps):
            # Calculate brightness using sine wave and scale it to the specified range
            sine_value = (math.sin(i / steps * 2 * math.pi) + 1) / 2  # Sine wave value between 0 and 1
            brightness = min_brightness + (max_brightness - min_brightness) * sine_value
            self.mosfet.value = brightness
            sleep(duration / steps)
        print("Smooth pulse with range complete.")

    def blink(self, on_time=2, off_time=2):
        """
        Blink the MOSFET on and off in a loop.

        Args:
            on_time (int): Duration in seconds for the MOSFET to stay on.
            off_time (int): Duration in seconds for the MOSFET to stay off.
        """

        self.mosfet.on()
        sleep(on_time)

        self.mosfet.off()
        sleep(off_time)

    def set_pwm(self, percentage):
        """
        Set the MOSFET brightness to a specific percentage using PWM.

        Args:
            percentage (float): The brightness level as a percentage (0 to 100).
        """
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100.")

        # Convert percentage to a value between 0 and 1 for PWM
        pwm_value = percentage / 100
        self.mosfet.value = pwm_value
        print(f"Mosfet set to {percentage}% brightness (PWM value: {pwm_value}).")

class MockMosfet:
    def __init__(self, gpio_pin=17):
        """
        Initialize the MockMosfet object for testing.

        Args:
            gpio_pin (int): The GPIO pin (not used in the mock implementation).
        """
        self.gpio_pin = gpio_pin

    def on(self):
        """
        Simulate turning the MOSFET on.
        """
        print(f"MockMosfet ON (GPIO Pin: {self.gpio_pin})")

    def off(self):
        """
        Simulate turning the MOSFET off.
        """
        print(f"MockMosfet OFF (GPIO Pin: {self.gpio_pin})")

    def pulse_smooth(self, duration=10, steps=100):
        """
        Simulate a smooth pulse for the MOSFET.

        Args:
            duration (int): Total duration of the pulse in seconds.
            steps (int): Number of steps for the pulse.
        """
        print(f"MockMosfet: Simulating smooth pulse for {duration} seconds with {steps} steps.")
        sleep(duration)  # Simulate the duration of the pulse

    def blink(self, on_time=2, off_time=2):
        """
        Simulate blinking the MOSFET on and off in a loop.

        Args:
            on_time (int): Duration in seconds for the MOSFET to stay on.
            off_time (int): Duration in seconds for the MOSFET to stay off.
        """
        print(f"MockMosfet: Simulating blink loop (ON: {on_time}s, OFF: {off_time}s).")

    def set_pwm(self, percentage):
        """
        Simulate setting the MOSFET brightness to a specific percentage.

        Args:
            percentage (float): The brightness level as a percentage (0 to 100).
        """
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100.")
        
        print(f"MockMosfet: Set to {percentage}% brightness (simulated).")