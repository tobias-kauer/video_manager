import time
import os
import eel
import subprocess
import cv2
import uuid
import threading
import base64
import numpy as np

from platform_manager import is_raspberry_pi

#source .venv/bin/activate
#pip freeze > requirements.txt

CAMERA = 0  # Default camera index (0 for the first camera)
RESOLUTION = (640, 480)  # Default resolution
DURATION = 12  # Default duration in seconds
DEFAULT_LOCATION = "videos/"  # Directory to save videos
OUTOUT_IMAGE_SIZE = 480  # Size for square output images
CAMERA_ACTIVATION_DELAY = 3  # Time in seconds to wait for the camera to activate

def record_video(duration=DURATION, resolution=RESOLUTION, location=DEFAULT_LOCATION):
    """
    Record a video using the webcam and send live frames to the browser.

    Args:
        duration (int): Duration of the video in seconds.
        resolution (tuple): Resolution of the video (width, height).
        location (str): Directory where the video will be saved.

    Returns:
        tuple: (file_path, uuid) - The full file path and the UUID associated with the video.
    """
    def record():

         # Ensure the save location exists
        if not os.path.exists(location):
            os.makedirs(location)

        uuid_str = str(uuid.uuid4().int)[:6]
        base_folder = os.path.join(location, uuid_str)
        video_path = os.path.join(base_folder, f"{uuid_str}.mp4")
        unprocessed_folder = os.path.join(base_folder, "unprocessed")

        #filename = f"{uuid_str}.mp4"
        #file_path = os.path.join(location, filename)

        # Create the base folder and the unprocessed subfolder
        os.makedirs(base_folder, exist_ok=True)
        os.makedirs(unprocessed_folder, exist_ok=True)

        # Create a folder to save individual frames
        #frame_folder = os.path.join(location, uuid_str)
        
        #os.makedirs(frame_folder, exist_ok=True)

        cap = cv2.VideoCapture(CAMERA)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        # Wait for the camera to activate
        print(f"Waiting {CAMERA_ACTIVATION_DELAY} seconds for the camera to activate...")
        time.sleep(CAMERA_ACTIVATION_DELAY)

        # Check if the camera is opened successfully
        if not cap.isOpened():
            print("Error: Unable to access the camera.")
            return None, None

        print("Camera activated. Starting recording...")

        # Set exposure via v4l2-ctl AFTER VideoCapture is opened
        # Set manual exposure after camera is opened

        if is_raspberry_pi():
            subprocess.call(['v4l2-ctl', '-d', '/dev/video0', '-c', 'auto_exposure=1'])  # Manual mode
            subprocess.call(['v4l2-ctl', '-d', '/dev/video0', '-c', 'exposure_time_absolute=200'])  # Set value

        # Try to disable auto exposure (this may vary by platform)
        # For many webcams, 0.25 = manual mode, 0.75 = auto mode
        #cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # May not work on all platforms

        # Set manual exposure value (negative values often used on webcams)
        # Try values like -4, -6, or positive ones like 100 depending on your hardware
        #cap.set(cv2.CAP_PROP_EXPOSURE, -4)

        print("Auto Exposure:", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))
        print("Exposure:", cap.get(cv2.CAP_PROP_EXPOSURE))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, resolution)

        start_time = time.time()
        frame_count = 0  # Counter for naming frames
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Flip the frame horizontally
            flipped_frame = cv2.flip(frame, 1)  # Use 0 for vertical flip, 1 for horizontal flip, -1 for both

            # Convert the frame to a square 480x480 image
            square_frame = convert_to_square(flipped_frame, size=480)

            # Write the frame to the video file
            out.write(square_frame)

            # Save the frame as an image in the UUID folder
            frame_filename = os.path.join(unprocessed_folder, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, square_frame)
            frame_count += 1

            # Encode the frame as a JPEG and send it to the browser
            success, buffer = cv2.imencode('.jpg', square_frame)
            if not success:
                print("Failed to encode frame")
                continue
            frame_data = base64.b64encode(buffer).decode('utf-8')
            eel.update_live_view(frame_data)

        cap.release()
        out.release()

        print(f"Video saved as: {video_path}")
        print(f"Frames saved in folder: {unprocessed_folder}")
        eel.on_record_done(uuid_str)  # Notify the browser that recording is done

        return video_path, uuid_str

    # Run the recording in a separate thread
    threading.Thread(target=record).start()

def convert_to_square(image, size=480):
    """
    Convert an image to a square image with the specified size (e.g., 480x480).
    The image is cropped to the center to make it square and then resized.

    Args:
        image (numpy.ndarray): The input image.
        size (int): The desired square size (default is 480).

    Returns:
        numpy.ndarray: The square image.
    """
    # Get the original dimensions of the image
    h, w = image.shape[:2]

    # Determine the crop dimensions to make the image square
    if h > w:
        # Crop height to match width
        crop_size = w
        y_start = (h - crop_size) // 2
        x_start = 0
    else:
        # Crop width to match height
        crop_size = h
        y_start = 0
        x_start = (w - crop_size) // 2

    # Perform the crop
    cropped_image = image[y_start:y_start + crop_size, x_start:x_start + crop_size]

    # Resize the cropped image to the desired size
    square_image = cv2.resize(cropped_image, (size, size))

    return square_image

def generate_uuid_filename():
    """
    Generate a unique filename using a truncated UUID (6 digits).
    """
    return str(uuid.uuid4().int)[:6] + ".mp4"