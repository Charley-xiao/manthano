<script setup lang="ts">

const recentPosts = ref([
    { id: 1, title: 'Tips for Effective Study Groups', author: 'Alice' },
    { id: 2, title: 'Best Resources for Math Help', author: 'Bob' },
    { id: 3, title: 'How to Prepare for Exams', author: 'Charlie' },
    { id: 4, title: 'Study Techniques for Science Classes', author: 'David' },
    { id: 5, title: 'Literature Class Discussions', author: 'Eve' },
    { id: 6, title: 'Time Management Tips for Students', author: 'Frank' },
    { id: 7, title: 'Effective Note-Taking Strategies', author: 'Grace' },
    { id: 8, title: 'Study Techniques for Different Learning Styles', author: 'Helen' },
    { id: 9, title: 'How to Stay Motivated in School', author: 'Ivy' },
    { id: 10, title: 'Best Study Spots on Campus', author: 'Jack' },
    { id: 11, title: 'How to Balance School and Work', author: 'Kevin' },
    { id: 12, title: 'Study Techniques for Visual Learners', author: 'Lily' },
    { id: 13, title: 'How to Manage Stress During Finals', author: 'Mike' },
    { id: 14, title: 'Study Techniques for Auditory Learners', author: 'Nancy' },
]);

const popularTopics = ref(['Mathematics', 'Science', 'Literature', 'Study Techniques']);

const colors = [
    "linear-gradient(135deg, #667eea, #764ba2)",
    "linear-gradient(135deg, #ff6a00, #ee0979)",
    "linear-gradient(135deg, #42e695, #3bb2b8)",
    "linear-gradient(135deg, #ff512f, #dd2476)",
    "linear-gradient(135deg, #24c6dc, #514a9d)"
];

onMounted(() => {
    const cardHeaders: NodeListOf<HTMLElement> = document.querySelectorAll('div.card-header');

    cardHeaders.forEach(cardHeader => {
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        cardHeader.style.background = randomColor;
    });

    console.log(cardHeaders);
});

</script>

<template>
    <div id="main-page" class="main-page-container">
        <header class="main-header">
            <h1>Class & Study Tips Forum</h1>
            <!-- <nav>
                <router-link to="/">Home</router-link>
                <router-link to="/posts">Posts</router-link>
                <router-link to="/about">About</router-link>
                <router-link to="/contact">Contact</router-link>
            </nav> -->
        </header>

        <main class="main-content">
            <section class="welcome-section">
                <h2>Welcome to the Forum!</h2>
                <p>Join discussions about classes and share your study tips.</p>
            </section>

            <section class="recent-discussions">
                <h2>Recent Discussions</h2>
                <div v-if="recentPosts.length === 0">No recent discussions.</div>
                <div class="post-card">
                    <div class="card" v-for="post in recentPosts" :key="post.id">
                        <div class="card-header">
                            <router-link to="/community/post">{{ post.title }}</router-link>
                        </div>
                        <div class="card-body">
                            <p>by {{ post.author }}</p>
                        </div>
                    </div>
                </div>
            </section>

            <section class="write-post">
                <h2>
                    <router-link to="/community/write">Write Your Own Post</router-link>
                </h2>
            </section>

            <section class="popular-topics">
                <h2>Popular Topics</h2>
                <ul>
                    <li v-for="topic in popularTopics" :key="topic">{{ topic }}</li>
                </ul>
            </section>

            <section class="study-tips">
                <h2>Study Tips</h2>
                <ul>
                    <li>Stay organized with a planner 📅</li>
                    <li>Use active recall techniques 🧠</li>
                    <li>Take regular breaks for better focus ⏳</li>
                </ul>
            </section>
        </main>

        <footer class="main-footer">
            <p>&copy; 2024 Class Forum. All rights reserved.</p>
        </footer>
    </div>
</template>

<style scoped>
.main-page-container {
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding: 20px;
}

.main-header {
    text-align: center;
    margin-bottom: 20px;
}

.main-header nav a {
    margin: 0 10px;
    text-decoration: none;
    color: #007BFF;
}

.main-content {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
}

section {
    margin-bottom: 20px;
}

h2 {
    border-bottom: 2px solid #007BFF;
    padding-bottom: 10px;
}

.main-footer {
    text-align: center;
    margin-top: 20px;
    font-size: 0.9em;
}

.post-card {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr;
    grid-gap: 10px;
}

.post-card>div {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
    color: #fff;
    padding: 10px;
    height: 10.8px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

.card-header a {
    color: #fff;
    text-decoration: none;
    text-overflow: ellipsis;
    -ms-word-break: break-all;
    word-break: break-all;
    word-break: break-word;
    -webkit-hyphens: auto;
    -moz-hyphens: auto;
    -ms-hyphens: auto;
    hyphens: auto;
}

.card-body {
    padding: 10px;
}
</style>
