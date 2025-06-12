import eel

from recorder import *
from frame_processer import *
from ultrasonic_sensor import *
from mosfet import *
from platform_manager import is_raspberry_pi
from segment_display import *
from model_visualizer import *

debug_mode = True  # Set to True to enable debug mode
disable_sensors = True  # Set to True to disable sensors

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
ROOM_SENSOR_ECHO_PIN = 27

MOSFET_GPIO_PIN = 17  # GPIO pin for the MOSFET

# Define global states
IDLE_STATE = "idle"
ROOM_STATE = "room"
CAMERA_STATE = "camera"
RECORDING_STATE = "recording"
TRAINING_STATE = "training"
VISUALIZING_STATE = "visualizing"
DEBUG_STATE = "debug"

# Initialize the current state
current_state = IDLE_STATE

total_submissions = 124
last_uuid = "000000"


# Check if running on a Raspberry Pi
if is_raspberry_pi():
    print("Running on Raspberry Pi. Using real sensors and devices.")
    sensorCamera = UltrasonicSensor(trigger_pin=CAMERA_SENSOR_TRIGGER_PIN, echo_pin=CAMERA_SENSOR_ECHO_PIN, name="Sensor Camera")
    sensorRoom = UltrasonicSensor(trigger_pin=ROOM_SENSOR_TRIGGER_PIN, echo_pin=ROOM_SENSOR_ECHO_PIN, name="Sensor Room")
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

    while True:

        if get_state() == IDLE_STATE and not disable_sensors:

            if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD):
                print(f"Sensor Camera triggered! Distance: {sensorCamera.get_distance():.2f} cm")
                set_state(CAMERA_STATE)  # Change state to CAMERA_STATE

                #trigger_function(sensor_name="Sensor Camera", distance=sensorCamera.get_distance())
 
                #eel.startRecordingEvent()  # Trigger the recording event in the frontend

            if sensorRoom.is_object_within_range(SENSOR_ROOM_THRESHOLD):
                print(f"Sensor Room triggered! Distance: {sensorRoom.get_distance():.2f} cm")
                set_state(ROOM_STATE)

                #trigger_function(sensor_name="Sensor Room", distance=sensorRoom.get_distance())

        if get_state() == ROOM_STATE and not disable_sensors:

            # Check if Sensor Camera is within range or manually triggered
            if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD):
                print(f"Sensor Camera triggered! Distance: {sensorCamera.get_distance():.2f} cm")

                set_state(CAMERA_STATE)  # Change state to CAMERA_STATE

                #trigger_function(sensor_name="Sensor Camera", distance=sensorCamera.get_distance())
                sensor_camera_manual_trigger = False  # Reset manual trigger flag

                #eel.startRecordingEvent()  # Trigger the recording event in the frontend

        time.sleep(0.1)  # Adjust the polling interval as needed
def mosfet_controller():
    """
    Continuously pulse the MOSFET in the background.
    """
    while True:
        if get_state() == IDLE_STATE:
            mosfet.pulse_smooth_with_range(duration=10, steps=100, min_brightness=0.3, max_brightness=0.9)  # Pulsate from 0% to 100%
        if get_state() == ROOM_STATE:
            mosfet.pulse_smooth_with_range(duration=10, steps=100, min_brightness=0.3, max_brightness=0.7)  # Pulsate from 0% to 100%
        if get_state() == CAMERA_STATE:
            mosfet.blink(on_time=2, off_time=2)
            mosfet.set_pwm(100)  # Set MOSFET to 100% brightness
def display_controller():

    """
    Continuously update the segment display in the background.
    """
    segmentDisplay.init_display()  # Initialize the display
    segmentDisplay.clear_display()  # Clear the display

    while True:

        segmentDisplay.test_character("E")  # Display "IDLE" text
         # Clear the display
        #segmentDisplay.scroll_text("TOTAL SUBMISSIONS", delay=0.1)  # Scroll a welcome message
        time.sleep(1)
        segmentDisplay.clear_display() 
        segmentDisplay.display_number(total_submissions)  # Display the total submissions
        time.sleep(2)
        segmentDisplay.clear_display() 

def model_trainer():
    """
    Reload the model in a separate thread to avoid blocking the main application.
    """
    while True:
            # Check if the current state is TRAINING_STATE
            if get_state() == TRAINING_STATE:
                print("Training started...")
                modelviz_train("0000000")  # Execute the model training logic
                print("Training completed. Switching to VISUALIZING_STATE.")
                set_state(VISUALIZING_STATE)  # Set the state to VISUALIZING_STATE
            time.sleep(1)  # Wait for 1 second before checking the state again
def data_recorder():
    """
    Record video data in a separate thread to avoid blocking the main application.
    """
    while True:
        if get_state() == RECORDING_STATE:
            print("Recording started...")
            eel.startRecordingEvent()
            print("Recording completed. Switching to IDLE_STATE.")
            set_state(IDLE_STATE)  # Set the state to IDLE_STATEr
        time.sleep(1)  # Wait for 1 second before checking the state again


@eel.expose
def set_state(new_state):
    """
    Set the global state to the specified state.

    Args:
        new_state (str): The new state to set (IDLE_STATE, ROOM_STATE, CAMERA_STATE).
    """
    global current_state
    current_state = new_state
    print(f"------------------------------------------------------------")
    print(f"State changed to: {current_state}")
    print(f"------------------------------------------------------------")

@eel.expose
def get_state():
    """
    Get the current global state.

    Returns:
        str: The current state.
    """
    global current_state
    return current_state

@eel.expose
def set_current_uuid(uuid):
    print(f"Setting current UUID to: {uuid}")
    global last_uuid
    last_uuid = uuid

@eel.expose
def get_current_uuid():
    global last_uuid
    print(f"Getting current UUID: {last_uuid}")
    return last_uuid

@eel.expose
def increase_submissions():
    global total_submissions
    total_submissions += 1

@eel.expose
def get_total_submissions():
    global total_submissions
    print(f"Total submissions: {total_submissions}")
    return total_submissions




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

    set_state(IDLE_STATE)  # Reset state to IDLE after processing

    return f"Data processed for UUID: {uuid}"

@eel.expose
def trigger_animations():
    print("All Animations triggered from Python!")
    eel.startAnimation()  # Calls the JS function
    eel.startAnimationTopIdle()

# Start the sensor monitoring thread
sensor_thread = threading.Thread(target=monitor_sensors, daemon=True)
sensor_thread.start()

# Start the MOSFET pulsating thread
mosfet_thread = threading.Thread(target=mosfet_controller, daemon=True)
mosfet_thread.start()

# Start the display controller thread
display_thread = threading.Thread(target=display_controller, daemon=True)
display_thread.start()

# Start the training thread
training_thread = threading.Thread(target=model_trainer, daemon=True)
training_thread.start()

# Start the data recorder thread
data_recorder_thread = threading.Thread(target=data_recorder, daemon=True)
data_recorder_thread.start()


eel.start('index.html', size=(800 , 600), block=False)
#eel.start('three.html', size=(720, 1000), block=False)
#eel.start('animation.html', size=(800, 600))

#reload_model()  # Load the model visualizer with the initial UUID

if debug_mode:
    eel.start('debug.html', size=(800, 600), block=False)

# Keep the app running
while True:

    eel.sleep(0.1)