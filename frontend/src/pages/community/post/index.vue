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

const toHumanReadable = (timestamp: string) => {
    const date = new Date(timestamp);
    const dateLocale = date.toLocaleString();
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const isYesterday = date.toDateString() === new Date(now.setDate(now.getDate() - 1)).toDateString();

    if (isToday) {
        return 'Today at ' + date.toLocaleTimeString();
    } else if (isYesterday) {
        return 'Yesterday at ' + date.toLocaleTimeString();
    } else {
        return dateLocale;
    }
};

onMounted(async () => {
    await getComments();
});
</script>

<template>
    <div id="post-page" class="post-page-container">
        <div class="comments-section">
            <h1 class="page-title">Comments</h1>
            <div class="comments-list">
                <div v-for="comment in comments" :key="comment.floor" class="comment-card appeared">
                    <div class="comment-header">
                        <span class="commenter-name">{{ comment.commenter_name }}</span>
                        <span class="comment-floor">#{{ comment.floor }}</span>
                    </div>
                    <p class="comment-content">{{ comment.comment_content }}</p>
                    <small class="comment-date">{{ toHumanReadable(comment.date_submitted) }}</small>
                </div>
            </div>
            <div class="add-comment-section">
                <textarea 
                    v-model="newComment.comment_content" 
                    class="comment-input" 
                    placeholder="Add a comment"></textarea>
                <button @click="submitComment" class="submit-button">Submit</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Base Styling */
body {
    font-family: 'Arial', sans-serif;
    margin: 0;
    background-color: #f9f9f9;
    color: #333;
}

/* Container Styling */
.post-page-container {
    max-width: 800px;
    margin: 50px auto;
    padding: 20px;
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
}

/* Page Title */
.page-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 20px;
    text-align: center;
    color: #555;
}

/* Comments List */
.comments-list {
    margin-bottom: 30px;
}

.comment-card {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 15px;
    background: #f8f9fa;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease-in-out;
}

.comment-card:hover {
    transform: translateY(-5px);
}

.comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.commenter-name {
    font-weight: bold;
    color: #333;
}

.comment-floor {
    font-size: 12px;
    color: #888;
}

.comment-content {
    font-size: 16px;
    margin-bottom: 8px;
    color: #555;
}

.comment-date {
    font-size: 12px;
    color: #999;
}

/* Add Comment Section */
.add-comment-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 20px;
}

.comment-input {
    width: 100%;
    min-height: 80px;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    font-size: 16px;
    resize: none;
    outline: none;
    transition: border 0.3s ease;
}

.comment-input:focus {
    border-color: #667eea;
    box-shadow: 0 0 5px rgba(102, 126, 234, 0.5);
}

.submit-button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.3s ease;
}

.submit-button:hover {
    background: linear-gradient(135deg, #764ba2, #667eea);
}
</style>
