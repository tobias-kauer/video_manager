import eel

from recorder import *
from frame_processer import *
from ultrasonic_sensor import *
from mosfet import *
from platform_manager import is_raspberry_pi
from segment_display import *
from model_visualizer import *
from datetime import datetime
import time
import json

debug_mode = True  # Set to True to enable debug mode
disable_sensors = False # Set to True to disable sensors

RESOLUTION = (640, 480)  # Default resolution
DURATION = 10  # Default duration in seconds
VIDEO_LOCATION = "web/videos/"  # Directory to save videos

BASE_SUBMISSIONS = 124  # Base number of submissions for the segment display

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

MOSEFET_BLINK = "blink"
MOSFET_PULSE = "pulse"
MOSFET_OFF = "off"
MOSFET_ON = "on"

current_mosfet_state = MOSFET_PULSE

def count_entries():
    json_file_path = "entries.json"

    # Check if the file exists
    if not os.path.exists(json_file_path):
        print(f"{json_file_path} does not exist.")
        return 0

    # Load the file and count the entries
    with open(json_file_path, "r") as json_file:
        entries = json.load(json_file)
        return len(entries)

total_submissions = BASE_SUBMISSIONS + count_entries()  # Initialize total submissions with base value plus existing entries
last_uuid = "000000"

# Check if running on a Raspberry Pi
if is_raspberry_pi():
    print("Running on Raspberry Pi. Using real sensors and devices.")
    sensorCamera = UltrasonicSensor(trigger_pin=CAMERA_SENSOR_TRIGGER_PIN, echo_pin=CAMERA_SENSOR_ECHO_PIN, name="Sensor Camera")
    sensorRoom = UltrasonicSensor(trigger_pin=ROOM_SENSOR_TRIGGER_PIN, echo_pin=ROOM_SENSOR_ECHO_PIN, name="Sensor Room")
    mosfet = Mosfet(gpio_pin=MOSFET_GPIO_PIN, frequency=3000)
    segmentDisplay = SegmentDisplay()

else:
    print("Not running on Raspberry Pi. Using mock sensors and devices.")
    sensorCamera = MockUltrasonicSensor(trigger_pin=23, echo_pin=24, name="Sensor Camera", trigger_key="space")
    sensorRoom = MockUltrasonicSensor(trigger_pin=25, echo_pin=26, name="Sensor Room", trigger_key="space")
    mosfet = MockMosfet(gpio_pin=MOSFET_GPIO_PIN)
    segmentDisplay = MockSegmentDisplay()

segmentDisplay.init_display()
segmentDisplay.clear_display()
segmentDisplay.display_number(total_submissions)

# Initialize variables for debugging
sensor_camera_value = 0
sensor_room_value = 0
last_display_value = 0
lamp_brightness = 0

print("Initializing Eel...")  # Starting EEl for the web interface
eel.init('web')

eel.updateModelInfoText("14.06.2025", total_submissions)
 
def monitor_sensors():
    """
    Continuously monitor both sensors and trigger a function if a threshold is crossed.
    """
    while True:

        if get_state() == IDLE_STATE and not disable_sensors:

            if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD):
                print(f"Sensor Camera triggered! Distance: {sensorCamera.get_distance():.2f} cm")
                set_state(CAMERA_STATE)  # Change state to CAMERA_STATE

            if sensorRoom.is_object_within_range(SENSOR_ROOM_THRESHOLD):
                print(f"Sensor Room triggered! Distance: {sensorRoom.get_distance():.2f} cm")
                set_state(ROOM_STATE)

        if get_state() == ROOM_STATE and not disable_sensors:

            # Check if Sensor Camera is within range or manually triggered
            if sensorCamera.is_object_within_range(SENSOR_CAMERA_THRESHOLD):
                print(f"Sensor Camera triggered! Distance: {sensorCamera.get_distance():.2f} cm")

                set_state(CAMERA_STATE)  # Change state to CAMERA_STATE

        time.sleep(0.5)  # Adjust the polling interval as needed

def mosfet_controller():
    """
    Continuously pulse the MOSFET in the background.
    """
    previous_state = "pulse"

    while True:
        current_state = get_mosfet_state()

        # Only interrupt and start a new operation if the state has changed
        if current_state != previous_state:
            print(f"MOSFET state changed from {previous_state} to {current_state}")

            # Interrupt any running MOSFET operation
            mosfet.interrupt = True
            while mosfet.is_running:  # Wait for the current operation to finish
                time.sleep(0.1)

            # Reset the interrupt flag for the next operation
            mosfet.interrupt = False

            # Perform the operation based on the new state
            if current_state == MOSEFET_BLINK:
                print("MOSFET state: BLINK")
                mosfet.blink(on_time=0.5, off_time=0.5)
                set_mosfet_state(MOSFET_OFF)
            elif current_state == MOSFET_PULSE:
                print("MOSFET state: PULSE")
                mosfet.pulse_smooth_with_range(duration=10, steps=200, min_brightness=0.3, max_brightness=1)
            elif current_state == MOSFET_OFF:
                print("MOSFET state: OFF")
                mosfet.set_pwm(0)  # Set brightness to 0%
            elif current_state == MOSFET_ON:
                print("MOSFET state: ON")
                mosfet.set_pwm(100)  # Set brightness to 60%

            # Update the previous state
            previous_state = current_state

        # Sleep briefly to avoid excessive CPU usage
        time.sleep(0.1)

def display_controller():

    """
    Continuously update the segment display in the background.
    """
    segmentDisplay.init_display()  # Initialize the display
    segmentDisplay.clear_display()  # Clear the display

    while True:
        segmentDisplay.display_number(total_submissions)  # Display the total submissions
        time.sleep(2)
        segmentDisplay.clear_display()

def update_total_submissions_display():
    segmentDisplay.clear_display()
    segmentDisplay.display_number(total_submissions)

def start_training_thread():
    """
    Start the training process in a separate thread.
    """
    def training_task():
        print("Training started...")
        modelviz_train(get_current_uuid()) 
        print("Training completed. Switching to VISUALIZING_STATE.")
        set_state(VISUALIZING_STATE)  # Switch to VISUALIZING_STATE after training

    # Start the training task in a new thread
    training_thread = threading.Thread(target=training_task)
    training_thread.start()
    training_thread.join()  # Wait for the thread to finish

@eel.expose
def set_mosfet_state(new_state):
    """updateTrainingImages
    Set the global MOSFET state to the specified state.

    Args:
        new_state (str): The new MOSFET state (MOSEFET_BLINK, MOSFET_PULSE, MOSFET_OFF, MOSFET_ON).
    """
    global current_mosfet_state
    current_mosfet_state = new_state
    mosfet.interrupt_task()  # Interrupt any ongoing MOSFET operation
    print(f"------------------------------------------------------------")
    print(f"MOSFET state changed to: {current_mosfet_state}")
    print(f"------------------------------------------------------------")

@eel.expose
def get_mosfet_state():
    """
    Get the current global MOSFET state.

    Returns:
        str: The current MOSFET state.
    """
    global current_mosfet_state
    return current_mosfet_state

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

    if current_state == IDLE_STATE:
        set_mosfet_state(MOSFET_PULSE)  # Set MOSFET to pulse state
        eel.startAnimationTopIdle()
        eel.startAnimationSideIdle()
        eel.reloadSprites(False)
    elif current_state == ROOM_STATE:
        set_mosfet_state(MOSFET_OFF)  # Set MOSFET to pulse state
        eel.startAnimationTopRoom()
        triggerCameraMovePY(0.004, 0.5)  # Move camera to room position
        #eel.startAnimationSideRoom()
    elif current_state == CAMERA_STATE:
        print("Camera state detected. Starting recording...")
        eel.startRecordingEvent()
        set_mosfet_state(MOSFET_ON)  # Set MOSFET to pulse state
        eel.startAnimationSideCamera()
    elif current_state == TRAINING_STATE:
        eel.startAnimationSideTraining()
        set_mosfet_state(MOSFET_OFF)
        #eel.updateTrainingImages()
        eel.startAnimationTopTraining()
        start_training_thread()
        print("Training state detected. Starting training...")
    elif current_state == VISUALIZING_STATE:
        eel.startAnimationSideVisualizing()
        print("Visualizing state detected. Starting model visualization...")
        eel.reloadSprites(True)
        current_time = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
        eel.updateModelInfoText(current_time, total_submissions)

@eel.expose
def trigger_Animation_Side_Room():
    """
    Trigger the side animation for the room state.
    """
    print("Triggering side animation for ROOM_STATE...")
    eel.startAnimationSideRoom()

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
    eel.updateUuidInfo(uuid)
    last_uuid = uuid

    increase_submissions()  # Increment the total submissions count

    # Define the path to the JSON file
    json_file_path = "entries.json"

    # Get the current timestamp
    timestamp = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")

    # Create the new entry
    new_entry = {"uuid": uuid, "timestamp": timestamp}

    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        # Create the file and initialize it with an empty list
        with open(json_file_path, "w") as json_file:
            json.dump([new_entry], json_file, indent=4)
        print(f"Created new JSON file: {json_file_path}")
    else:
        # Append the new entry to the existing file
        with open(json_file_path, "r") as json_file:
            entries = json.load(json_file)

        entries.append(new_entry)

        with open(json_file_path, "w") as json_file:
            json.dump(entries, json_file, indent=4)
        print(f"Updated JSON file: {json_file_path} with new entry.")


@eel.expose
def get_current_uuid():
    global last_uuid
    #print(f"Getting current UUID: {last_uuid}")
    return last_uuid

@eel.expose
def increase_submissions():
    global total_submissions  
    total_submissions += 1
    update_total_submissions_display()

@eel.expose
def get_total_submissions():
    global total_submissions
    print(f"Total submissions: {total_submissions}")
    return total_submissions

@eel.expose
def triggerCameraMovePY(move_speed, target_position):
    """
    Trigger the camera move from Python.
    """
    print("Camera move triggered from Python!")
    return eel.triggerCameraMove(move_speed, target_position)  # Calls the JS function


@eel.expose
def record_data():
    record_video(duration=DURATION, resolution=RESOLUTION, location=VIDEO_LOCATION)
    return "Recording started"
    #print(f"Video saved to {file_path} with UUID {uuid_str}")

@eel.expose
def process_frames(uuid):
    print(f"Processing data for UUID: {uuid}")

    # Define input and output directories for "no_BG"
    input_dir = f"{VIDEO_LOCATION}{uuid}/unprocessed/"
    no_bg_dir = f"{VIDEO_LOCATION}{uuid}/no_BG/"
    os.makedirs(no_bg_dir, exist_ok=True)

    # Process images in the input directory to remove idle background using skin mask
    print(f"Removing background for images in {input_dir}...")
    remove_background_skin_mask_directory(input_dir, no_bg_dir, suffix="_noBG")
    # Define input and output directories for "processed_colour"
    processed_colour_dir = f"{VIDEO_LOCATION}{uuid}/processed_colour/"
    os.makedirs(processed_colour_dir, exist_ok=True)

    # Process images in the "no_BG" directory to replace transparent pixels with white,
    # convert to black and white, and increase contrast
    print(f"Processing images in {no_bg_dir}...")
    process_images_in_folder(no_bg_dir, processed_colour_dir, suffix="_processed")

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


set_state(IDLE_STATE)  # Set the initial state to IDLE

eel.start('index.html', size=(800 , 600), block=False)
eel.start('three.html', size=(1080, 1080), block=False)

if debug_mode:
    eel.start('debug.html', size=(800, 600), block=False)

# Keep the app runningidle
while True:
    eel.sleep(0.1)