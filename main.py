import eel

from recorder import *
from frame_processer import *
from ultrasonic_sensor import *


RESOLUTION = (640, 480)  # Default resolution
DURATION = 10  # Default duration in seconds
VIDEO_LOCATION = "videos/"  # Directory to save videos

# Threshold values for the sensors
SENSOR_CAMERA_THRESHOLD = 20  # cm
SENSOR_ROOM_THRESHOLD = 90  # cm

'''sensorCamera = UltrasonicSensor(trigger_pin=23, echo_pin=24, name="Sensor Camera")
print(f"Ultrasonic Sensor initialized: {sensorCamera.name}")

sensorRoom = UltrasonicSensor(trigger_pin=23, echo_pin=24, name="Sensor Room")
print(f"Ultrasonic Sensor initialized: {sensorCamera.name}")'''

print("Initializing Eel...")  # Should show up in terminal
eel.init('web')

def monitor_sensors():
    """
    Continuously monitor both sensors and trigger a function if a threshold is crossed.
    """
    while True:
        distance1 = sensorCamera.get_distance()
        distance2 = sensorRoom.get_distance()

        if distance1 < SENSOR_CAMERA_THRESHOLD:
            print(f"Sensor 1 triggered! Distance: {distance1:.2f} cm")
            trigger_function(sensor_name="Sensor 1", distance=distance1)

        if distance2 < SENSOR_ROOM_THRESHOLD:
            print(f"Sensor 2 triggered! Distance: {distance2:.2f} cm")
            trigger_function(sensor_name="Sensor 2", distance=distance2)

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

'''# Start the sensor monitoring thread
sensor_thread = threading.Thread(target=monitor_sensors, daemon=True)
sensor_thread.start()'''

eel.start('index.html', size=(800, 600), block=False)
#eel.start('three.html', size=(800, 600), block=False)

# Keep the app running
while True:
    eel.sleep(0.1)