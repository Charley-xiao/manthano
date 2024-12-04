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
        isEditing?: boolean;
        isCompleted?: boolean;
        published?: boolean;
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
            content: 'https://www.bilibili.com/video/BV1Wc1dYSEAG/?spm_id_from=333.1007.tianma.3-4-10.click',
            courseware: []
        },
        {
            id: '3',
            title: 'Loops and Conditionals',
            type: 'teaching',
            content: 'https://youtu.be/9wnja3h70DM?si=_NllYIa8wnuHI6MM',
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
        const params = new URLSearchParams();
        params.append('title', newChapterDetails.title);
        params.append('type', newChapterDetails.type);
        params.append('content', newChapterDetails.content);
        await axios.post(`/api/courses/${courseId}`, params);
        // alert('Chapter added successfully!');
    } catch (error) {
        console.error('Failed to add chapter:', error);
    }
};

// Edit a chapter
const saveChapterTitle = async (chapter: { id: string; title: string }) => {
    const chapterToUpdate = courseDetails.value.chapters.find(ch => ch.id === chapter.id);
    if (chapterToUpdate) {
        chapterToUpdate.title = chapter.title;
        chapterToUpdate.isEditing = false;

        try {
            await axios.put(`/api/courses/${courseId}`, chapterToUpdate);
            alert('Chapter title updated successfully!');
        } catch (error) {
            console.error('Failed to update chapter title:', error);
        }
    }
};

// Delete a chapter
const deleteChapter = async (chapterId: string) => {
    courseDetails.value.chapters = courseDetails.value.chapters.filter(ch => ch.id !== chapterId);

    try {
        const params = new URLSearchParams();
        params.append('chapter_id', chapterId);
        await axios.delete(`/api/courses/${courseId}`, { params });
        // alert('Chapter deleted successfully!');
    } catch (error) {
        console.error('Failed to delete chapter:', error);
    }
};

/*const addCourseware = async (chapterId: string, courseware: { name: string; file: File }) => {
    const chapter = courseDetails.value.chapters.find(ch => ch.id === chapterId);
    if (chapter) {
        try {
            const formData = new FormData();
            formData.append('chapterId', chapterId);
            formData.append('name', courseware.name);
            formData.append('file', courseware.file); // Attach the selected file

            const response = await axios.post(`/api/courseware`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            // Assuming the response contains the file's public link
            const uploadedCourseware = {
                name: response.data.name || courseware.name,
                link: response.data.link, // URL of the uploaded courseware
            };

            chapter.courseware.push(uploadedCourseware);
            alert('Courseware uploaded and added successfully!');
        } catch (error) {
            console.error('Failed to upload courseware:', error);
            alert('Failed to upload courseware.');
        }
    } else {
        alert('Chapter not found.');
    }
};*/


const fetchCourseDetails = async () => {
    try {
        const response = await axios.get(`/api/courses/${courseId}`);
        courseDetails.value = response.data;
        console.log('Course details:', courseDetails.value);

        isOwnerOrAdmin.value = (response.data.owner === currentUsername.value) || response.data.isAdmin;
    } catch (error) {
        console.error('Failed to fetch course details:', error);
    }
};

const fetchCourseComments = async () => {
    try {
        const response = await axios.get(`/api/courses/${courseId}/comments?course_id=${courseId}`);
        comments.value = response.data;
    } catch (error) {
        console.error('Failed to fetch course comments:', error);
    }
};


const commentContent = ref('');

const postCourseComment = async () => {
    if (!commentContent.value.trim()) {
        console.log('Comment cannot be empty');
        alert('Comment cannot be empty');
        return;
    }

    const newComment = {
        user: currentUsername.value,
        content: commentContent.value,
        timestamp: new Date().toISOString(),
        course_id: courseId
    };

    const params = new URLSearchParams();
    params.append('user', currentUsername.value);
    params.append('content', commentContent.value);
    params.append('timestamp', new Date().toISOString());
    params.append('course_id', courseId as string);

    try {
        await axios.post(`/api/courses/${courseId}/comments`, params);
        comments.value.push(newComment);
        commentContent.value = '';
    } catch (error) {
        console.error('Failed to post comment:', error);
    }
};

const progress = ref(0);

const getProgress = async () => {
    try {
        const params = new URLSearchParams();
        params.append('course_id', courseId.toString());
        const response = await axios.get(`/api/course/progress`, { params });
        console.log(response.data)
        const completedChapters = response.data.chapters;
        const totalChapters = courseDetails.value.chapters.length;
        const completedChaptersCount = completedChapters.length;
        progress.value = (completedChaptersCount / totalChapters) * 100;
        courseDetails.value.chapters.forEach(chapter => {
            chapter.isCompleted = completedChapters.includes(chapter.id);
        });
    } catch (error) {
        console.error('Failed to fetch course progress:', error);
    }
};

const isStudentSectionOpen = ref(false);
const newStudent = ref('');

const toggleStudentSection = () => {
    isStudentSectionOpen.value = !isStudentSectionOpen.value;
};

const addStudent = async (username: string) => {
    if (!username.trim()) {
        alert('Student username cannot be empty');
        return;
    }

    courseDetails.value.students.push(username);
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('course_id', courseId as string);
    params.append('student', username);

    try {
        await axios.post(`/api/courses/${courseId}/students`, params);
        // alert('Student added successfully!');
        // newStudent.value = '';
    } catch (error) {
        console.error('Failed to add student:', error);
    }
};

const removeStudent = async (student: string) => {
    courseDetails.value.students = courseDetails.value.students.filter(s => s !== student);

    const params = new URLSearchParams();
    params.append('student', student);

    try {
        await axios.delete(`/api/courses/${courseId}/students`, { params });
        // alert('Student removed successfully!');
    } catch (error) {
        console.error('Failed to remove student:', error);
    }
};

const currentUsername = ref('Alice');

onMounted(() => {
    currentUsername.value = localStorage.getItem('username') || '';
    fetchCourseDetails();
    fetchCourseComments();
    getProgress();
    document.addEventListener("visibilitychange", handleVisibilityChange);
});

onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    clearInterval(videoInterval!);
    clearInterval(idleInterval!);
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

const playingVideoNumber = ref(-1);
const isVideoModalOpen = ref(false);  // Control the modal visibility
const selectedVideoUrl = ref<string | null>(null);
const videoStarted = ref(false);
const videoWatchedTime = ref(0);  // Track how much time has been watched
const idleTime = ref(0);  // Track how long the user has been idle
const videoDuration = ref(0); // Total video duration
let videoInterval: ReturnType<typeof setInterval> | null = null;  // For tracking video time
let idleInterval: ReturnType<typeof setInterval> | null = null;  // For tracking idle time

// Ensure the user cannot leave the page or switch tabs while watching
const handleVisibilityChange = () => {
    if (document.hidden && isVideoModalOpen.value) {
        alert("You have switched tabs! Please stay on the page to complete the video.");
    }
};

// Enforce minimum viewing time
const enforceMinimumViewingTime = () => {
    if (videoWatchedTime.value < videoDuration.value * 0.9) {  // Require 90% viewing
        alert("You must watch at least 90% of the video to close this.");
        return false;
    }
    return true;
};

// Track video time
const startTrackingVideoTime = () => {
    videoInterval = setInterval(() => {
        videoWatchedTime.value += 1;
        console.log(videoWatchedTime.value);
        if (videoWatchedTime.value >= videoDuration.value * 0.9) {
            alert("You have met the required viewing time!");
            clearInterval(videoInterval!);
        }
    }, 1000);
};

// Track idle time (if the video is paused or the user is idle)
const startTrackingIdleTime = () => {
    idleInterval = setInterval(() => {
        idleTime.value += 1;
        if (idleTime.value > 10) {  // If idle for more than 10 seconds
            alert("You have been idle for too long. Please continue watching.");
        }
    }, 1000);
};

// Handle video play event
const handleVideoPlay = () => {
    console.log('Video started!');
    videoStarted.value = true;
    idleTime.value = 0;  // Reset idle time
    startTrackingVideoTime();  // Start counting watched time
};

// Handle video pause event
const handleVideoPause = () => {
    idleTime.value = 0;  // Reset idle time when paused
    clearInterval(videoInterval!);  // Stop tracking watched time
    startTrackingIdleTime();  // Start counting idle time
};

// Prevent multiple videos playing simultaneously
const showVideo = (videoUrl: string) => {
    if (isVideoModalOpen.value) {
        alert("You cannot open another video while one is playing.");
        return;
    }
    selectedVideoUrl.value = videoUrl;
    isVideoModalOpen.value = true;
    videoWatchedTime.value = 0;  // Reset watched time
    videoStarted.value = false;  // Reset video started state
    videoDuration.value = 600; // Assume 600 seconds (10 mins), replace with actual duration if possible
};

// Close video modal
const closeVideoModal = async () => {
    if (!enforceMinimumViewingTime()) return;
    isVideoModalOpen.value = false;
    clearInterval(videoInterval!);  // Stop video tracking
    clearInterval(idleInterval!);  // Stop idle tracking
    // alert(`You watched ${videoWatchedTime.value} seconds of the video.`);
    // record progress: mark this chapter as completed
    try {
        const params = new URLSearchParams();
        params.append('chapter_id', playingVideoNumber.value.toString());
        await axios.post(`/api/course/progress`, params);
        console.log('Chapter progress recorded successfully!');
    } catch (error) {
        console.error('Failed to record chapter progress:', error);
    }
};

const selectedFile = ref<File | null>(null);
const selectedFileName = ref('');
const coursewareFileName = ref('');

const handleFileSelection = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        selectedFile.value = target.files[0];
        selectedFileName.value = target.files[0].name;
        coursewareFileName.value = target.files[0].name.split('.').slice(0, -1).join('.'); // Default name without extension
    }
};

const uploadCourseware = async (chapterId: string) => {
    if (!selectedFile.value) {
        alert('Please select a file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile.value);
    formData.append('name', coursewareFileName.value);
    formData.append('chapter_id', chapterId);

    try {
        /*const response = await axios.post(`/api/courseware`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });*/

        // const uploadedCourseware = {
        //     name: response.data.name,
        //     link: response.data.link // Assuming the server returns the file's accessible URL
        // };

        // await addCourseware(chapterId, uploadedCourseware);

        alert('Courseware uploaded successfully!');
        // Reset fields
        selectedFile.value = null;
        selectedFileName.value = '';
        coursewareFileName.value = '';
    } catch (error) {
        console.error('Failed to upload courseware:', error);
        alert('Failed to upload courseware.');
    }
};

const changeVisibility = async (chapterId: string) => {
    const chapter = courseDetails.value.chapters.find(ch => ch.id === chapterId);
    if (chapter) {
        chapter.published = !chapter.published;
        const params = new URLSearchParams();
        params.append('chapter_id', chapterId);
        params.append('published', chapter.published ? 'true' : 'false');
        try {
            await axios.put(`/api/courses/${courseId}`, params);
            // alert('Chapter visibility updated successfully!');
        } catch (error) {
            console.error('Failed to update chapter visibility:', error);
        }
    }
};

const searchQuery = ref('');

interface SearchResult {
    id: string;
    username: string;
}

const searchResults = ref<SearchResult[]>([]);

const searchStudents = async () => {
    if (!searchQuery.value.trim()) {
        alert('Search query cannot be empty');
        return;
    }

    try {
        const response = await axios.get('/api/users/search', {
            params: { query: searchQuery.value },
        });
        searchResults.value = response.data;
    } catch (error) {
        console.error('Failed to search students:', error);
    }
};

const uploadHomeworkProject = async (chapterId: string) => {
    if (!selectedFile.value) {
        alert('Please select a file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile.value);
    formData.append('name', coursewareFileName.value);
    formData.append('course_id', courseId as string);
    formData.append('chapter_id', chapterId);

    try {
        /*const response = await axios.post(`/api/hwpj`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });*/

        // const uploadedCourseware = {
        //     name: response.data.name,
        //     link: response.data.link // Assuming the server returns the file's accessible URL
        // };

        // await addCourseware(chapterId, uploadedCourseware);

        alert('Homework/project submitted successfully!');
        // Reset fields
        selectedFile.value = null;
        selectedFileName.value = '';
        coursewareFileName.value = '';
    } catch (error) {
        console.error('Failed to submit homework/project:', error);
        alert('Failed to submit homework/project.');
    }
};

const notificationContent = ref('');

const sendNotification = async () => {
    if (!notificationContent.value.trim()) {
        alert('Notification content cannot be empty');
        return;
    }

    try {
        const params = new URLSearchParams();
        params.append('body', notificationContent.value);
        params.append('course_id', courseId as string);
        await axios.post(`/api/courses/${courseId}/notifications`, params);
        alert('Notification sent successfully!');
        notificationContent.value = '';
    } catch (error) {
        console.error('Failed to send notification:', error);
        alert('Failed to send notification.');
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

            <h2>Progress</h2>
            <div class="progress">
                <div class="progress-bar" :style="{ width: progress + '%' }" :data-progress="progress"></div>
            </div>

            <div v-if="isOwnerOrAdmin" class="manage-chapters">
                <h2>Manage Chapters</h2>
                <form @submit.prevent="addChapter" class="chapter-form">
                    <input v-model="newChapter.title" placeholder="Chapter Title" class="form-input" required />
                    <select v-model="newChapter.type" class="form-select">
                        <option value="teaching">Teaching</option>
                        <option value="homework">Homework</option>
                        <option value="project">Project</option>
                    </select>
                    <input v-model="newChapter.content" placeholder="Content URL" class="form-input" required />
                    <button type="submit" class="btn primary">Add Chapter</button>
                </form>

                <h3>Existing Chapters</h3>
                <ul class="chapter-list">
                    <li v-for="chapter in courseDetails.chapters" :key="chapter.id" class="chapter-item">
                        <p class="chapter-title">{{ chapter.title }}</p>
                        <div class="chapter-actions">
                            <input v-if="chapter.isEditing" v-model="chapter.title" @blur="saveChapterTitle(chapter)"
                                class="form-input" />
                            <span v-else>{{ chapter.title }}</span>
                            <button @click="chapter.isEditing = !chapter.isEditing" class="btn edit">{{
                                chapter.isEditing ? 'Save' : 'Edit' }}</button>
                            <button @click="deleteChapter(chapter.id)" class="btn delete">Delete</button>
                            <button @click="changeVisibility(chapter.id)" class="btn primary">{{ chapter.published ?
                                'Unpublish' : 'Publish' }}</button>
                        </div>
                    </li>
                </ul>
            </div>

            <div v-if="isOwnerOrAdmin" class="manage-students">
                <h2 @click="toggleStudentSection" class="collapsible-header">
                    Manage Students
                    <span :class="{ 'arrow-up': isStudentSectionOpen, 'arrow-down': !isStudentSectionOpen }"></span>
                </h2>
                <div v-if="isStudentSectionOpen" class="collapsible-content">
                    <div class="search-student">
                        <input v-model="searchQuery" @keydown.enter="searchStudents"
                            placeholder="Search students by username" class="form-input search-input" />
                        <button @click="searchStudents" class="btn primary">Search</button>
                    </div>
                    <div v-if="searchResults.length" class="search-results">
                        <h3>Search Results:</h3>
                        <ul>
                            <li v-for="student in searchResults" :key="student.id" class="search-item">
                                <span>{{ student.username }}</span>
                                <button @click="addStudent(student.username)" class="btn primary">Add</button>
                            </li>
                        </ul>
                    </div>
                    <form @submit.prevent="addStudent(newStudent)" class="student-form">
                        <input v-model="newStudent" placeholder="Student Username" class="form-input" required />
                        <button type="submit" class="btn primary">Add Student</button>
                    </form>
                    <h3>Enrolled Students</h3>
                    <ul class="student-list">
                        <li v-for="student in courseDetails.students" :key="student" class="student-item">
                            <span>{{ student }}</span>
                            <button @click="removeStudent(student)" class="btn delete">Remove</button>
                        </li>
                    </ul>
                    <h3>Notification</h3>
                    <form @submit.prevent="sendNotification" class="notification-form">
                        <textarea v-model="notificationContent" placeholder="Enter notification message"
                            class="form-input" required></textarea>
                        <button type="submit" class="btn primary">Send Notification</button>
                    </form>

                </div>
            </div>


            <div class="chapter-list">
                <div v-for="chapter in filteredChapters(activeTab)" :key="chapter.id" class="chapter-card">
                    <h3>{{ chapter.title }}</h3>
                    <div v-if="chapter.isCompleted" class="chapter-completed">Completed</div>
                    <div v-else class="chapter-completed not-completed">Not Completed</div>
                    <!-- If the user clicks this button, the page pops up the video in the front -->
                    <div v-if="chapter.type === 'teaching'">
                        <button @click="showVideo(chapter.content)" class="btn primary">Play Video</button>
                    </div>
                    <div v-else>
                        <a :href="chapter.content" target="_blank">Open {{ chapter.type }} Material</a>
                    </div>

                    <div v-if="chapter.courseware.length" class="courseware-section">
                        <h4>Courseware</h4>
                        <ul>
                            <li v-for="(file, index) in chapter.courseware" :key="index">
                                <a :href="`/api/files/courseware/${chapter.id}/${file.name}`" target="_blank">{{
                                    file.name }}</a>
                            </li>
                        </ul>
                    </div>

                    <!-- Courseware Upload Section -->
                    <div v-if="isOwnerOrAdmin" class="courseware-upload">
                        <h4>Upload Courseware</h4>
                        <form @submit.prevent="uploadCourseware(chapter.id)" class="upload-form">
                            <div class="file-upload-wrapper">
                                <label for="file-upload" class="file-upload-label">
                                    <input type="file" id="file-upload" class="file-input" @change="handleFileSelection"
                                        required />
                                    <span class="upload-icon">📁</span>
                                    <span class="upload-text">
                                        {{ selectedFileName || 'Choose a file from your computer' }}
                                    </span>
                                </label>
                            </div>
                            <input v-model="coursewareFileName" placeholder="Enter a display name for the file"
                                class="form-input" />
                            <button type="submit" class="btn primary upload-button">Upload</button>
                        </form>
                    </div>

                    <!-- Homework and Project Upload Section (for students) -->
                    <div v-if="!isOwnerOrAdmin && chapter.type!=='teaching'" class="courseware-upload">
                        <h4>Submit {{ chapter.type }}</h4>
                        <form @submit.prevent="uploadHomeworkProject(chapter.id)" class="upload-form">
                            <div class="file-upload-wrapper">
                                <label for="file-upload" class="file-upload-label">
                                    <input type="file" id="file-upload" class="file-input" @change="handleFileSelection"
                                        required />
                                    <span class="upload-icon">📁</span>
                                    <span class="upload-text">
                                        {{ selectedFileName || 'Choose a file from your computer' }}
                                    </span>
                                </label>
                            </div>
                            <input v-model="coursewareFileName" placeholder="Enter a display name for the file"
                                class="form-input" />
                            <button type="submit" class="btn primary upload-button">Submit</button>
                        </form>
                    </div>

                    <!-- Homework and Project Upload Section (for instructors) -->
                    <div v-if="isOwnerOrAdmin && (chapter.type === 'homework' || chapter.type === 'project')"
                        class="courseware-upload">
                        <h4>View {{ chapter.type }} Submissions</h4>
                        <ul>
                            <li v-for="(file, index) in chapter.courseware" :key="index">
                                <a :href="`/api/files/hwpj/${chapter.id}/${file.name}`" target="_blank">{{ file.name
                                    }}</a>
                            </li>
                        </ul>
                    </div>

                </div>
            </div>

            <div v-if="isVideoModalOpen" class="video-modal">
                <div class="modal-content">
                    <button @click="closeVideoModal" class="close-btn">Close</button>
                    <iframe v-if="selectedVideoUrl" :src="selectedVideoUrl" frameborder="0" allowfullscreen
                        @play="handleVideoPlay" @pause="handleVideoPause">
                    </iframe>
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
            <form class="comment-form" @submit.prevent="postCourseComment">
                <textarea v-model="commentContent" placeholder="Your comment..."></textarea>
                <button type="submit">Submit</button>
            </form>
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


.progress {
    background-color: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
    height: 20px;
    margin-bottom: 20px;
}

.progress-bar {
    background: linear-gradient(90deg, #3498db, #2ecc71);
    height: 100%;
    transition: width 0.4s ease;
    position: relative;
}

.progress-bar::after {
    content: attr(data-progress) '%';
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: white;
    font-weight: bold;
}

.manage-students {
    background-color: var(--app-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
}

.collapsible-header {
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: var(--app-bg);
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease;
}

.collapsible-header:hover {
    background-color: #f0f0f0;
}

.arrow-up::after {
    content: '▲';
    margin-left: 10px;
}

.arrow-down::after {
    content: '▼';
    margin-left: 10px;
}

.collapsible-content {
    padding: 10px;
    background-color: var(--app-bg);
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin-top: 10px;
}

.student-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.student-form input {
    padding: 10px;
    border: 2px solid #ccc;
    border-radius: 5px;
    width: 100%;
    transition: border-color 0.3s;
}

.student-form input:focus {
    border-color: #3498db;
    outline: none;
}

.student-list {
    list-style-type: none;
    padding: 0;
}

.student-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
    transition: box-shadow 0.3s ease;
}

.student-item:hover {
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
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

.comment-form {
    margin-top: 20px;
    margin-right: 20px;
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

    .form-input,
    .form-select {
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 5px;
        width: 100%;
        transition: border-color 0.3s;
    }

    .form-input:focus,
    .form-select:focus {
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
}

.video-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    position: relative;
    width: 80%;
    max-width: 900px;
    background: white;
    padding: 20px;
    border-radius: 8px;
}

.modal-content iframe {
    width: 100%;
    height: 500px;
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 8px;
    background: red;
    color: white;
    border: none;
    cursor: pointer;
}

.file-upload-wrapper {
    position: relative;
    margin-bottom: 10px;
    border: 2px dashed #3498db;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    transition: background-color 0.3s ease, border-color 0.3s ease;
}

.file-upload-wrapper:hover {
    background-color: #f0f8ff;
    border-color: #2980b9;
}

.file-upload-label {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-weight: bold;
    color: #3498db;
}

.file-upload-label .upload-icon {
    font-size: 24px;
}

.file-upload-label .upload-text {
    font-size: 16px;
}

.file-input {
    display: none;
}

.upload-button {
    display: block;
    margin-top: 10px;
    background-color: #3498db;
    color: #fff;
    font-weight: bold;
    text-transform: uppercase;
}

.upload-button:hover {
    background-color: #2980b9;
}

.chapter-completed {
    padding: 5px 10px;
    border-radius: 5px;
    color: white;
    font-size: 14px;
    display: inline-block;
    background-color: #2ecc71;
    /* Default to green for completed */
    margin-bottom: 20px;

    &.not-completed {
        background-color: #e74c3c;
        /* Red for not completed */
    }
}

.search-student {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-input {
    padding: 10px;
    border: 2px solid #ccc;
    border-radius: 5px;
    width: 100%;
}

.search-results {
    margin-bottom: 20px;
}

.search-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-radius: 5px;
    background-color: #f9f9f9;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
}

.notification-form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 10px;
}

.notification-form .form-input {
    padding: 10px;
    border: 2px solid #ccc;
    border-radius: 5px;
    resize: vertical;
    min-height: 80px;
    transition: border-color 0.3s;
}

.notification-form .form-input:focus {
    border-color: #3498db;
    outline: none;
}
</style>
