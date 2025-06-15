import { triggerCameraMove } from './imagesprite.js';

const TEXT_FADE_IN= 1;
const TEXT_FADE_OUT = 1;
const TEXT_STAY_DURATION = 3;
const EASE = "power2.out";

const WAIT_TIME_ROOM = (TEXT_FADE_IN+TEXT_STAY_DURATION+TEXT_FADE_OUT)*6;

let timeline;

// Function to start the idle animation at the top

  function resetAnimation() {

    gsap.killTweensOf("*");

    if (timeline) {
      timeline.kill();
    }

    //document.getElementById("idle-animation").style.display = "none"; 
    document.getElementById("room-animation").style.display = "none"; 
    document.getElementById("camera-animation").style.display = "none";
    
    const elementsToReset = [
      document.getElementById("room-animation-1"),
      document.getElementById("room-animation-2"),
    ];
    
    elementsToReset.forEach((element) => {
      if (element) {
          element.style.display = "none"; // Hide all elements initially
          element.style.opacity = 0; // Ensure opacity is reset
      }
    });

  }
  function startAnimationSideIdle() {
    resetAnimation();
  }
  function startAnimationSideRoom() {
    // Clear all running animations in the window
  
    //document.getElementById("room-animation").style.display = "flex";

    // Create a GSAP timeline
    resetAnimation();

    document.getElementById("room-animation").style.display = "flex";

    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    timeline.to("#placeholder", {
      opacity: 1, // Fade in
      duration: WAIT_TIME_ROOM, // Duration of fade-in
      ease: "power2.out",
      onStart: () => {
        triggerCameraMove(0.005, 0.5); // Call the function from imagesprite.js
      },
    }) 
    
    // Animate the first element (#idle-animation-1)
    timeline.to("#room-animation-1", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-1", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION*1.5, // Duration to stay visible
    })
    .to("#room-animation-1", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#room-animation-2", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-2", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION*3, // Duration to stay visible
    })
    .to("#room-animation-2", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
      onStart: () => {
        triggerCameraMove(0.05, 10); // Call the function from imagesprite.js
      },
    });
  
  }
  function startAnimationSideCamera() {

    resetAnimation();
    document.getElementById("camera-animation").style.display = "flex";
    
    // Create a GSAP timeline
    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#idle-animation-1)
    timeline.to("#camera-animation-1", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN/2, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#camera-animation-1", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION/6, // Duration to stay visible
    })
    .to("#camera-animation-1", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT/2, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

  }

  
  
  // Expose to Python
  eel.expose(startAnimationSideIdle);
  eel.expose(startAnimationSideRoom);
  eel.expose(startAnimationSideCamera);
  
  // Optionally trigger on load
  /*
  window.onload = () => {
    setTimeout(() => {
      startAnimationSideIdle();
    }, 1000);  // 1-second delay
  };*/