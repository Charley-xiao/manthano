<template>
    <div class="home-page">
        <canvas ref="canvas" class="background"></canvas>

        <div class="content">
            <h1 class="slogan">Manthano</h1>
            <h1 class="slogan-small">Inspire, Inquire, Aspire</h1>
            <p class="description">Empowering learning journeys through interactive courses.</p>
            <div v-if="!isLoggedIn" class="buttons">
                <router-link to="/login" class="btn btn-login">Login</router-link>
                <router-link to="/register" class="btn btn-register">Register</router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount } from 'vue';
import { isLoggedIn } from '../../store/index.d';
import * as THREE from 'three';
import { OrbitControls } from '@three-ts/orbit-controls';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import helvetikerFont from 'three/examples/fonts/helvetiker_regular.typeface.json'; // Load default font


const canvas = ref<HTMLCanvasElement | null>(null);
let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer;
let objects: THREE.Mesh[] = [];
let particles: THREE.Points, particleMaterial: THREE.PointsMaterial;
let equations: THREE.Mesh[] = [];

const formulas = [
    "E = mc^2",
    "F = ma",
    "P = NP?",
    "x^2 + y^2 = r^2",
    "L = λW",
    "PV = nRT",
    "V = IR",
    "F = q(E + v x B)",
];

const init3DScene = () => {
    if (canvas.value) {
        scene = new THREE.Scene();

        camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5;

        renderer = new THREE.WebGLRenderer({ canvas: canvas.value });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 1;
        controls.maxDistance = 50;

        const loader = new FontLoader();
        const font = loader.parse(helvetikerFont);

        // Generate floating equations
        formulas.forEach((formula) => {
            const geometryText = new TextGeometry(formula, {
                font: font,
                size: 0.4,
                height: 0.05,
            });
            const materialText = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const textMesh = new THREE.Mesh(geometryText, materialText);

            textMesh.position.set((Math.random() - 0.5) * 10, (Math.random() - 0.5) * 10, (Math.random() - 0.5) * 10);
            textMesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI);

            scene.add(textMesh);
            equations.push(textMesh);
        });

        const material = new THREE.ShaderMaterial({
            uniforms: {
                color1: { value: new THREE.Color(0x667eea) },
                color2: { value: new THREE.Color(0x764ba2) }
            },
            vertexShader: `
              varying vec2 vUv;
              void main() {
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
              }
            `,
            fragmentShader: `
              uniform vec3 color1;
              uniform vec3 color2;
              varying vec2 vUv;
              void main() {
                gl_FragColor = vec4(mix(color1, color2, vUv.y), 1.0);
              }
            `,
            side: THREE.BackSide,
        });
        const geometry = new THREE.SphereGeometry(500, 64, 64);
        const backgroundMesh = new THREE.Mesh(geometry, material);
        scene.add(backgroundMesh);

        const geometryIcosahedron = new THREE.IcosahedronGeometry(1, 0);
        const materialIcosahedron = new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true });
        const icosahedron = new THREE.Mesh(geometryIcosahedron, materialIcosahedron);
        scene.add(icosahedron);
        objects.push(icosahedron);

        const geometryCube = new THREE.BoxGeometry(1, 1, 1);
        const materialCube = new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });
        const cube = new THREE.Mesh(geometryCube, materialCube);
        cube.position.set(-2, 1, -1);
        scene.add(cube);
        objects.push(cube);

        const particlesGeometry = new THREE.BufferGeometry();
        const particlesCount = 500;
        const positions = new Float32Array(particlesCount * 3);
        const colors = new Float32Array(particlesCount * 3);
        for (let i = 0; i < particlesCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 10;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
            const hue = Math.random() * 60 + 30;
            const saturation = 0.5 + Math.random() * 0.3;
            const lightness = 0.4 + Math.random() * 0.2;
            const color = new THREE.Color().setHSL(hue / 360, saturation, lightness);

            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }
        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        particleMaterial = new THREE.PointsMaterial({
            size: 0.05,
            vertexColors: true
        });
        particles = new THREE.Points(particlesGeometry, particleMaterial);
        scene.add(particles);

        window.addEventListener('mousemove', onMouseMove);

        const animate = () => {
            requestAnimationFrame(animate);

            // Rotate floating objects
            equations.forEach(eq => {
                eq.rotation.x += 0.01;
                eq.rotation.y += 0.01;
            });

            objects.forEach(obj => {
                obj.rotation.x += 0.01;
                obj.rotation.y += 0.01;
            });

            particles.rotation.x += 0.002;
            particles.rotation.y += 0.002;

            controls.update();
            renderer.render(scene, camera);
        };

        animate();
    }
};

const onMouseMove = (event: MouseEvent) => {
    const mouseX = (event.clientX / window.innerWidth) * 2 - 1;
    const mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

    objects.forEach(obj => {
        obj.rotation.x += mouseY * 0.1;
        obj.rotation.y += mouseX * 0.1;
    });
};

onMounted(() => {
    init3DScene();
});

onBeforeUnmount(() => {
    if (canvas.value) {
        scene.clear();
        renderer.dispose();
        canvas.value = null;
    }
    window.removeEventListener('mousemove', onMouseMove);
});

// return {
//     canvas,
// };

</script>

<style scoped>
.home-page {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    overflow: hidden;
    position: relative;
}

.background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
}

.content {
    position: relative;
    z-index: 1;
    text-align: center;
    color: white;
    animation: fadeIn 1s ease-in-out;
}

.slogan {
    font-size: 4rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5);
}

.slogan-small {
    font-size: 2rem;
    margin: 0;
}

.description {
    font-size: 1.5rem;
    margin: 20px 0;
}

.buttons {
    display: flex;
    gap: 20px;
}

.btn {
    padding: 10px 30px;
    font-size: 1.2rem;
    border-radius: 50px;
    text-decoration: none;
    color: #fff;
    transition: background-color 0.3s;
}

.btn-login {
    background-color: #00b894;
}

.btn-register {
    background-color: #0984e3;
}

.btn:hover {
    background-color: #636e72;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
