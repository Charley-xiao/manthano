<script lang="ts" setup>
import axios from 'axios';

const route = useRoute();
const tag = Array.isArray(route.query.tag) ? route.query.tag[0] : route.query.tag;
console.log(tag);

const posts = ref<Array<{ id: number; course_id: number; title: string; sender_name: string; content: string; likes: number; date_submitted: string; }>>([]);

async function getPosts() {
    await axios.get(`/api/post/tag/${tag}`)
        .then((response) => {
            console.log(response.data);
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
});
</script>

<template>
    <div>
        <h1>Tag: {{ tag }}</h1>
        <div v-for="post in posts" :key="post.id">
            <h2 @click="$router.push({ path: `/community/post/${post.id}` })">
                {{ post.title }}
            </h2>
            <p>{{ post.sender_name }} - {{ post.date_submitted }}</p>
            <p>{{ post.content }}</p>
            <p>{{ post.likes }} likes</p>
        </div>
    </div>
</template>

<style scoped></style>