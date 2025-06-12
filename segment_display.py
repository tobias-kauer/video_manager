try:
    import spidev
except ImportError:
    spidev = None  # Handle the case where spidev is not available

import time

CHARACTER_MAP = {
    '0': 0x3F,  # 0
    '1': 0x06,  # 1
    '2': 0x5B,  # 2
    '3': 0x4F,  # 3
    '4': 0x66,  # 4
    '5': 0x6D,  # 5
    '6': 0x7D,  # 6
    '7': 0x07,  # 7
    '8': 0x7F,  # 8
    '9': 0x6F,  # 9
    'A': 0x77,  # A
    'B': 0x7C,  # B
    'C': 0x39,  # C
    'D': 0x5E,  # D
    'E': 0x79,  # E
    'F': 0x71,  # F
    'G': 0x3D,  # G
    'H': 0x76,  # H
    'I': 0x06,  # I
    'J': 0x1E,  # J
    'K': 0x75,  # K (approximation)
    'L': 0x38,  # L
    'M': 0x37,  # M (approximation)
    'N': 0x54,  # N
    'O': 0x3F,  # O
    'P': 0x73,  # P
    'Q': 0x67,  # Q (approximation)
    'R': 0x50,  # R (approximation)
    'S': 0x6D,  # S
    'T': 0x78,  # T
    'U': 0x3E,  # U
    'V': 0x3E,  # V (same as U)
    'W': 0x2E,  # W (approximation)
    'X': 0x76,  # X (same as H)
    'Y': 0x6E,  # Y
    'Z': 0x5B,  # Z
    '-': 0x40,  # Dash
    ' ': 0x00,  # Blank
}

class SegmentDisplay:
    def __init__(self):
        """
        Initialize the real segment display using SPI.
        """
        if spidev is None:
            raise RuntimeError("spidev library is not available. Cannot use SegmentDisplay on this platform.")

        self.spi_disp = spidev.SpiDev()
        self.spi_disp.open(0, 0)
        self.spi_disp.max_speed_hz = 1000000
        self.spi_disp.mode = 0

        print("Display Initialized")

    def write_cmd(self, register, data):
        """
        Write a command to the display.

        Args:
            register (int): The register to write to.
            data (int): The data to write.
        """
        self.spi_disp.xfer2([register, data])

    def init_display(self):
        """
        Initialize the display with default settings.
        """
        self.write_cmd(0x0F, 0x00)  # Display test: off
        self.write_cmd(0x0C, 0x01)  # Shutdown: off
        self.write_cmd(0x09, 0xFF)  # BCD decode mode
        self.write_cmd(0x0B, 0x07)  # Scan limit: all digits
        self.write_cmd(0x0A, 0x08)  # Intensity: medium
        self.clear_display()

    def clear_display(self):
        """
        Clear the display by blanking all digits.
        """
        for i in range(1, 9):
            self.write_cmd(i, 0x0F)  # Blank

    def display_number(self, number):
        """
        Display a number on the segment display.

        Args:
            number (int): The number to display.
        """
        number_str = str(int(number)).rjust(8)[::-1]  # Right-align, reverse
        for i in range(1, 9):
            if i <= len(number_str) and number_str[i - 1].isdigit():
                self.write_cmd(i, int(number_str[i - 1]))
            else:
                self.write_cmd(i, 0x0F)  # Blank


    def display_text(self, text):
        """
        Display text on the segment display.

        Args:
            text (str): The text to display (max 8 characters).
        """
        text = text.upper().ljust(8)[:8]  # Convert to uppercase, pad, and truncate to 8 characters
        for i in range(1, 9):
            char = text[i - 1]
            if char in CHARACTER_MAP:
                self.write_cmd(i, CHARACTER_MAP[char])  # Write the mapped character
            else:
                self.write_cmd(i, 0x00)  # Blank for unsupported characters

    def scroll_text(self, text, delay=0.5):
        """
        Scroll text across the segment display.

        Args:
            text (str): The text to scroll.
            delay (float): Delay between each scroll step (in seconds).
        """
        text = text.upper() + " " * 8  # Add spaces for scrolling
        for i in range(len(text) - 7):  # Scroll step by step
            self.display_text(text[i:i + 8])
            time.sleep(delay)


    def display_number_broken(self, number):
        """
        Display a number on the segment display.

        Args:
            number (int): The number to display (must be between 0 and 99999999).
        """
        # Ensure the number is within the valid range
        if not (0 <= number <= 99999999):
            raise ValueError("Number must be between 0 and 99999999.")

        # Convert the number to an 8-digit string, padded with leading zeros
        number_str = f"{number:08d}"  # Format as an 8-digit number

        # Write each digit to the corresponding register
        for i in range(1, 9):  # Registers 1 to 8
            self.write_cmd(i, int(number_str[i - 1]))


class MockSegmentDisplay:
    def __init__(self):
        """
        Initialize the mock segment display for testing.
        """
        self.display_state = [" "] * 8  # Simulate an 8-digit display

    def write_cmd(self, register, data):
        """
        Simulate writing a command to the display.

        Args:
            register (int): The register to write to.
            data (int): The data to write.
        """
        if 1 <= register <= 8:
            self.display_state[register - 1] = str(data) if data != 0x0F else " "
        print(f"MockSegmentDisplay: Register {register}, Data {data}")

    def init_display(self):
        """
        Simulate initializing the display.
        """
        print("MockSegmentDisplay: Initializing display")
        self.clear_display()

    def clear_display(self):
        """
        Simulate clearing the display.
        """
        self.display_state = [" "] * 8
        print("MockSegmentDisplay: Display cleared")

    def display_number(self, number):
        """
        Simulate displaying a number on the segment display.

        Args:
            number (int): The number to display.
        """
        number_str = str(int(number)).rjust(8)[::-1]  # Right-align, reverse
        for i in range(1, 9):
            if i <= len(number_str) and number_str[i - 1].isdigit():
                self.write_cmd(i, int(number_str[i - 1]))
            else:
                self.write_cmd(i, 0x0F)  # Blank
        print(f"MockSegmentDisplay: Displaying number {number}")

    def display_text(self, text):
        print(f"MockSegmentDisplay: Displaying text '{text}'")

    def scroll_text(self, text, delay=0.5):
        print(f"MockSegmentDisplay: Scrolling text '{text}' with delay {delay}")    

'''# -------------------------------
# DISPLAY SETUP
# -------------------------------
spi_disp = spidev.SpiDev()
spi_disp.open(0, 0)
spi_disp.max_speed_hz = 1000000
spi_disp.mode = 0

def write_cmd(register, data):
    spi_disp.xfer2([register, data])

def init_display():
    write_cmd(0x0F, 0x00)  # Display test: off
    write_cmd(0x0C, 0x01)  # Shutdown: off
    write_cmd(0x09, 0xFF)  # BCD decode mode
    write_cmd(0x0B, 0x07)  # Scan limit: all digits
    write_cmd(0x0A, 0x08)  # Intensity: medium
    clear_display()

def clear_display():
    for i in range(1, 9):
        write_cmd(i, 0x0F)  # Blank

def display_number(number):
    number_str = str(int(number)).rjust(8)[::-1]  # Right-align, reverse
    for i in range(1, 9):
        if i <= len(number_str) and number_str[i-1].isdigit():
            write_cmd(i, int(number_str[i-1]))
        else:
            write_cmd(i, 0x0F)

def close_display():
    clear_display()
    spi_disp.close()
'''