function startRecordingEvent() {
    console.log("Event started!");
    document.getElementById('idle-animation').style.display = 'none';
    document.getElementById('camera-animation').style.display = 'block';
    eel.record_data(); // Trigger Python side
    startCountdown(10); // Start the countdown with the duration (e.g., 10 seconds)
  }

// Expose the function to be called from Python
eel.expose(startRecordingEvent);

document.addEventListener('keydown', function (e) {
  if (e.key === 'Enter') {
    console.log("Enter key pressed");
    document.getElementById('idle-animation').style.display = 'none';
    document.getElementById('camera-animation').style.display = 'block';
    eel.record_data(); // Trigger Python side
    startCountdown(10); // Start the countdown with the duration (e.g., 10 seconds)
  }
});

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
  document.getElementById('idle-animation').style.display = 'flex';

  eel.trigger_animation();
  eel.process_frames(uuid)
  
}