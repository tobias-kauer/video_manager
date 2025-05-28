import eel

from recorder import *
from frame_processer import *
from ultrasonic_sensor import *
from platform_manager import is_raspberry_pi


RESOLUTION = (640, 480)  # Default resolution
DURATION = 10  # Default duration in seconds
VIDEO_LOCATION = "videos/"  # Directory to save videos

# Threshold values for the sensors
SENSOR_CAMERA_THRESHOLD = 20  # cm
SENSOR_ROOM_THRESHOLD = 90  # cm

CAMERA_SENSOR_TRIGGER_PIN = 23
CAMERA_SENSOR_ECHO_PIN = 24
ROOM_SENSOR_TRIGGER_PIN = 25
ROOM_SENSOR_ECHO_PIN = 26

# Check if running on a Raspberry Pi
if is_raspberry_pi():
    print("Running on Raspberry Pi. Using real sensors.")
    sensorCamera = UltrasonicSensor(trigger_pin=CAMERA_SENSOR_TRIGGER_PIN, echo_pin=CAMERA_SENSOR_ECHO_PIN, name="Sensor Camera")
    sensorRoom = UltrasonicSensor(trigger_pin=ROOM_SENSOR_TRIGGER_PIN, echo_pin=ROOM_SENSOR_TRIGGER_PIN, name="Sensor Room")
else:
    print("Not running on Raspberry Pi. Using mock sensors.")
    sensorCamera = MockUltrasonicSensor(trigger_pin=23, echo_pin=24, name="Sensor Camera", trigger_key="space")
    sensorRoom = MockUltrasonicSensor(trigger_pin=25, echo_pin=26, name="Sensor Room", trigger_key="space")

print("Initializing Eel...")  # Should show up in terminal
eel.init('web')
 
def monitor_sensors():
    """
    Continuously monitor both sensors and trigger a function if a threshold is crossed.
    """
    while True:

        if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD):
            print(f"Sensor 1 triggered! Distance: cm")
            trigger_function(sensor_name="Sensor 1", distance=1)

        if sensorRoom.is_object_within_range(SENSOR_ROOM_THRESHOLD):
            print(f"Sensor 2 triggered! Distance:  cm")
            trigger_function(sensor_name="Sensor 2", distance=2)

        time.sleep(0.1)  # Adjust the polling interval as needed

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
#eel.start('three.html', size=(720, 1000), block=False)
#eel.start('animation.html', size=(800, 600))

# Keep the app running
while True:
    eel.sleep(0.1)