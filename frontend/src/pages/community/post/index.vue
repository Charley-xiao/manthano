<script setup lang="ts">
const post = ref({
    title: 'Post Title',
    author: 'Post Author',
    content: 'Post content goes here.'
});
</script>

<template>
    <div id="post-page" class="post-page-container">
        <header class="post-header">
            <h1>{{ post.title }}</h1>
            <p>by {{ post.author }}</p>
        </header>

        <div class="post-content">
            <p>{{ post.content }}</p>
        </div>
    </div>
</template>

<style scoped></style>