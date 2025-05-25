#from segment_display import *
#from ultrasonic_sensor import *

import time
import cv2
import uuid
import threading
import keyboard  # pip install keyboard

CAMERA_DEVICE = 0

def generate_uuid_filename():
    return str(uuid.uuid4().int)[:6] + ".mp4"

def record_video_with_countdown(duration=10, resolution=(640, 480)):
    filename = generate_uuid_filename()
    print(f"Recording video: {filename}")

    cap = cv2.VideoCapture(CAMERA_DEVICE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 20.0, resolution)

    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Add countdown overlay
        remaining = duration - int(time.time() - start_time)
        cv2.putText(frame, f"Recording... {remaining}s", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        out.write(frame)
        cv2.imshow("Recording...", frame)
        if cv2.waitKey(1) == 27:  # ESC to exit early
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video saved as: {filename}")

def animate_text_loop(interrupt_event):
    message = "Hello there, this is an animated message. Press 'r' to record video."
    while not interrupt_event.is_set():
        for char in message:
            print(char, end='', flush=True)
            time.sleep(0.05)
            if interrupt_event.is_set():
                break
        print("\n")
        time.sleep(1)

def main():
    interrupt_event = threading.Event()

    # Thread for animated text
    text_thread = threading.Thread(target=animate_text_loop, args=(interrupt_event,))
    text_thread.start()

    try:
        while True:
            if keyboard.is_pressed('r'):
                print("\n[INTERRUPT] Starting recording...")
                interrupt_event.set()
                text_thread.join()

                record_video_with_countdown(duration=10)

                # Restart the animation loop
                interrupt_event.clear()
                text_thread = threading.Thread(target=animate_text_loop, args=(interrupt_event,))
                text_thread.start()

            time.sleep(0.1)
    except KeyboardInterrupt:
        interrupt_event.set()
        text_thread.join()
        print("Program exited.")

if __name__ == "__main__":
    main()