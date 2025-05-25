import * as THREE from 'three';


const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

scene.background = new THREE.Color(0xffffff); // Set background to white

// Set up basic scene properties

const scale = 1;
const speed = 0.002;
const maxPoints = 1000;
const selectedFile = 'pca_output.json';

const group = new THREE.Group();
scene.add(group);

camera.position.z = 10;

function loadSprites(data) {
  const loader = new THREE.TextureLoader();
  const limitedSprites = data.slice(0, Math.min(maxPoints, data.length));

  limitedSprites.forEach((item) => {
    loader.load(item.imageUrl, (texture) => {
      texture.flipY = false; // Ensure texture is not flipped
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

// Animation loop
let zoomingIn = false;
let zoomingOut = false;
let zoomTarget = 5; // Target zoom level when zooming in
let zoomSpeed = 0.1; // Speed of zooming

// Animation loop
function animate() {
    requestAnimationFrame(animate);
  
    // Rotate the group (globe)
    group.rotation.y += speed;
  
    // Handle zooming in
    if (zoomingIn && camera.position.z > zoomTarget) {
      camera.position.z -= zoomSpeed;
      if (camera.position.z <= zoomTarget) {
        zoomingIn = false;
        zoomingOut = true; // Start zooming out
      }
    }
  
    // Handle zooming out
    if (zoomingOut && camera.position.z < 10) {
      camera.position.z += zoomSpeed;
      if (camera.position.z >= 10) {
        zoomingOut = false; // Stop zooming out
      }
    }
  
    renderer.render(scene, camera);
  }
  
animate();

document.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      console.log('Enter key pressed');
      zoomingIn = true; // Start zooming in
      zoomingOut = false; // Ensure we don't zoom out immediately
    }
  });

