from gpiozero import PWMLED
import time
import math


class Mosfet:
    def __init__(self, gpio_pin=17, frequency=1500):
        self.mosfet = PWMLED(gpio_pin, frequency=frequency)

        self.is_running = False  # Flag to indicate if a function is running
        self.interrupt = False  # Flag to interrupt the current function

        self.current_pwm_value = None

    def interrupt_task(self):
        self.interrupt = True

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
            time.sleep(step_duration)
        
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

        # Precompute brightness values
        brightness_values = [
            min_brightness + (max_brightness - min_brightness) * (math.sin(i / steps * 2 * math.pi) + 1) / 2
            for i in range(steps)
        ]
        step_duration = duration / steps

        print(f"Starting smooth pulse for {duration} seconds with {steps} steps between {min_brightness} and {max_brightness}.")

        self.is_running = True
        self.interrupt = False

        while not self.interrupt:
            # Gradually apply brightness values
            for brightness in brightness_values:
                if self.interrupt:
                    print("Pulse interrupted.")
                    break

                self.mosfet.value = brightness
                time.sleep(step_duration)
        self.mosfet.value = 0
        self.is_running = False
        print("Smooth pulse complete.")

    def pulse_smooth_with_range_old(self, duration=10, steps=100, min_brightness=0.2, max_brightness=0.8):
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
            time.sleep(duration / steps)
        print("Smooth pulse with range complete.")

    def blink(self, on_time=2, off_time=2):
        """
        Blink the MOSFET on and off in a loop until interrupted.

        Args:
            on_time (int): Duration in seconds for the MOSFET to stay on.
            off_time (int): Duration in seconds for the MOSFET to stay off.
        """
        print(f"Starting blink with on_time={on_time} and off_time={off_time}.")
        self.is_running = True
        self.interrupt = False

        while not self.interrupt:
            self.mosfet.on()
            time.sleep(on_time)

            if self.interrupt:  # Check if interrupted after turning on
                break

            self.mosfet.off()
            time.sleep(off_time)

        self.mosfet.off()  # Ensure the MOSFET is turned off after interruption
        self.is_running = False
        print("Blink operation interrupted or completed.")

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
        time.sleep(duration)  # Simulate the duration of the pulse

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