TEXT_FADE_IN= 1;
TEXT_FADE_OUT = 1;
TEXT_STAY_DURATION = 3;
EASE = "power2.out";

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
  function startAnimationTopIdle() {

    resetAnimation();
    document.getElementById("idle-animation").style.display = "flex";
    
    // Create a GSAP timeline
    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
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

  }
  function startAnimationTopRoom() {
    // Clear all running animations in the window
    
    resetAnimation();

    document.getElementById("room-animation").style.display = "flex";

    // Create a GSAP timeline
    timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#idle-animation-1)
    timeline.to("#room-animation-1", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-1", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#room-animation-1", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#room-animation-2", {
      opacity: 1, // Fade in the container
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex",
    })
    .to("#room-animation-2a", {
      opacity: 1, // Fade in the first sub-element
      duration: TEXT_FADE_IN / 2, // Half the duration of the container fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-2b", {
      opacity: 1, // Fade in the second sub-element
      duration: TEXT_FADE_IN / 2, // Duration of fade-in for the second sub-element
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    }, `+=${TEXT_STAY_DURATION / 2}`) // Start halfway through the stay duration
    .to("#room-animation-2", {
      opacity: 1, // Keep the container visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#room-animation-2", {
      opacity: 0, // Fade out the container
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#room-animation-3", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
      onStart: () => {
        document.getElementById("room-animation-3").style.display = "flex"; // Ensure visibility
        resetScrollPosition(); // Reset the scroll position to the top
        startScrollingList(); // Start scrolling the list
      },
    })
    .to("#room-animation-3", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION*2, // Duration to stay visible
    })
    .to("#room-animation-3", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
      onComplete: () => stopScrollingList(), // Stop scrolling the list when hidden
    });

    timeline.to("#room-animation-4", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
      onStart: () => {
        document.getElementById("room-animation-4").style.display = "flex"; // Ensure visibility
        resetScrollPosition(); // Reset the scroll position to the top
        startScrollingList(); // Start scrolling the list
      },
    })
    .to("#room-animation-4", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#room-animation-4", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
      onComplete: () => stopScrollingList(), // Stop scrolling the list when hidden
    });

    timeline.to("#room-animation-5", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-5", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION, // Duration to stay visible
    })
    .to("#room-animation-5", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    timeline.to("#room-animation-6", {
      opacity: 1, // Fade in
      duration: TEXT_FADE_IN, // Duration of fade-in
      ease: "power2.out",
      display: "flex", // Ensure it is displayed
    })
    .to("#room-animation-6", {
      opacity: 1, // Keep visible
      duration: TEXT_STAY_DURATION*1.5, // Duration to stay visible
    })
    .to("#room-animation-6", {
      opacity: 0, // Fade out
      duration: TEXT_FADE_OUT, // Duration of fade-out
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });
  
  }

  function resetScrollPosition() {
    const list1 = document.getElementById("scroll-list-1");
    const list2 = document.getElementById("scroll-list-2");
    const list3 = document.getElementById("scroll-list-3");
  
    console.log("List 1:", list1);
    console.log("List 2:", list2);
    console.log("List 3:", list3);
  
    if (!list1 || !list2 || !list3) {
      console.warn("One or more lists are not found in the DOM.");
      return;
    }
  
    gsap.set(list1, { y: 0 }); // Reset the scroll position to the top
    gsap.set(list2, { y: 0 });
    gsap.set(list3, { y: 0 });
  }
  function startScrollingList() {
    const lists = [
      document.getElementById("scroll-list-1"),
      document.getElementById("scroll-list-2"),
      document.getElementById("scroll-list-3"), // Add more lists as needed
    ];
    const container = document.getElementById("scroll-container");
  
    // Temporarily make the container and lists visible to calculate heights
    container.style.display = "block";
    lists.forEach((list) => {
      if (list) list.style.display = "block";
    });
  
    const containerHeight = container.offsetHeight; // Height of the visible container
    console.log("Container Height:", containerHeight);
  
    lists.forEach((list, index) => {
      if (!list) {
        console.warn(`List ${index + 1} not found.`);
        return;
      }
  
      const listHeight = list.offsetHeight; // Total height of the current list
      console.log(`List ${index + 1} Height:`, listHeight);
  
      // Reset the scroll position to the top
      gsap.set(list, { y: 0 });
  
      // Ensure the list scrolls even if it's smaller than the container
      const scrollDistance = Math.max(listHeight - containerHeight, 100); // Minimum scroll distance is 100px
  
      gsap.to(list, {
        y: -scrollDistance, // Scroll the list upwards
        duration: 10, // Duration of the scrolling animation
        ease: "linear",
        repeat: -1, // Repeat the scrolling infinitely
      });
    });
  
    // Restore the original display property
    container.style.display = "";
    lists.forEach((list) => {
      if (list) list.style.display = "";
    });
  } 
  function stopScrollingList() {
    // Stop the scrolling animation
    gsap.killTweensOf("#scroll-list");
  }
  
  // Expose to Python
  eel.expose(startAnimationTopIdle);
  eel.expose(startAnimationTopRoom);
  
  // Optionally trigger on load
  window.onload = () => {
    setTimeout(() => {
      startAnimationTopIdle();
    }, 1000);  // 1-second delay
  };