import * as THREE from 'three';

// --- 1. Setup Three.js Scene ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); // Alpha for video bg

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('scene-container').appendChild(renderer.domElement);
camera.position.z = 8;

// Lighting for color spheres
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0xffffff, 1);
pointLight.position.set(5, 5, 5);
scene.add(pointLight);

// --- 2. Environment Objects ---

// A. The Trash Bin (Image)
const texLoader = new THREE.TextureLoader();
const binTexture = texLoader.load('trash_bin.png');
const binGeo = new THREE.PlaneGeometry(2, 2);
const binMat = new THREE.MeshBasicMaterial({ map: binTexture, transparent: true, side: THREE.DoubleSide });
const bin = new THREE.Mesh(binGeo, binMat);
bin.position.set(5, 5, 0); // Bottom Left
scene.add(bin);

// Label for Bin (Simple Text Mesh is hard without font loader, using position for context)

// B. Color Palette (Spheres)
const colors = [0xff0000, 0x0000ff, 0xffff00, 0x00ff00]; // Red, Blue, Yellow, Green
const paletteGroup = new THREE.Group();
colors.forEach((col, idx) => {
    const sGeo = new THREE.SphereGeometry(0.5, 32, 32);
    const sMat = new THREE.MeshStandardMaterial({ color: col });
    const sphere = new THREE.Mesh(sGeo, sMat);
    // Horizontal layout, centered at bottom (y=-3.5)
    // Centered around x=0 with spacing of 1.2
    const spacing = 1.2;
    const startX = -((colors.length - 1) * spacing) / 2;
    sphere.position.set(startX + (idx * spacing), -3.5, 0);
    sphere.userData = { isPalette: true, color: col }; // Tag for logic
    paletteGroup.add(sphere);
});
scene.add(paletteGroup);

// --- 3. Logic State ---
const blocks = [];         // All created cubes
let cursor = new THREE.Mesh(
    new THREE.SphereGeometry(0.2),
    new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 })
);
scene.add(cursor); // Follows finger

let isPinching = false;
let grabbedObject = null;
let lastPinchState = false; // For detecting "Start" of pinch
let currentSelectedColor = 0x00ff00; // Default color for new blocks

// Helper: Create a Hologram Block
function createBlock(x, y, z) {
    const group = new THREE.Group();

    // Solid Block
    const mat = new THREE.MeshBasicMaterial({
        color: currentSelectedColor, transparent: true, opacity: 1.0, // Opaque by default
        side: THREE.DoubleSide
    });
    const geo = new THREE.BoxGeometry(1, 1, 1);
    const mesh = new THREE.Mesh(geo, mat);

    // Save for restoring after bin warning
    group.userData = { originalColor: currentSelectedColor };

    group.add(mesh);
    // Wireframe removed as per request

    group.position.set(x, y, z);
    scene.add(group);
    blocks.push(group);
    return group;
}

// Animation Loop
function animate() {
    requestAnimationFrame(animate);

    // No rotation for blocks as per request

    renderer.render(scene, camera);
}
animate();

// Handle Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});


// --- 4. WebSocket & Interaction ---
const statusDiv = document.getElementById('status');
const socket = new WebSocket('ws://localhost:8765');

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Update Video Feed
    if (data.image) {
        document.getElementById('video-feed').src = "data:image/jpeg;base64," + data.image;
    }

    if (data.hand_detected && data.landmarks.length > 8) {
        statusDiv.innerText = `Gesture: ${data.gesture}`;

        // 1. Update Cursor Position
        const indexTip = data.landmarks[8];
        const cx = (indexTip[0] * 14) - 7;      // Wider range (-7 to +7)
        const cy = (1 - indexTip[1]) * 8 - 4;   // Taller range (-4 to +4)
        cursor.position.set(cx, cy, 0);

        // 2. Palette Selection (Hover to Select Color)
        paletteGroup.children.forEach(p => {
            const pPos = new THREE.Vector3();
            p.getWorldPosition(pPos);
            if (cursor.position.distanceTo(pPos) < 0.8) {
                currentSelectedColor = p.userData.color;
                cursor.material.color.setHex(currentSelectedColor); // Visual feedback
            }
        });

        // 3. Determine Pinch State
        isPinching = (data.gesture === "PINCH");

        // --- STATE MACHINE ---

        // A. PINCH STARTED (Frame 0)
        if (isPinching && !lastPinchState) {
            // Check collisions
            let touchedBlock = null;

            // Simple overlap check (sphere vs box center)
            blocks.forEach(b => {
                if (cursor.position.distanceTo(b.position) < 1.0) {
                    touchedBlock = b;
                }
            });

            if (touchedBlock) {
                // Grab Existing
                grabbedObject = touchedBlock;
                grabbedObject.children[0].material.opacity = 0.5; // Translucent when moving
            } else {
                // Create New
                grabbedObject = createBlock(cx, cy, 0);
                grabbedObject.children[0].material.opacity = 0.5; // Translucent when created/moving
            }
        }

        // B. PINCH HELD (Dragging)
        if (isPinching && grabbedObject) {
            // Move object
            grabbedObject.position.set(cx, cy, 0);

            // Bin Collision Check (Feedback only)
            if (cursor.position.distanceTo(bin.position) < 1.5) {
                statusDiv.innerText = "⚠️ DELETING BLOCK ⚠️";
                statusDiv.style.color = "red";
                grabbedObject.children[0].material.color.setHex(0xff0000); // Turn red warning
            } else {
                statusDiv.style.color = "white"; // Reset text color
                if (grabbedObject.userData.originalColor) {
                    grabbedObject.children[0].material.color.setHex(grabbedObject.userData.originalColor);
                }
            }
        }

        // C. RELEASED
        if (!isPinching && lastPinchState) {
            if (grabbedObject) {
                // Bin Collision Check
                if (cursor.position.distanceTo(bin.position) < 1.5) {
                    // Delete
                    scene.remove(grabbedObject);
                    // Remove from array
                    const idx = blocks.indexOf(grabbedObject);
                    if (idx > -1) blocks.splice(idx, 1);
                    statusDiv.style.color = "white";
                } else {
                    // Just Drop -> Become Solid
                    grabbedObject.children[0].material.opacity = 1.0; // Opaque when placed
                    // Restore color if it was red from bin warning
                    if (grabbedObject.userData.originalColor) {
                        grabbedObject.children[0].material.color.setHex(grabbedObject.userData.originalColor);
                    }
                }
                grabbedObject = null;
            }
        }

        lastPinchState = isPinching;

    } else {
        statusDiv.innerText = "No Hand Detected";
        statusDiv.style.color = "white";
        isPinching = false;
        lastPinchState = false;
        if (grabbedObject) {
            // If we lose tracking while holding, drop it safely
            grabbedObject.children[0].material.opacity = 1.0; // Opaque
            if (grabbedObject.userData.originalColor) {
                grabbedObject.children[0].material.color.setHex(grabbedObject.userData.originalColor);
            }
            grabbedObject = null;
        }
    }
};
