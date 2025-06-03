import * as THREE from 'three';


const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.background = new THREE.Color(0xffffff); // Set background to white

// Set up basic scene properties

const scale = 0.4;
const speed = 0.002;
const maxPoints = 1000;
const selectedFile = 'pca_output.json';

const group = new THREE.Group();
scene.add(group);

camera.position.z = 10;

// Center the sprite group in the scene
group.position.set(0, 0, 0);

function loadSprites(data) {
  const loader = new THREE.TextureLoader();
  const limitedSprites = data.slice(0, Math.min(maxPoints, data.length));

  limitedSprites.forEach((item) => {
    loader.load(item.imageUrl, (texture) => {
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


// Animation loop
let movingForward = false;
let movingBackward = false;
let moveTarget = 2; // Target position when moving forward
let moveSpeed = 0.01; // Speed of movement

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
    if (movingBackward && camera.position.z < 10) {
        camera.position.z += moveSpeed;
        if (camera.position.z >= 10) {
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

