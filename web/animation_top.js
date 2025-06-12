TEXT_FADE_IN= 1;
TEXT_FADE_OUT = 1;
TEXT_STAY_DURATION = 3;
EASE = "power2.out";

function startAnimationTopIdle() {
    // Create a GSAP timeline
    const timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#idle-animation-1)
    timeline.to("#idle-animation-1", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#idle-animation-1", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#idle-animation-1", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#idle-animation-2", {
      opacity: 1, // Fade in the container
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex",
    })
    .to("#idle-animation-2a", {
      opacity: 1, // Fade in the first sub-element
      duration: TEXT_FADE_IN / 2, // Half the duration of the container fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#idle-animation-2b", {
      opacity: 1, // Fade in the second sub-element
      duration: TEXT_FADE_IN / 2, // Duration of fade-in for the second sub-element
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    }, `+=${TEXT_STAY_DURATION / 2}`) // Start halfway through the stay duration
    .to("#idle-animation-2", {
      opacity: 1, // Keep the container visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#idle-animation-2", {
      opacity: 0, // Fade out the container
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#idle-animation-3", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
      onStart: () => {
        document.getElementById("idle-animation-3").style.display = "flex"; // Ensure visibility
        resetScrollPosition(); // Reset the scroll position to the top
        startScrollingList(); // Start scrolling the list
      },
    })
    .to("#idle-animation-3", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION*2, // Duration to stay visible
    })
    .to("#idle-animation-3", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
      onComplete: () => stopScrollingList(), // Stop scrolling the list when hidden
    });

    timeline.to("#idle-animation-4", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
      onStart: () => {
        document.getElementById("idle-animation-4").style.display = "flex"; // Ensure visibility
        resetScrollPosition(); // Reset the scroll position to the top
        startScrollingList(); // Start scrolling the list
      },
    })
    .to("#idle-animation-4", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#idle-animation-4", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
      onComplete: () => stopScrollingList(), // Stop scrolling the list when hidden
    });

    timeline.to("#idle-animation-5", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#idle-animation-5", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#idle-animation-5", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    
  
  }

  function resetScrollPosition() {
    const list = document.getElementById("scroll-list");
    gsap.set(list, { y: 0 }); // Reset the scroll position to the top
  }

  function startScrollingList() {
    const list = document.getElementById("scroll-list");
    const container = document.getElementById("scroll-container");
  
    // Temporarily make the container visible to calculate heights
    container.style.display = "block";
  
    const listHeight = list.offsetHeight; // Total height of the list
    const containerHeight = container.offsetHeight; // Height of the visible container
  
    // Restore the original display property
    container.style.display = "";
  
    // Debugging: Log the heights
    console.log("List Height:", listHeight);
    console.log("Container Height:", containerHeight);
  
    // Check if the list is taller than the container
    if (listHeight > containerHeight) {
      // Animate the list to scroll upwards
      gsap.to(list, {
        y: -(listHeight - containerHeight), // Scroll the list upwards
        duration: 10, // Duration of the scrolling animation
        ease: "linear",
        repeat: -1, // Repeat the scrolling infinitely
      });
    } else {
      console.warn("List height is smaller than container height. No scrolling needed.");
    }
  }
  
  function stopScrollingList() {
    // Stop the scrolling animation
    gsap.killTweensOf("#scroll-list");
  }
  
  // Expose to Python
  eel.expose(startAnimationTopIdle);
  
  // Optionally trigger on load
  window.onload = () => {
    setTimeout(() => {
      startAnimationTopIdle();
    }, 1000);  // 1-second delay
  };