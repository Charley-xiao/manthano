<script lang="ts" setup>
import axios from 'axios';
import * as THREE from 'three';

const route = useRoute();
const tag = Array.isArray(route.query.tag) ? route.query.tag[0] : route.query.tag;

const posts = ref<Array<{ id: number; course_id: number; title: string; sender_name: string; content: string; likes: number; date_submitted: string; }>>([]);

const gradients = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #ff6a00, #ee0979)',
    'linear-gradient(135deg, #42e695, #3bb2b8)',
    'linear-gradient(135deg, #ff512f, #dd2476)',
    'linear-gradient(135deg, #24c6dc, #514a9d)',
    'linear-gradient(135deg, #ff9a9e, #fecfef)',
    'linear-gradient(135deg, #a1c4fd, #c2e9fb)',
    'linear-gradient(135deg, #fbc2eb, #a6c1ee)'
];

function getRandomGradient() {
    return gradients[Math.floor(Math.random() * gradients.length)];
}

async function getPosts() {
    await axios.get(`/api/post/tag/${tag}`)
        .then((response) => {
            response.data.posts.forEach((p: Array<any>) => {
                const post = {
                    id: p[0],
                    course_id: p[1],
                    title: p[2],
                    sender_name: p[3],
                    content: p[4],
                    likes: p[5],
                    date_submitted: p[7]
                };
                posts.value.push(post);
            });
        })
        .catch((error) => {
            console.error('Failed to fetch posts:', error);
        });
}

onMounted(async () => {
    await getPosts();
    init3D();
});

function init3D() {
    const canvas = document.getElementById('tag-canvas') as HTMLCanvasElement;

    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
    renderer.setSize(window.innerWidth, 300);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 300, 0.1, 1000);
    camera.position.z = 5;

    // Sphere with glowing effect
    const geometry = new THREE.SphereGeometry(2, 32, 32);
    const material = new THREE.MeshBasicMaterial({ color: 0x42a5f5, wireframe: true });
    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);

    const glowMaterial = new THREE.ShaderMaterial({
        uniforms: {
            glowColor: { value: new THREE.Color(0x42a5f5) },
            intensity: { value: 1.0 }
        },
        vertexShader: `
            varying float intensity;
            void main() {
                vec3 vNormal = normalize(normalMatrix * normal);
                vec3 vLight = vec3(0.5, 0.2, 1.0);
                intensity = dot(vNormal, vLight);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            varying float intensity;
            uniform vec3 glowColor;
            void main() {
                gl_FragColor = vec4(glowColor * intensity, 1.0);
            }
        `,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending,
        transparent: true,
    });

    const glow = new THREE.Mesh(geometry.clone(), glowMaterial);
    glow.scale.multiplyScalar(1.2);
    scene.add(glow);

    const animate = () => {
        requestAnimationFrame(animate);
        sphere.rotation.x += 0.01;
        sphere.rotation.y += 0.01;
        glow.rotation.x += 0.01;
        glow.rotation.y += 0.01;
        renderer.render(scene, camera);
    };

    animate();
}
</script>



<template>
    <div class="tag-page">
        <!-- Dynamic Header -->
        <div class="tag-header">
            <h1>Tag: {{ tag }}</h1>
            <canvas id="tag-canvas"></canvas>
        </div>

        <!-- Post List -->
        <div class="posts-grid">
            <div 
                v-for="post in posts" 
                :key="post.id" 
                class="post-card" 
                :style="{ background: getRandomGradient() }"
                @click="$router.push({ path: `/community/post/${post.id}` })"
            >
                <h2>{{ post.title }}</h2>
                <p class="post-meta">{{ post.sender_name }} - {{ post.date_submitted }}</p>
                <p class="post-content">{{ post.content }}</p>
                <p class="post-likes">{{ post.likes }} likes</p>
            </div>
        </div>
    </div>
</template>


<style scoped>
/* General Styling */
body {
    margin: 0;
    font-family: 'Arial', sans-serif;
    background-color: #f0f0f5;
    color: #333;
    overflow-x: hidden;
}

/* Tag Header */
.tag-header {
    position: relative;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    text-align: center;
    background: linear-gradient(45deg, #42a5f5, #7b1fa2, #f50057, #00e676);
    background-size: 400% 400%;
    animation: gradientShift 10s infinite;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.tag-header h1 {
    position: absolute;
    z-index: 10;
    color: white;
    font-size: 36px;
    font-weight: bold;
    text-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
    margin: 0;
}

#tag-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 300px;
    pointer-events: none;
    z-index: 0;
}

/* Post Grid */
.posts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px;
}

/* Post Card */
.post-card {
    padding: 20px;
    border-radius: 15px;
    color: white;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    overflow: hidden;
}

.post-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.2);
}

.post-card h2 {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
}

.post-meta {
    font-size: 14px;
    color: #e1e1e1;
    margin-bottom: 10px;
}

.post-content {
    font-size: 16px;
    margin-bottom: 10px;
}

.post-likes {
    font-size: 14px;
    font-weight: bold;
}

/* Responsive Design */
@media (max-width: 600px) {
    .posts-grid {
        grid-template-columns: 1fr;
    }

    .tag-header h1 {
        font-size: 28px;
    }
}
</style>
