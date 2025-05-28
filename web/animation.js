function startAnimation() {
    // Create a GSAP timeline
    const timeline = gsap.timeline({ repeat: -1 }); // `repeat: -1` makes it loop infinitely
  
    // Animate the first element (#text)
    timeline.to("#text", {
      opacity: 1,
      y: 0,
      duration: 1.5,
      ease: "power2.out",
    });
  
    // Fade out the first element (#text) before the second one appears
    timeline.to("#text", {
        opacity: 0,
        y: -40,
        duration: 0.5,
        ease: "power2.in",
    });

    // Animate the second element (#text2) after #text fades out
    timeline.to("#text2", {
        opacity: 1,
        y: 0,
        duration: 1.5,
        ease: "power2.out",
    });

    // Fade out the second element (#text2) before restarting the loop
    timeline.to("#text2", {
        opacity: 0,
        x: 10,
        y: 0,
        duration: 0.5,
        ease: "power2.in",
    });
  
    // Hide both elements before restarting the loop
    timeline.to("#text", {
      opacity: 0,
      y: -20,
      duration: 0.5,
      ease: "power2.in",
    });
    timeline.to("#text2", {
      opacity: 0,
      y: -20,
      duration: 0.5,
      ease: "power2.in",
    });
  }
  
  
  // Expose to Python
  eel.expose(startAnimation);
  
  // Optionally trigger on load
  window.onload = () => {
    setTimeout(() => {
      startAnimation();
    }, 1000);  // 1-second delay
  };