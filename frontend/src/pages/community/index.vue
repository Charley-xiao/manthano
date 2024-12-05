<script setup lang="ts">
import axios from "axios";
import { ref, onMounted } from "vue";

interface Post {
  id: number;
  course_id: number;
  title: string;
  sender_name: string;
  content: string;
  date_submitted: string;
  likes: number;
  tag: string;
}

const posts = ref<Post[]>([]);

async function fetchPosts() {
  const response = await axios.get('/api/posts');
  const data = response.data;
  posts.value = data.posts;
  posts.value.sort((a, b) => {
    return new Date(b.date_submitted).getTime() - new Date(a.date_submitted).getTime();
  });
  console.table(posts.value)
}

const tags = ref(['Academic', 'Career', 'Lifestyle', 'Tech', 'Health']);

const colors = [
  "linear-gradient(135deg, #667eea, #764ba2)",
  "linear-gradient(135deg, #ff6a00, #ee0979)",
  "linear-gradient(135deg, #42e695, #3bb2b8)",
  "linear-gradient(135deg, #ff512f, #dd2476)",
  "linear-gradient(135deg, #24c6dc, #514a9d)"
];

onMounted(async () => {
  await fetchPosts();

  const cardHeaders: NodeListOf<HTMLElement> = document.querySelectorAll('div.card-header');

  cardHeaders.forEach(cardHeader => {
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    cardHeader.style.background = randomColor;
  });
});

</script>

<template>
  <div class="sticky-button-container">
    <button class="super-funky-button" @click="$router.push('/community/write')">New Post</button>
  </div>
  <div id="main-page" class="main-container">
    <header class="header">
      <h1>Study Forum</h1>
      <p>Your hub for shared knowledge and tips</p>
    </header>

    <main>
      <!-- Recent Posts Grid -->
      <section class="recent-posts">
        <h2>Recent Discussions</h2>
        <div class="posts-grid">
          <div class="post-card enhanced" v-for="post in posts.slice(0, 3)" :key="post.id">
            <div class="post-header">
              <h3>{{ post.title }}</h3>
              <span class="post-tag">{{ post.tag }}</span>
            </div>
            <p class="post-excerpt">{{ post.content.substring(0, 80) }}...</p>

            <!-- Updated Meta Information -->
            <div class="post-meta">
              <div class="meta-item">
                <i class="icon sender"></i>
                <span>{{ post.sender_name }}</span>
              </div>
              <div class="meta-item">
                <i class="icon date"></i>
                <span>{{ new Date(post.date_submitted).toLocaleDateString() }}</span>
              </div>
              <div class="meta-item">
                <i class="icon likes"></i>
                <span>{{ post.likes }} Likes</span>
              </div>
            </div>

            <router-link :to="'/community/post/' + post.id" class="read-more">Read More</router-link>
          </div>
        </div>
      </section>

      <h2>Tags</h2>
      <section class="tag-container">
        <div class="tag" v-for="(tag, index) in tags"
          @click="$router.push({ path: '/community/tag/', query: { tag: tag } })" :key="index"
          :style="`--i: ${index + 1}`">{{ tag }}</div>
      </section>
    </main>

    <footer>
      <p>&copy; 2024 Study Forum. Built for learners.</p>
      <nav>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background: #f4f4f9;
  color: #333;
  margin: 0;
  padding: 0;
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Header Styling */
.header {
  text-align: center;
  padding: 50px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  animation: fade-in 1s ease-in-out;
}

.header h1 {
  font-size: 2.5rem;
  margin: 0;
}

.header p {
  font-size: 1rem;
  margin-top: 10px;
}

h2 {
  font-size: 1.8rem;
  border-bottom: 2px solid #ddd;
  padding-bottom: 10px;
  margin-bottom: 20px;
  font-weight: 600;
  color: #333;
  /* set a soft font */
  font-family: 'Times New Roman', Times, serif;
}

/* Featured Post */
.featured-post {
  margin-bottom: 40px;
}

.featured-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: fade-in 1.2s ease-in-out;
}

.featured-card h3 {
  margin-top: 0;
  font-size: 1.5rem;
}

/* Recent Posts */
.recent-posts {
  margin-bottom: 40px;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.post-card.enhanced {
  position: relative;
  background: linear-gradient(135deg, #43cea2, #185a9d);
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  color: #fff;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  animation: slide-in 1s ease-in-out;
}

.post-card.enhanced:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.post-tag {
  background: #87ab05;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  color: #fff;
  animation: pop 1.2s infinite;
}

.post-excerpt {
  margin: 15px 0;
  font-size: 1rem;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #ccefff;
}

.meta-item {
  display: flex;
  align-items: center;
}

.icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon.sender {
  background-image: url('/icons/user.svg');
  /* Placeholder SVG URL */
}

.icon.date {
  background-image: url('/icons/calendar.svg');
}

.icon.likes {
  background-image: url('/icons/heart.svg');
}

.read-more {
  display: inline-block;
  margin-top: 15px;
  background: #1cad0c;
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s ease;
}

.read-more:hover {
  background: #0f8b06;
}

/* Popular Topics */
.popular-topics {
  margin-bottom: 40px;
}

.topics-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.topic {
  background: #08b8a4;
  color: white;
  padding: 10px 15px;
  border-radius: 50px;
  font-size: 0.9rem;
  animation: pulse 1.5s infinite ease-in-out;
}

/* Footer */
footer {
  text-align: center;
  margin-top: 50px;
  font-size: 0.85rem;
  color: #555;
  animation: fade-in 1.2s ease-in-out;
}

footer nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #007BFF;
  font-weight: 600;
}

footer nav a:hover {
  color: #0056b3;
}

.sticky-button-container {
  position: fixed;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  animation: slideDown 0.8s ease-out;
}

.floating-button-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
}


/* Super Funky Button */
.super-funky-button {
  font-family: 'Montserrat', sans-serif;
  font-size: 22px;
  font-weight: 700;
  padding: 18px 36px;
  border: none;
  border-radius: 50px;
  background: linear-gradient(135deg, #42e695, #3bb2b8, #ff512f, #dd2476);
  background-size: 300% 300%;
  color: white;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5);
  position: relative;
  overflow: hidden;
  animation: pulse 2s infinite, gradientShift 6s infinite;
  transition: transform 0.2s ease, box-shadow 0.4s ease;
}

/* Ripple Effect on Hover */
.super-funky-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  height: 300%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3), transparent);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.6s ease-out;
  opacity: 0.8;
  pointer-events: none;
}

.super-funky-button:hover::before {
  transform: translate(-50%, -50%) scale(1);
}

.super-funky-button:hover {
  transform: translateY(-8px) scale(1.1);
  box-shadow: 0 15px 45px rgba(59, 178, 184, 0.7);
}

/* Bounce Effect on Hover */
.super-funky-button:active {
  transform: scale(0.95);
  box-shadow: 0 8px 20px rgba(42, 230, 149, 0.5);
}

/* Pulse Animation */
@keyframes pulse {

  0%,
  100% {
    box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5), 0 0 0 0 rgba(42, 230, 149, 0.3);
  }

  50% {
    box-shadow: 0 15px 45px rgba(42, 230, 149, 0.7), 0 0 20px 10px rgba(42, 230, 149, 0);
  }
}

/* Gradient Shift Animation */
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

/* Slide Down on Load */
@keyframes slideDown {
  from {
    transform: translateX(-50%) translateY(-100%);
  }

  to {
    transform: translateX(-50%) translateY(0);
  }
}

/* Mobile Adjustments */
@media (max-width: 600px) {
  .sticky-button-container {
    top: 10px;
  }

  .super-funky-button {
    font-size: 18px;
    padding: 14px 28px;
  }
}

/* Animations */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pop {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

/* @keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
} */

.tag-container {
  position: relative;
  display: flex;
  width: 100%;
  height: 500px;
}

.tag-container::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 0;
  background: linear-gradient(135deg, #667eea 30%, #764ba2);
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: .3s 0.01ms ease-in;
}

.tag-container:hover {
  width: 100%;
}

.tag-container:hover::before {
  height: 200px;
  transition: .5s .6s ease-in;
}

.tag {
  position: absolute;
  width: 235px;
  aspect-ratio: 3/4;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.6);
  font-size: 2.5em;
  font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
  font-weight: 900;
  line-height: 300px;
  text-align: center;
  cursor: pointer;
  color: rgba(0, 0, 0, 0.8);
  margin: 0 5px;
  left: 50%;
  top: 50%;
  transform: rotate(calc(var(--i) * 5deg)) translate(-50%, -50%);
  transform-origin: center;
  transition: .5s calc(var(--i) * 0.3s) ease;
  z-index: 0;
}

.tag:nth-child(even) {
  transform: rotate(calc(var(--i) * -5deg)) translate(-50%, -50%);
}

.tag-container:hover {
  display: flex;
  justify-content: center;
  align-items: center;
}

.tag-container:hover .tag {
  transform-origin: center center;
  transform: rotate(calc(var(--i) * 0deg)) translate(-349%, -50%) translateX(calc(var(--i) * 235px));
  transition-delay: calc(var(--i) * 0s);
  font-size: 3em;
  line-height: 300px;
  scale: 1.1;
  backdrop-filter: blur(12px);
  -webkit-text-stroke: 1px rgba(0, 0, 0, 0.5);
  color: black;
  background-color: #7f86f1;
  -webkit-box-reflect: below 4px linear-gradient(to bottom, transparent 80%, rgba(0, 0, 0, 0.5));
  z-index: 1;
}

.tag-container:hover .tag:not(:hover) {
  background: rgba(252, 254, 254, .3);
  font-size: 2em;
  line-height: 200px;
  scale: 1;
  border: 2px solid #b3b3b3;
  -webkit-text-stroke: 1px rgba(252, 254, 254, .8);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
  z-index: 0;
}
</style>
