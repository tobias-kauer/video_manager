import { triggerCameraMove } from './imagesprite.js';

const TEXT_FADE_IN= 1;
const TEXT_FADE_OUT = 1;
const TEXT_STAY_DURATION = 3;
const EASE = "power2.out";

const WAIT_TIME_ROOM = (TEXT_FADE_IN+TEXT_STAY_DURATION+TEXT_FADE_OUT)*6 + TEXT_FADE_IN/2;

let timeline;

// Function to start the idle animation at the top

  function resetAnimation() {

    gsap.killTweensOf("*");

    if (timeline) {
      timeline.kill();
    }

    document.getElementById("idle-animation").style.display = "none"; 
    document.getElementById("room-animation").style.display = "none"; 
    document.getElementById("camera-animation").style.display = "none";
    
    const elementsToReset = [
      document.getElementById("idle-animation-1"),
      document.getElementById("room-animation-1"),
      document.getElementById("room-animation-2"),
      document.getElementById("room-animation-3"),
      document.getElementById("room-animation-4"),
      document.getElementById("room-animation-5"),
      document.getElementById("room-animation-6"),
    ];
    
    elementsToReset.forEach((element) => {
      if (element) {
          element.style.display = "none"; // Hide all elements initially
          element.style.opacity = 0; // Ensure opacity is reset
      }
    });

    //special treatment
    document.getElementById("room-animation-2a").style.opacity = 0; // Reset opacity of sub-element 2a
    document.getElementById("room-animation-2b").style.opacity = 0; // Reset opacity of sub-element 2b

  }
  function startAnimationSideIdle() {

    //resetAnimation();
    //document.getElementById("idle-animation").style.display = "flex";
    
    // Create a GSAP timeline
    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#idle-animation-1)
    timeline.to("#overlay", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      onStart: () => {
        triggerCameraMove(0.5, 50); // Call the function from imagesprite.js
      },
    })
    .to("#overlay", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#overlay", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
    });

  }
  function startAnimationSideRoom() {
    // Clear all running animations in the window
  
    //document.getElementById("room-animation").style.display = "flex";

    // Create a GSAP timeline
    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    timeline.to("#placeholder", {
      opacity: 1, // Fade in
      duration: WAIT_TIME_ROOM, // Duration of fade-in
      ease: "power2.out",
      onStart: () => {
        triggerCameraMove(0.005, 1); // Call the function from imagesprite.js
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
  
  }

  
  
  // Expose to Python
  eel.expose(startAnimationSideIdle);
  eel.expose(startAnimationSideRoom);
  
  // Optionally trigger on load
  /*
  window.onload = () => {
    setTimeout(() => {
      startAnimationSideIdle();
    }, 1000);  // 1-second delay
  };*/