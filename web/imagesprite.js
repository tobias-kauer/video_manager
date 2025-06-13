import * as THREE from 'three';


const similarity_threshold = 64; // Threshold for similarity detection
const camera_position_z = 100; // Initial camera position on the z-axis


const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.background = new THREE.Color(0xffffff); // Set background to white

// Set up basic scene properties

const scale = 4;
const speed = 0.002;
const maxPoints = 1000;
const selectedFile = 'data/tsne_images/tsne_output.json';
const enableSimilarityBackground = true; // Flag to enable/disable similarity-based backgrounds

const group = new THREE.Group();
scene.add(group);

camera.position.z = camera_position_z;

// Center the sprite group in the scene
group.position.set(0, 0, 0);

function loadSprites(data) {
  const loader = new THREE.TextureLoader();
  const limitedSprites = data.slice(0, Math.min(maxPoints, data.length));

  // Extract the base path from the selected file URL
  const basePath = selectedFile.substring(0, selectedFile.lastIndexOf('/') + 1);

  limitedSprites.forEach((item) => {
    const imageUrl = basePath + item.imageUrl;

    loader.load(imageUrl, (texture) => {
      texture.flipY = true; // Ensure texture is not flipped
      texture.encoding = THREE.sRGBEncoding; // Use sRGB color space for proper rendering


      const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true, // Enable transparency
        alphaTest: 0.1, // Discard fully transparent pixels
      });

      const sprite = new THREE.Sprite(material);
      sprite.position.set(...item.position);
      sprite.scale.set(scale, scale, 1);

      // Add similarity-based background if enabled
      if (enableSimilarityBackground && item.similarity > similarity_threshold) {
        const similarity = item.similarity || 0; // Default to 0 if similarity is not defined
        const redOpacity = similarity / 200; // Scale similarity to opacity (0 to 1)

        // Create a frame sprite slightly larger than the image
        const frameMaterial = new THREE.SpriteMaterial({
          color: new THREE.Color(1, 0, 0), // Pure red color
          transparent: true,
          opacity: redOpacity, // Set opacity based on similarity
        });

        const frameSprite = new THREE.Sprite(frameMaterial);
        frameSprite.position.copy(sprite.position); // Match position of the sprite
        frameSprite.scale.set(scale * 1.2, scale * 1.2, 1); // Slightly larger than the sprite
        group.add(frameSprite);
      }

      group.add(sprite);
    });
  });
}

console.log(`Fetching file from: /${selectedFile}`);
fetch(`/${selectedFile}`)
  .then((res) => res.json())
  .then(loadSprites)
  .catch((err) => console.error('Failed to load sprite data:', err));
/*
console.log('Sprite data loaded, starting animation...');
function animate() {
  requestAnimationFrame(animate);
  group.rotation.y += speed;
  renderer.render(scene, camera);
}*/

// Handle window resize
function onWindowResize() {
  // Update camera aspect ratio and projection matrix
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  // Update renderer size
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// Add event listener for window resize
window.addEventListener('resize', onWindowResize, false);



let animationComplete = false; // Flag to indicate when the animation is done

function moveCamera(moveSpeed, targetPosition) {
    animationComplete = false; // Reset the flag

    function animateCamera() {
        // Check if the camera is close enough to the target position
        if (Math.abs(camera.position.z - targetPosition) <= moveSpeed) {
            camera.position.z = targetPosition; // Snap to the target position
            animationComplete = true; // Set the flag to true
            return; // Stop the animation
        }

        // Move the camera towards the target position
        if (camera.position.z < targetPosition) {
            camera.position.z += moveSpeed; // Move forward
        } else if (camera.position.z > targetPosition) {
            camera.position.z -= moveSpeed; // Move backward
        }

        // Continue animating
        requestAnimationFrame(animateCamera);
    }

    // Start the animation
    animateCamera();
}

// Example usage in your Eel application
eel.expose(triggerCameraMove);
function triggerCameraMove(moveSpeed, targetPosition) {
    moveCamera(moveSpeed, targetPosition);
    return animationComplete; // Return the flag when the animation is done
}


// Animation loop
let movingForward = false;
let movingBackward = false;
let moveTarget = 2; // Target position when moving forward
let moveSpeed = 0.05; // Speed of movement



// Animation loop
function animate() {
    requestAnimationFrame(animate);
  
    // Rotate the group (globe)
    group.rotation.y += speed;
  
    // Handle moving forward
    if (movingForward && camera.position.z > moveTarget) {
        camera.position.z -= moveSpeed;
        if (camera.position.z <= moveTarget) {
            movingForward = false;
            movingBackward = true; // Start moving backward
        }
    }
  
    // Handle moving backward
    if (movingBackward && camera.position.z < camera_position_z) {
        camera.position.z += moveSpeed;
        if (camera.position.z >= camera_position_z) {
            movingBackward = false; // Stop moving backward
        }
    }
  
    renderer.render(scene, camera);
}
  
animate();

// Add event listener for "Enter" key to start moving forward
document.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
      console.log('Enter key pressed');
      movingForward = true; // Start moving forward
      movingBackward = false; // Ensure we don't move backward immediately
  }
});

