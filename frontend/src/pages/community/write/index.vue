<script setup lang="ts">
import axios from "axios";
import { ref } from "vue";

interface Post {
  id: number;
  title: string;
  course_id: number;
  sender_name: string;
  content: string;
  likes: number;
  tag: string;
}

const newPost = ref<Post>({
  id: 0,
  course_id: NaN,
  title: '',
  sender_name: '',
  content: '',
  likes: 0,
  tag: ''
});

async function createPost() {
  const post = {
    course_id: newPost.value.course_id,
    sender_name: localStorage.getItem('username') || 'Anonymous',
    title: newPost.value.title,
    content: newPost.value.content,
    tag: newPost.value.tag
  };

  try {
    await axios.post('/api/posts', post);
    alert('Post added successfully!');
    resetForm();
  } catch (error) {
    console.error('Failed to add post:', error);
    alert('Failed to add post. Please try again.');
  }
}

function resetForm() {
  newPost.value = {
    id: 0,
    course_id: 0,
    title: '',
    sender_name: '',
    content: '',
    likes: 0,
    tag: ''
  };
}
</script>

<template>
  <div id="forum" class="forum-container">
    <header class="forum-header">
      <h1>Class & Study Tips Forum</h1>
      <p>Share your insights and questions with peers.</p>
    </header>

    <main class="forum-main">
      <section class="post-creation">
        <h2>Create a Post</h2>
        <form @submit.prevent="createPost" class="post-form">
          <input v-model="newPost.title" placeholder="Post Title" required />
          <input v-model="newPost.course_id" placeholder="Course ID" type="number" required />
          <textarea v-model="newPost.content" placeholder="Share your tips or questions..." required></textarea>
          <input v-model="newPost.tag" placeholder="Tag (e.g., Math, Science)" required />
          <button type="submit" class="submit-button">Submit</button>
        </form>
      </section>
    </main>

    <footer class="forum-footer">
      <p>&copy; 2024 Class Forum. All rights reserved.</p>
    </footer>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

.forum-container {
  max-width: 700px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: fadeIn 1s ease-in-out;
}

.forum-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.forum-header h1 {
  font-size: 2rem;
  color: #34495e;
  margin: 0;
}

.forum-header p {
  font-size: 1rem;
  color: #7f8c8d;
}

.forum-main {
  padding: 20px;
}

.post-creation h2 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #2c3e50;
}

.post-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-form input,
.post-form textarea {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  transition: border-color 0.3s ease;
}

.post-form input:focus,
.post-form textarea:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 6px rgba(52, 152, 219, 0.3);
}

.post-form textarea {
  min-height: 120px;
  resize: none;
}

.submit-button {
  align-self: flex-end;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.3s ease;
}

.submit-button:hover {
  background: linear-gradient(135deg, #2980b9, #27ae60);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.submit-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.forum-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 0.85rem;
  color: #95a5a6;
  padding-top: 10px;
  border-top: 2px solid #f0f0f0;
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

@media (max-width: 600px) {
  .forum-container {
    padding: 15px;
  }

  .post-form {
    gap: 10px;
  }

  .submit-button {
    font-size: 0.9rem;
    padding: 10px 20px;
  }
}
</style>
