<script setup lang="ts">
import axios from "axios";

const route = useRoute();
const postId = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id;
const newComment = ref<{ post_id?: string; commenter_name?: string; floor?: number; comment_content?: string }>({});

interface Comment {
    floor: number;
    commenter_name: string;
    comment_content: string;
    date_submitted: string;
}

const comments = ref<Comment[]>([]);

const submitComment = async () => {
    if (!newComment.value.comment_content?.trim()) {
        return;
    }
    newComment.value = {
        post_id: postId,
        floor: comments.value.length + 1,
        commenter_name: localStorage.getItem('username') || '',
        comment_content: newComment.value.comment_content
    };
    await axios.post(`/api/post/${postId}/comments`, newComment.value)
        .then((response) => {
            console.log(response.data);
            comments.value.push({
                floor: response.data.floor,
                commenter_name: response.data.commenter_name,
                comment_content: response.data.comment_content,
                date_submitted: response.data.date_submitted
            });
            newComment.value = {};
        })
        .catch((error) => {
            console.error('Failed to submit comment:', error);
        });

    await getComments();
};

async function getComments() {
    // clear comments before fetching
    document.querySelectorAll('.appeared').forEach((comment) => {
        comment.remove();
    });
    await axios.get(`/api/post/${postId}/comments`)
        .then((response) => {
            console.log(response.data.comments);
            response.data.comments.forEach((comment: any[]) => {
                console.log(comment);
                comments.value.push({
                    floor: comment[2],
                    commenter_name: comment[3],
                    comment_content: comment[4],
                    date_submitted: comment[5]
                });
            });
        })
        .catch((error) => {
            console.error('Failed to fetch post:', error);
        });
    console.log(comments.value);
}

onMounted(async () => {
    await getComments();
});
</script>

<template>
    <div id="post-page" class="post-page-container">
        <ul>
            <li v-for="comment in comments" :key="comment.floor" class="appeared">
                <p>{{ comment.commenter_name }}: {{ comment.comment_content }}</p>
                <small>{{ comment.date_submitted }}</small>
            </li>
            <li>
                <textarea v-model="newComment.comment_content" placeholder="Add a comment"></textarea>
                <button @click="submitComment">Submit</button>
            </li>
        </ul>
    </div>
</template>

<style scoped></style>