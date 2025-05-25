import eel

from recorder import *

RESOLUTION = (640, 480)  # Default resolution
DURATION = 10  # Default duration in seconds
VIDEO_LOCATION = "videos/"  # Directory to save videos

print("Initializing Eel...")  # Should show up in terminal
eel.init('web')

@eel.expose
def test_function():
    print("Test function called from JavaScript")
    return "Hello from Python!"

@eel.expose
def record_data():

    record_video(duration=DURATION, resolution=RESOLUTION, location=VIDEO_LOCATION)
    #print(f"Video saved to {file_path} with UUID {uuid_str}")


eel.start('index.html', size=(800, 600), block=False)
#eel.start('three.html', size=(800, 600), block=False)

# Keep the app running
while True:
    eel.sleep(0.1)