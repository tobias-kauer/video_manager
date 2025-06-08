function startAnimationTopIdle() {
    // Create a GSAP timeline
    const timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#idle-animation-1)
    timeline.to("#idle-animation-1", {
      opacity: 1,
      y: 0,
      duration: 2,
      ease: "power2.out",
      display: "block", // Ensure it is displayed
    });

    // Fade out the first element (#idle-animation-1)
    timeline.to("#idle-animation-1", {
      opacity: 0,
      y: 0,
      duration: 2,
      ease: "power2.in",
      display: "none", // Hide it after fading out
    });

    // Animate the second element (#idle-animation-2)
    timeline.to("#idle-animation-2", {
      opacity: 1,
      y: 0,
      duration: 8,
      ease: "power2.out",
      display: "block",
      onStart: () => {
        document.getElementById("idle-animation-2").style.display = "block"; // Ensure visibility
        resetScrollPosition(); // Reset the scroll position to the top
        startScrollingList();
      },
    });

    // Fade out the second element (#idle-animation-2)
    timeline.to("#idle-animation-2", {
      opacity: 0,
      y: 0,
      duration: 0.5,
      ease: "power2.in",
      display: "none",
      onComplete: () => stopScrollingList(), // Stop scrolling the list when hidden
    });

    // Animate the third element (#idle-animation-3)
    timeline.to("#idle-animation-3", {
      opacity: 1,
      y: 0,
      duration: 1.5,
      ease: "power2.out",
      display: "block",
    });

    // Fade out the third element (#idle-animation-3)
    timeline.to("#idle-animation-3", {
      opacity: 0,
      y: 0,
      duration: 0.5,
      ease: "power2.in",
      display: "none",
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