import spidev

# -------------------------------
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
