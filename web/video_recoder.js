const RECORDING_DURATION = 10; // Configurable recording duration in seconds

function startRecordingEvent() {
    console.log("Event started!");
    document.getElementById('idle-animation').style.display = 'none';
    document.getElementById('room-animation').style.display = 'none';
    document.getElementById('camera-animation').style.display = 'block';

    eel.record_data();

    startPreRecordingCountdown(3, () => {

      document.getElementById('live-view-container').style.display = 'flex';
      startRecordingCountdown(RECORDING_DURATION);
    });
  }

// Expose the function to be called from Python
eel.expose(startRecordingEvent);

// Function to start the pre-recording countdown
function startPreRecordingCountdown(duration, callback) {
  const preCountdownTimer = document.getElementById('pre-countdown-timer');
  const preRecordingCountdown = document.getElementById('pre-recording-countdown');
  preRecordingCountdown.style.display = 'block';

  let remainingTime = duration;

  const preCountdownInterval = setInterval(() => {
    preCountdownTimer.textContent = remainingTime;
    remainingTime--;

    if (remainingTime < 0) {
      clearInterval(preCountdownInterval);
      preRecordingCountdown.style.display = 'none'; // Hide the pre-recording countdown
      callback(); // Trigger the callback to start the recording countdown
    }
  }, 1000);
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') {
    console.log("Enter key pressed");
    document.getElementById('idle-animation').style.display = 'none';
    document.getElementById('camera-animation').style.display = 'block';
    eel.record_data(); // Trigger Python side
    startCountdown(10); // Start the countdown with the duration (e.g., 10 seconds)
  }
});

// Function to start the recording countdown
function startRecordingCountdown(duration) {
  const countdownTimer = document.getElementById('countdown-timer');
  const recordingCountdown = document.getElementById('recording-countdown');
  const blinkingDot = document.getElementById('blinking-dot');

  recordingCountdown.style.display = 'block';
  blinkingDot.style.display = 'inline-block';

  let remainingTime = duration;

  const countdownInterval = setInterval(() => {
    countdownTimer.textContent = remainingTime;
    remainingTime--;

    if (remainingTime < 0) {
      clearInterval(countdownInterval);
      recordingCountdown.style.display = 'none'; // Hide the recording countdown
      blinkingDot.style.display = 'none'; // Hide the blinking dot
      console.log("Recording complete!");
    }
  }, 1000);
}

// Function to start the countdown
function startCountdown(duration) {
const countdownTimer = document.getElementById('countdown-timer');
const blinkingDot = document.getElementById('blinking-dot');
let remainingTime = duration;

// Update the countdown timer every second
const countdownInterval = setInterval(() => {
  countdownTimer.textContent = `Recording: ${remainingTime}s`;
  remainingTime--;

  if (remainingTime < 0) {
    clearInterval(countdownInterval); // Stop the countdown when it reaches 0
    countdownTimer.textContent = ""; // Clear the countdown text
    blinkingDot.style.display = "none"; // Hide the blinking dot
  }
}, 1000);

// Make the red dot blink
let isDotVisible = true;
const blinkingInterval = setInterval(() => {
  if (remainingTime < 0) {
    clearInterval(blinkingInterval); // Stop blinking when the countdown ends
  } else {
    isDotVisible = !isDotVisible;
    blinkingDot.style.opacity = isDotVisible ? "1" : "0"; // Toggle visibility
  }
}, 500); // Blink every 500ms
}

// Update the live view with frames from Python
eel.expose(update_live_view);
function update_live_view(frame_data) {
const img = document.getElementById('live-view');
img.src = "data:image/jpeg;base64," + frame_data;
}

// Handle when recording is done
eel.expose(on_record_done);
function on_record_done(uuid) {
  console.log("Recording finished: " + uuid);
  document.getElementById('camera-animation').style.display = 'none';
  document.getElementById('live-view-container').style.display = 'none';

  document.getElementById('idle-animation').style.display = 'flex';
  eel.set_current_uuid(uuid)
  eel.process_frames(uuid); // Process the recording with the UUID

  eel.set_state("training"); // Set the state to idle after recording
  
}