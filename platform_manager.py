import platform

def is_raspberry_pi():
    """
    Check if the code is running on a Raspberry Pi.
    Returns:
        bool: True if running on a Raspberry Pi, False otherwise.
    """
    # Check the platform name
    if platform.system() != "Linux":
        return False

    # Check the machine name for Raspberry Pi
    with open("/proc/cpuinfo", "r") as f:
        cpuinfo = f.read()
        if "Raspberry Pi" in cpuinfo:
            return True

    return False