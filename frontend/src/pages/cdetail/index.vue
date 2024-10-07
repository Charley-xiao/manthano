<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

const route = useRoute();
const courseId = route.params.id;

interface CourseDetails {
    id: string;
    title: string;
    description: string;
    owner: string;
    type: string;
    students: string[];
    chapters: {
        id: string;
        title: string;
        type: string;
        content: string;
        courseware: {
            name: string;
            link: string;
        }[];
    }[];
}

const courseDetails = ref<CourseDetails>({
    id: '1',
    title: 'CS101: Introduction to Computer Science',
    description: 'Learn the basics of computer science and programming.',
    owner: 'John Doe',
    type: 'open',
    students: ['Alice', 'Bob', 'Charlie'],
    chapters: [
        {
            id: '1',
            title: 'Introduction to Programming',
            type: 'teaching',
            content: 'https://www.youtube.com/embed/O-qqgRjfo3s?si=rfrP1zvgmmh7LFxL',
            courseware: []
        },
        {
            id: '2',
            title: 'Variables and Data Types',
            type: 'teaching',
            content: 'https://www.youtube.com/embed/6OvJz0iQpHk',
            courseware: []
        },
        {
            id: '3',
            title: 'Loops and Conditionals',
            type: 'teaching',
            content: 'https://www.youtube.com/embed/6OvJz0iQpHk',
            courseware: []
        },
        {
            id: '4',
            title: 'Homework 1',
            type: 'homework',
            content: 'https://www.example.com/homework1.pdf',
            courseware: [
                {
                    name: 'Homework 1',
                    link: 'https://www.example.com/homework1.pdf'
                }
            ]
        },
        {
            id: '5',
            title: 'Project 1',
            type: 'project',
            content: 'https://www.example.com/project1.pdf',
            courseware: [
                {
                    name: 'Project 1',
                    link: 'https://www.example.com/project1.pdf'
                }
            ]
        }
    ]
});

const isOwnerOrAdmin = ref(true);
const activeTab = ref('teaching');

interface Comment {
    user: string;
    content: string;
    timestamp: string;
}

const comments = ref<Comment[]>([
    {
        user: 'Alice',
        content: 'Great course! I learned a lot.',
        timestamp: '2024-09-30 10:00:00'
    },
    {
        user: 'Bob',
        content: 'Wow~',
        timestamp: '2024-10-01 12:34:22'
    }
]);

const newChapter = ref({
    title: '',
    type: 'teaching',
    content: '',
    courseware: []
});

// Add a new chapter
const addChapter = async () => {
    const newChapterDetails = {
        ...newChapter.value,
        id: Date.now().toString()
    };
    courseDetails.value.chapters.push(newChapterDetails);

    try {
        await axios.post(`/api/courses/${courseId}`, newChapterDetails);
        alert('Chapter added successfully!');
    } catch (error) {
        console.error('Failed to add chapter:', error);
    }
};

// Edit a chapter
const editChapter = async (chapterId: string, updatedDetails: any) => {
    const chapterIndex = courseDetails.value.chapters.findIndex(ch => ch.id === chapterId);
    if (chapterIndex !== -1) {
        courseDetails.value.chapters[chapterIndex] = { ...courseDetails.value.chapters[chapterIndex], ...updatedDetails };

        try {
            await axios.put(`/api/courses/${courseId}`, {
                id: chapterId,
                ...updatedDetails
            });
            alert('Chapter updated successfully!');
        } catch (error) {
            console.error('Failed to update chapter:', error);
        }
    }
};

// Delete a chapter
const deleteChapter = async (chapterId: string) => {
    courseDetails.value.chapters = courseDetails.value.chapters.filter(ch => ch.id !== chapterId);

    try {
        await axios.delete(`/api/courses/${courseId}`, { params: { id: chapterId } });
        alert('Chapter deleted successfully!');
    } catch (error) {
        console.error('Failed to delete chapter:', error);
    }
};

// Add courseware to a chapter
const addCourseware = async (chapterId: string, courseware: { name: string; link: string }) => {
    const chapter = courseDetails.value.chapters.find(ch => ch.id === chapterId);
    if (chapter) {
        chapter.courseware.push(courseware);

        try {
            await axios.post(`/api/courseware`, { chapterId, courseware });
            alert('Courseware added successfully!');
        } catch (error) {
            console.error('Failed to add courseware:', error);
        }
    }
};

const fetchCourseDetails = async () => {
    try {
        const response = await axios.get(`/api/courses/${courseId}`);
        courseDetails.value = response.data;

        isOwnerOrAdmin.value = (response.data.owner === currentUsername.value) || response.data.isAdmin;
    } catch (error) {
        console.error('Failed to fetch course details:', error);
    }
};

const fetchCourseComments = async () => {
    try {
        const response = await axios.get(`/api/courses/${courseId}/comments`);
        comments.value = response.data;
    } catch (error) {
        console.error('Failed to fetch course comments:', error);
    }
};


const commentContent = ref('');

const postCourseComment = async () => {
    if (!commentContent.value.trim()) {
        alert('Comment cannot be empty');
        return;
    }

    const newComment = {
        user: currentUsername.value,
        content: commentContent.value,
        timestamp: new Date().toISOString()
    };

    try {
        await axios.post(`/api/courses/${courseId}/comments`, newComment);
        comments.value.push(newComment);
        commentContent.value = '';
        alert('Comment posted successfully!');
    } catch (error) {
        console.error('Failed to post comment:', error);
    }
};


const currentUsername = ref('Alice');

onMounted(() => {
    currentUsername.value = localStorage.getItem('username') || '';
    // fetchCourseDetails();
});

const filteredChapters = (type: string) => {
    return courseDetails.value.chapters.filter(chapter => chapter.type === type);
};

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
</script>

<template>
    <div id="course-details" class="course-container fade-in">
        <div class="course-content">
            <div class="course-header">
                <h1>{{ courseDetails.title }}</h1>
                <p class="course-type" :class="courseDetails.type">{{ courseDetails.type }}</p>
                <p>{{ courseDetails.description }}</p>
                <p class="course-owner">Instructor: {{ courseDetails.owner }}</p>
            </div>

            <div class="tabs">
                <button :class="{ active: activeTab === 'teaching' }" @click="activeTab = 'teaching'">Teaching</button>
                <button :class="{ active: activeTab === 'homework' }" @click="activeTab = 'homework'">Homework</button>
                <button :class="{ active: activeTab === 'project' }" @click="activeTab = 'project'">Project</button>
            </div>

            <div v-if="isOwnerOrAdmin" class="manage-chapters">
                <h2>Manage Chapters</h2>
                <form @submit.prevent="addChapter" class="chapter-form">
                    <input v-model="newChapter.title" placeholder="Chapter Title" class="form-input" required/>
                    <select v-model="newChapter.type" class="form-select">
                        <option value="teaching">Teaching</option>
                        <option value="homework">Homework</option>
                        <option value="project">Project</option>
                    </select>
                    <input v-model="newChapter.content" placeholder="Content URL" class="form-input" required/>
                    <button type="submit" class="btn primary">Add Chapter</button>
                </form>

                <h3>Existing Chapters</h3>
                <ul class="chapter-list">
                    <li v-for="chapter in courseDetails.chapters" :key="chapter.id" class="chapter-item">
                        <p class="chapter-title">{{ chapter.title }}</p>
                        <div class="chapter-actions">
                            <button @click="editChapter(chapter.id, { title: 'Updated Title' })" class="btn edit">Edit</button>
                            <button @click="deleteChapter(chapter.id)" class="btn delete">Delete</button>
                        </div>
                    </li>
                </ul>
            </div>


            <div class="chapter-list">
                <div v-for="chapter in filteredChapters(activeTab)" :key="chapter.id" class="chapter-card">
                    <h3>{{ chapter.title }}</h3>
                    <iframe v-if="chapter.type === 'teaching'" :src="chapter.content" frameborder="0"></iframe>
                    <div v-else>
                        <a :href="chapter.content" target="_blank">Open {{ chapter.type }} Material</a>
                    </div>

                    <div v-if="chapter.courseware.length" class="courseware-section">
                        <h4>Courseware</h4>
                        <ul>
                            <li v-for="(file, index) in chapter.courseware" :key="index">
                                <a :href="file.link" target="_blank">{{ file.name }}</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <div class="course-comments">
            <h2>Comments</h2>
            <div class="comment-list">
                <div v-for="(comment, index) in comments" :key="index" class="comment">
                    <div class="comment-header">
                        <strong>{{ comment.user }}</strong>
                        <span class="timestamp">{{ toHumanReadable(comment.timestamp) }}</span>
                    </div>
                    <p class="comment-content">{{ comment.content }}</p>
                </div>
            </div>
            <div class="comment-form" @submit.prevent="postCourseComment">
                <textarea v-model="commentContent" placeholder="Your comment..."></textarea>
                <button type="submit">Submit</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.course-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    padding: 20px;
}


.course-header {
    background-color: var(--app-bg);
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.course-type {
    padding: 5px 10px;
    border-radius: 5px;
    color: var(--app-bg);
    font-size: 14px;
    display: inline-block;
}

.course-type.open {
    background-color: #2ecc71;
}

.course-type.ongoing {
    background-color: #f39c12;
}

.course-type.closed {
    background-color: #e74c3c;
}

.course-owner {
    font-size: 16px;
    margin-top: 10px;
}


.tabs {
    display: flex;
    margin-bottom: 20px;
}

.tabs button {
    flex: 1;
    padding: 10px;
    cursor: pointer;
    background-color: var(--app-bg);
    color: var(--text-color);
    border: none;
    outline: none;
    transition: background-color 0.3s ease;
}

.tabs button.active {
    background-color: #3498db;
    color: var(--app-bg);
}


.chapter-list {
    display: grid;
    gap: 20px;
}

.chapter-card {
    background-color: var(--app-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.chapter-card:hover {
    transform: scale(1.02);
}


.courseware-section {
    margin-top: 20px;
}

.courseware-section ul {
    list-style: none;
    padding: 0;
}

.courseware-section li {
    background-color: var(--app-bg);
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
}


.course-comments {
    background-color: var(--app-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.comment-list {
    max-height: 400px;
    overflow-y: auto;
    padding: 10px;
    background-color: var(--comment-bg);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.comment {
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 10px;
    background-color: var(--app-bg);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.3s ease;
}

.comment:hover {
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    font-size: 14px;
}

.comment-header strong {
    font-size: 16px;
    color: var(--text-color);
}

.comment-header .timestamp {
    font-size: 12px;
    color: #7f8c8d;
}

.comment-content {
    font-size: 15px;
    line-height: 1.5;
    color: var(--text-color);
}

.comment-form textarea {
    width: 100%;
    height: 80px;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
    resize: none;
}

.comment-form button {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.comment-form button {
    background-color: #2980b9;
}

.manage-chapters {
    background-color: var(--app-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.manage-chapters {
    

.chapter-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.form-input, .form-select {
    padding: 10px;
    border: 2px solid #ccc;
    border-radius: 5px;
    width: 100%;
    transition: border-color 0.3s;
}

.form-input:focus, .form-select:focus {
    border-color: #3498db;
    outline: none;
}

.chapter-list {
    list-style-type: none;
    padding: 0;
}

.chapter-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
    transition: box-shadow 0.3s ease;
}

.chapter-item:hover {
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.chapter-title {
    font-weight: 600;
    color: var(--text-color);
}

.chapter-actions {
    display: flex;
    gap: 10px;
}

.btn {
    padding: 8px 16px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s;
    border: none;
    font-weight: 600;
}

.btn.primary {
    background-color: #3498db;
    color: #fff;
}

.btn.edit {
    background-color: #f39c12;
    color: #fff;
}

.btn.delete {
    background-color: #e74c3c;
    color: #fff;
}

.btn:hover {
    transform: scale(1.05);
}

.btn:active {
    transform: scale(1);
}
}
</style>