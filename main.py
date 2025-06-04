import eel

from recorder import *
from frame_processer import *
from ultrasonic_sensor import *
from mosfet import *
from platform_manager import is_raspberry_pi
from segment_display import *

RESOLUTION = (640, 480)  # Default resolution
DURATION = 10  # Default duration in seconds
VIDEO_LOCATION = "videos/"  # Directory to save videos

# Threshold values for the sensors
SENSOR_CAMERA_THRESHOLD = 20  # cm
SENSOR_ROOM_THRESHOLD = 90  # cm


# GPIO pin configuration for the sensors and MOSFET
CAMERA_SENSOR_TRIGGER_PIN = 23
CAMERA_SENSOR_ECHO_PIN = 24
ROOM_SENSOR_TRIGGER_PIN = 25
ROOM_SENSOR_ECHO_PIN = 26

MOSFET_GPIO_PIN = 17  # GPIO pin for the MOSFET

# Flags for manual sensor triggering
sensor_camera_manual_trigger = False
sensor_room_manual_trigger = False


# Check if running on a Raspberry Pi
if is_raspberry_pi():
    print("Running on Raspberry Pi. Using real sensors and devices.")
    sensorCamera = UltrasonicSensor(trigger_pin=CAMERA_SENSOR_TRIGGER_PIN, echo_pin=CAMERA_SENSOR_ECHO_PIN, name="Sensor Camera")
    #sensorRoom = UltrasonicSensor(trigger_pin=ROOM_SENSOR_TRIGGER_PIN, echo_pin=ROOM_SENSOR_TRIGGER_PIN, name="Sensor Room")
    mosfet = Mosfet(gpio_pin=MOSFET_GPIO_PIN)
    segmentDisplay = SegmentDisplay()

else:
    print("Not running on Raspberry Pi. Using mock sensors and devices.")
    sensorCamera = MockUltrasonicSensor(trigger_pin=23, echo_pin=24, name="Sensor Camera", trigger_key="space")
    sensorRoom = MockUltrasonicSensor(trigger_pin=25, echo_pin=26, name="Sensor Room", trigger_key="space")
    mosfet = MockMosfet(gpio_pin=MOSFET_GPIO_PIN)
    segmentDisplay = MockSegmentDisplay()

segmentDisplay.init_display()
segmentDisplay.clear_display()
segmentDisplay.display_number(124)

# Initialize variables for debugging
sensor_camera_value = 0
sensor_room_value = 0
last_display_value = 0
lamp_brightness = 0

print("Initializing Eel...")  # Starting EEl for the web interface

eel.init('web')
 
def monitor_sensors():
    """
    Continuously monitor both sensors and trigger a function if a threshold is crossed.
    """

    global sensor_camera_manual_trigger, sensor_room_manual_trigger

    while True:

        # Check if Sensor Camera is within range or manually triggered
        if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD) or sensor_camera_manual_trigger:
            print(f"Sensor Camera triggered! Distance: {sensorCamera.get_distance():.2f} cm")
            trigger_function(sensor_name="Sensor Camera", distance=sensorCamera.get_distance())
            sensor_camera_manual_trigger = False  # Reset manual trigger flag

        # Check if Sensor Room is within range or manually triggered
        if sensorRoom.is_object_within_range(SENSOR_ROOM_THRESHOLD) or sensor_room_manual_trigger:
            print(f"Sensor Room triggered! Distance: {sensorRoom.get_distance():.2f} cm")
            trigger_function(sensor_name="Sensor Room", distance=sensorRoom.get_distance())
            sensor_room_manual_trigger = False  # Reset manual trigger flag

        

        time.sleep(0.1)  # Adjust the polling interval as needed

@eel.expose
def get_debug_data():
    """
    Provide debug data to the frontend.
    """
    return {
        "sensor_camera_value": sensor_camera_value,
        "sensor_room_value": sensor_room_value,
        "last_display_value": last_display_value,
        "lamp_brightness": lamp_brightness,
    }

@eel.expose
def set_display_value(value):
    """
    Set a value to the segment display and update the debug data.
    """
    global last_display_value
    last_display_value = value
    segmentDisplay.display_number(value)
    print(f"Display updated with value: {value}")

@eel.expose
def set_lamp_brightness(percentage):
    """
    Set the brightness of the lamp and update the debug data.
    """
    global lamp_brightness
    lamp_brightness = percentage
    mosfet.set_pwm(percentage)
    print(f"Lamp brightness set to: {percentage}%")

@eel.expose
def trigger_sensor(sensor_name):
    """
    Manually trigger a sensor for debugging.
    """
    global sensor_camera_manual_trigger, sensor_room_manual_trigger

    if sensor_name == "Sensor Camera":
        print("Manually triggered Sensor Camera")
        sensor_camera_manual_trigger = True
    elif sensor_name == "Sensor Room":
        print("Manually triggered Sensor Room")
        sensor_room_manual_trigger = True

def trigger_function(sensor_name, distance):
    """
    Function to be triggered when a sensor detects a value below the threshold.

    Args:
        sensor_name (str): The name of the sensor that triggered the function.
        distance (float): The distance measured by the sensor.
    """
    print(f"Triggered by {sensor_name} with distance {distance:.2f} cm")

@eel.expose
def test_function():
    print("Test function called from JavaScript")
    return "Hello from Python!"

@eel.expose
def record_data():

    record_video(duration=DURATION, resolution=RESOLUTION, location=VIDEO_LOCATION)
    return "Recording started"
    #print(f"Video saved to {file_path} with UUID {uuid_str}")

@eel.expose
def process_frames(uuid):
    print(f"Processing data for UUID: {uuid}")

    input_dir = f"{VIDEO_LOCATION}{uuid}/"
    output_dir = f"{VIDEO_LOCATION}{uuid}_noBG/"

    # Process images in the input directory to remove background using skin mask
    remove_background_skin_mask_directory(input_dir, output_dir, suffix="_noBG")

    input_dir = f"{VIDEO_LOCATION}{uuid}_noBG/"
    output_dir = f"{VIDEO_LOCATION}{uuid}_processed/"

    # Process images in the input directory to replace transparent pixels with white,
    # convert to black and white, and increase contrast

    process_images_in_folder(input_dir, output_dir, suffix="_processed", replace_transparent=False)

    return f"Data processed for UUID: {uuid}"

@eel.expose
def trigger_animation():
    print("Animation triggered from Python!")
    eel.startAnimation()  # Calls the JS function


# Start the sensor monitoring thread
sensor_thread = threading.Thread(target=monitor_sensors, daemon=True)
sensor_thread.start()

eel.start('index.html', size=(800 , 600), block=False)
eel.start('three.html', size=(720, 1000), block=False)
#eel.start('animation.html', size=(800, 600))
eel.start('debug.html', size=(800, 600), block=False)

# Keep the app running
while True:
    eel.sleep(0.1)