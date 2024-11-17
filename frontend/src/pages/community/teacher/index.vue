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


interface Teacher {
  id: number;
  title: string;
  instructor: string;
  rating: number;
}

const posts = ref<Post[]>([
  {
    id: 1,
    course_id: 101,
    title: "Sample Post Title",
    sender_name: "A",
    content: "Sample content.",
    date_submitted: "2024-11-17",
    likes: 25,
    tag: "CS101"
  },{
    id: 2,
    course_id: 101,
    title: "Sample Post Title 2",
    sender_name: "B",
    content: "Sample content 2.",
    date_submitted: "2024-11-17",
    likes: 25,
    tag: "CS101"
  }
]);

const teacher = ref<Teacher>(
  {
    id: 1,
    title: "CS101",
    instructor: "A",
    rating: 1.4
  })

async function fetchPosts() {
  const response = await axios.get('/api/posts');
  console.log(response.data.posts);
  posts.value = response.data.posts;
}

onMounted(() => {
  fetchPosts();
});

const filledStars = ref(0);

function rate(stars: number) {
  filledStars.value = stars;
}

async function submitRating() {
  console.log('Rating submitted:', filledStars.value);
}


</script>

<template>
  <div id="main-page" class="main-container">
    <header class="header">
      <h1>{{ teacher.title + " post"}} </h1>
      <p>{{ teacher.instructor }}</p>
      <div class="teacher-rating">Rating: {{ teacher.rating }} ★</div>
    </header>

    <main>
      <section class="recent-posts">
        <h2>Teacher post</h2>
        <div class="posts-grid">
          <div class="post-card enhanced" v-for="post in posts" :key="post.id">
            <div class="post-header">
              <h3>{{ post.title }}</h3>
              <span class="post-tag">{{ post.tag }}</span>
            </div>
            <p class="post-excerpt">{{ post.content.substring(0, 80) }}...</p>
            
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
      
      <div class="star_container">
        <div class="stars">
          <h2>Give a rating</h2>
          <div>
            <span v-for="n in 5" :key="n" @click="rate(n)" :class="{'star filled': n <= filledStars, 'star empty': n > filledStars}">&#9733;</span>
          </div>
        </div>
        <div class="button">
          <button @click="submitRating" class="subbmit">Submit</button>
        </div>
      </div>
      
    </main>

  </div>
</template>

<style scoped>

.container {
  display: flex;
  justify-content: center;
  align-items: center;
}


.stars {
  margin-right: 10px;
}

.star {
  cursor: pointer;
  font-size: 50px;
}

.button {
  margin-left: 65px;
}

.filled {
  color: gold;
}

.empty {
  color: #ccc;
}

.subbmit {
  display: inline-block;
  margin-top: 15px;
  background: #1cad0c;
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: bold;
  transition: background 0.3s ease;
  border: none; 
}

.subbmit:hover {
  background: #0f8b06;
}

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
  background-image: url('/icons/user.svg'); /* Placeholder SVG URL */
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

.floating-button-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
}

.teacher-rating {
    margin-top: 10px;
    font-size: 1rem;
    color: #f39c12;
  }

/* Pulse Animation */
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5), 0 0 0 0 rgba(42, 230, 149, 0.3);
  }
  50% {
    box-shadow: 0 15px 45px rgba(42, 230, 149, 0.7), 0 0 20px 10px rgba(42, 230, 149, 0);
  }
}

/* Gradient Shift Animation */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
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
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

</style>
