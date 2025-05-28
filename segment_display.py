try:
    import spidev
except ImportError:
    spidev = None  # Handle the case where spidev is not available

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

    def display_number_old(self, number):
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

    def display_number(self, number):
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