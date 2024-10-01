<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;

const router = useRouter();

const courses = ref<Array<{ id: number; title: string; description: string }>>([]);

const colors = [
    "linear-gradient(135deg, #667eea, #764ba2)", 
    "linear-gradient(135deg, #ff6a00, #ee0979)",
    "linear-gradient(135deg, #42e695, #3bb2b8)", 
    "linear-gradient(135deg, #ff512f, #dd2476)", 
    "linear-gradient(135deg, #24c6dc, #514a9d)"
]

const getCardBackground = (index: number) => {
    return colors[index % colors.length];
}

const getCourses = async () => {
  try {
    const response = await axios.get('/api/my/course');
    courses.value = response.data;
    console.log('Courses:', courses.value);
  } catch (error: any) {
    console.error('An error occurred while fetching courses:', error);
  }
};

onMounted(() => {
  getCourses();
});
</script>

<template>
    <div class="course-grid">
      <div class="course-card" 
           v-for="(course, index) in courses" 
           :key="course.id" 
           :style="{ background: getCardBackground(index) }">
        <!--<img :src="course.image" alt="course image" />-->
        <div class="card-content">
          <h2>{{ course.title }}</h2>
          <p>{{ course.description }}</p>
        </div>
        <div class="card-footer">
          <div class="course-link" @click="router.push(`/cdetail/${course.id}`)">
            View Course
          </div>
        </div>
      </div>
    </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap");

/* Course Grid */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  padding: 40px;
  background-color: var(--app-bg);
}

.course-card {
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.course-card:hover {
  transform: scale(1.08);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.course-card h2 {
  font-family: 'Montserrat', sans-serif;
  font-size: 24px;
  color: #fff;
  margin-bottom: 15px;
  position: relative;
  z-index: 1;
}

.course-card p {
  font-size: 16px;
  color: #f3f3f3;
  position: relative;
  z-index: 1;
}

.course-card .card-content {
  position: relative;
  z-index: 2;
}

.course-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.2), rgba(0,0,0,0));
  transition: transform 0.6s ease;
  transform: scale(0.5);
  z-index: 0;
}

.course-card:hover::before {
  transform: scale(1.5);
}

.course-link {
  font-size: 16px;
  padding: 10px 20px;
  color: black;
  background-color: #fff;
  border-radius: 20px;
  text-decoration: none;
  text-align: center;
  transition: background-color 0.3s ease;
  z-index: 3;
}

.course-link:hover {
  background-color: #ffdd57;
  color: #764ba2;
}

.card-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 600px) {
  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>
