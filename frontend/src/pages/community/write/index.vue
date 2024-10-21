<template>
    <div id="forum" class="forum-container">
        <header class="forum-header">
            <h1>Class & Study Tips Forum</h1>
        </header>

        <main class="forum-main">
            <section class="post-creation">
                <h2>Create a Post</h2>
                <form @submit.prevent="createPost">
                    <input v-model="newPost.title" placeholder="Post Title" required />
                    <textarea v-model="newPost.content" placeholder="Share your tips or questions..."
                        required></textarea>
                    <button type="submit">Submit</button>
                </form>
            </section>

            <section class="post-list">
                <h2>Recent Posts</h2>
                <div v-if="posts.length === 0">No posts available.</div>
                <div v-for="post in posts" :key="post.id" class="post">
                    <h3>{{ post.title }}</h3>
                    <p>{{ post.content }}</p>
                    <footer>
                        <small>Posted by: {{ post.author }} on {{ post.date }}</small>
                    </footer>
                </div>
            </section>
        </main>

        <footer class="forum-footer">
            <p>&copy; 2024 Class Forum. All rights reserved.</p>
        </footer>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const newPost = ref({
    title: '',
    content: '',
});

const posts = ref([]);

function createPost() {
    const post = {
        id: posts.value.length + 1,
        title: newPost.value.title,
        content: newPost.value.content,
        author: 'User', // You can replace this with actual user info
        date: new Date().toLocaleString(),
    };
    posts.value.push(post);
    newPost.value.title = '';
    newPost.value.content = '';
}
</script>

<style scoped>
.forum-container {
    max-width: 800px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding: 20px;
}

.forum-header {
    text-align: center;
    margin-bottom: 20px;
}

.forum-header nav a {
    margin: 0 10px;
    text-decoration: none;
    color: #007BFF;
}

.forum-main {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
}

.post-creation input,
.post-creation textarea {
    width: 100%;
    margin: 10px 0;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.post-creation button {
    background-color: #007BFF;
    color: white;
    border: none;
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
}

.post {
    background: #fff;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.forum-footer {
    text-align: center;
    margin-top: 20px;
    font-size: 0.9em;
}
</style>
