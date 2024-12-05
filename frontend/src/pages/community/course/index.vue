<script setup lang="ts">
import axios from "axios";

const route = useRoute();
const router = useRouter();
const courseId = route.params.id[0];

interface Post {
  id: number;
  course_id: string;
  title: string;
  sender_name: string;
  content: string;
  timestamp: string;
  like: number;
  tag: string;
}

interface Rating {
  id: number;
  course_id: string;
  sender_name: string;
  star: number;
  difficulty: string;
  workload: string;
  grading: string;
  gain: string;
  comment: string;
  timestamp: string;
}

interface Course {
  id: number;
  title: string;
  instructor: string;
  rating: number;
}

const posts = ref<Post[]>([]);

const ratings = ref<Rating[]>([]);

const course = ref<Course>({
  id: 0,
  title: '',
  instructor: '',
  rating: 0
})

const newRating = ref<Rating>({
  id: 0,
  course_id: courseId,
  sender_name: '',
  star: 5,
  difficulty: 'Low',
  workload: 'Low',
  grading: 'Low',
  gain: 'Low',
  comment: '',
  timestamp: ''
});


async function fetchCourse() {
  try {
    const response = await axios.get(`/api/course/all`);
    course.value = response.data[parseInt(courseId) - 1];
    console.log('Teacher details:', response.data);

  } catch (error) {
    console.error('Failed to fetch course details:', error);
  }
};



async function submitRating() {

  const params = new URLSearchParams();
  params.append('sender_name', localStorage.getItem('username') || 'Anonymous');
  params.append('course_id', newRating.value.course_id);
  params.append('comment', newRating.value.comment);
  params.append('star', newRating.value.star.toString());
  params.append('difficulty', newRating.value.difficulty);
  params.append('workload', newRating.value.workload);
  params.append('grading', newRating.value.grading);
  params.append('gain', newRating.value.gain);

  try {
    await axios.post('/api/rating', params);
    alert('Rating added successfully!');
    newRating.value = {
      id: 0,
      course_id: courseId,
      sender_name: '',
      star: 5,
      difficulty: 'Low',
      workload: 'Low',
      grading: 'Low',
      gain: 'Low',
      comment: '',
      timestamp: ''
    }
    fetchRating();
  } catch (error) {
    alert(params);
    console.error('Failed to rate:', error);
    //alert('Failed to rate. Please try again.');
  }
}


async function fetchPosts() {
  const params = new URLSearchParams();
  params.append('course_id', courseId);

  try {
    const response = await axios.get('/api/course/post', { params: params });
    console.log('post detail:', response.data);
    posts.value = response.data.posts;
  } catch (error) {
    alert(params);
    console.error('Failed to get rate:', error);
  }
}


async function fetchRating() {
  const params = new URLSearchParams();
  params.append('course_id', courseId);

  try {
    const response = await axios.get('/api/rating', { params: params });
    console.log('rating detail:', response.data);
    response.data.forEach((rating: any) => {
      console.log(rating);
      ratings.value.push({
        id: rating.id,
        course_id: courseId,
        sender_name: rating.sender_name,
        star: rating.star,
        difficulty: rating.difficulty,
        workload: rating.workload,
        grading: rating.grading,
        gain: rating.gain,
        comment: rating.comment,
        timestamp: rating.timestamp
      });
    });
  } catch (error) {
    alert(params);
    console.error('Failed to get rate:', error);
  }
}
const isTeacher = ref(false);
onMounted(async () => {
  await fetchPosts();
  await fetchCourse();
  await fetchRating();
  isTeacher.value = localStorage.getItem('role') === 'teacher';
});

function rate(stars: number) {
  newRating.value.star = stars;
}

const sendRequestToJoinCourse = () => {
  const params = new URLSearchParams();
  params.append('course_id', courseId);
  params.append('username', localStorage.getItem('username') || '');
  try {
    axios.post('/api/joincourserequest', params);
    router.push('/cdetail/' + courseId);
  } catch (error) {
    console.error('Failed to send request:', error);
  }
};

</script>

<template>
  <div id="main-page" class="main-container">
    <header class="header">
      <h1>{{ course.title }} </h1>
      <p>{{ course.instructor }}</p>
      <div class="course-rating">Rating:
        <!-- <span v-for="n in course.rating" :key="n" class="ratestar filled">★</span> -->
        <span class="ratestar filled" v-for="n in Math.floor(course.rating)" :key="n">★</span>
        <span class="ratestar half" v-if="course.rating % 1 !== 0">★</span>
        <span class="ratestar empty" v-for="n in 5 - Math.ceil(course.rating)" :key="n">★</span>
        <span style="margin-left: 10px;">
          {{ course.rating.toFixed(1) }} ({{ ratings.length }} ratings)
        </span>
      </div>
      <div class="button" v-if="!isTeacher">
        <button @click="sendRequestToJoinCourse" class="subbmit">Join Course</button>
      </div>
    </header>

    <main>
      <section class="recent-posts">

        <h2>Rating post</h2>
        <div class="posts-grid">
          <div class="post-card enhanced" id="rating-post" v-for="post in ratings" :key="post.id">
            <div class="post-header">
              <div>
                <span v-for="n in 5" :key="n"
                  :class="{ 'ratestar filled': n <= post.star, 'ratestar empty': n > post.star }">&#9733;</span>
              </div>
            </div>
            <p class="post-excerpt">{{ post.comment.substring(0, 80) }}</p>


            <div class="post-meta">
              <div class="meta-item">
                <i class="icon difficulty"></i>
                <span>Difficulty: {{ post.difficulty }}</span>
              </div>
              <div class="meta-item">
                <i class="icon workload"></i>
                <span>Workload: {{ post.workload }}</span>
              </div>
            </div>

            <div class="post-meta">
              <div class="meta-item">
                <i class="icon gain"></i>
                <span>Gain: {{ post.gain }}</span>
              </div>
              <div class="meta-item">
                <i class="icon grading"></i>
                <span>Grading: {{ post.grading }}</span>
              </div>
            </div>

            <div class="post-meta">
              <div class="meta-item">
                <i class="icon sender"></i>
                <span>{{ post.sender_name }}</span>
              </div>
              <div class="meta-item">
                <i class="icon date"></i>
                <span>{{ new Date(post.timestamp).toLocaleDateString() }}</span>
              </div>
            </div>

          </div>
        </div>

        <h2>Course post</h2>
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
                <span>{{ new Date(post.timestamp).toLocaleDateString() }}</span>
              </div>
            </div>

            <router-link :to="'/community/post/' + post.id" class="read-more">Read More</router-link>
          </div>
        </div>
      </section>

      <div class="star_container">
        <h2>Give a rating</h2>
        <div class="stars">
          <div>
            <span v-for="n in 5" :key="n" @click="rate(n)"
              :class="{ 'star filled': n <= newRating.star, 'star empty': n > newRating.star }">&#9733;</span>
          </div>
        </div>
        <div class="rating_optations">
          <label for="difficulty">Difficulty:&nbsp;</label>
          <select id="difficulty" v-model="newRating.difficulty" class="input3d-flip">
            <option value="Very low">Very low</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="Very high">Very high</option>
            <option value="High">High</option>
          </select>
          <label for="workload">Workload:</label>
          <select id="workload" v-model="newRating.workload" class="input3d-flip">
            <option value="Very low">Very low</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="Very high">Very high</option>
            <option value="High">High</option>
          </select>
          <label for="grading">Grading:&nbsp;&nbsp;</label>
          <select id="grading" v-model="newRating.grading" class="input3d-flip">
            <option value="Very low">Very low</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="Very high">Very high</option>
            <option value="High">High</option>
          </select>
          <label for="gain">Gain:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</label>
          <select id="gain" v-model="newRating.gain" class="input3d-flip">
            <option value="Very low">Very low</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="Very high">Very high</option>
            <option value="High">High</option>
          </select>
        </div>
        <textarea v-model="newRating.comment" placeholder="Share your opinion on rating..." required></textarea>
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

.rating_optations>* {
  padding-left: 20px;
}

.input3d-flip {
  width: 180px;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  transition: transform 0.4s ease-in-out, box-shadow 0.3s ease;
}


.stars {
  display: flex;
  justify-content: center;
}

.star {
  margin-right: 10px;
  cursor: pointer;
  font-size: 50px;
}

.ratestar {
  margin-right: 10px;
  cursor: pointer;
  font-size: 20px;
}

.button {
  display: flex;
  justify-content: center;
}

.filled {
  color: gold;
}

.half {
  background: linear-gradient(90deg, gold 50%, transparent 50%);
  -webkit-background-clip: text;
  color: transparent;
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
  background-image: url('/icons/user.svg');
  /* Placeholder SVG URL */
}

.icon.date {
  background-image: url('/icons/calendar.svg');
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


.star_container {
  width: 600px;
}

.star_container textarea {
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  border: 1px solid #bdc3c7;
  border-radius: 8px;
  transition: border-color 0.3s ease;
}

.star_container input:focus,
.star_container textarea:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 6px rgba(52, 152, 219, 0.3);
}

.course-rating {
  margin-top: 10px;
  font-size: 1rem;
  /* color: #f39c12; */
}

/* Pulse Animation */
@keyframes pulse {

  0%,
  100% {
    box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5), 0 0 0 0 rgba(42, 230, 149, 0.3);
  }

  50% {
    box-shadow: 0 15px 45px rgba(42, 230, 149, 0.7), 0 0 20px 10px rgba(42, 230, 149, 0);
  }
}

/* Gradient Shift Animation */
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
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

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}
</style>
