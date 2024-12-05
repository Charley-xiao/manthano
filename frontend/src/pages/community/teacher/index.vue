<script setup lang="ts">
import axios from "axios";
import { ref, onMounted } from "vue";
import { useRoute } from 'vue-router';

const route = useRoute();
const router = useRouter();

const courses = ref<Array<{ id: number; title: string; description: string; color?: string }>>([]);
const draggedItem = ref<{ id: number; index: number } | null>(null);

interface Teacher {
  id: number;
  name: string;
  rating: number;
}


const teacher = ref<Teacher>(
  {
    id: 1,
    name: "Teacher Wang",
    rating: 1.4
  })

const colors = [
  "linear-gradient(135deg, #667eea, #764ba2)",
  "linear-gradient(135deg, #ff6a00, #ee0979)",
  "linear-gradient(135deg, #42e695, #3bb2b8)",
  "linear-gradient(135deg, #ff512f, #dd2476)",
  "linear-gradient(135deg, #24c6dc, #514a9d)"
];


const getCardBackground = (index: number) => {
  return colors[index % colors.length];
};


const getCourses = async () => {
  const params = new URLSearchParams();
  params.append('username', teacher.value.name);
  try {
    const response = await axios.get('/api/my/course', {params: params});
    courses.value = response.data;
    for (let i = 0; i < courses.value.length; i++) {
      courses.value[i].color = getCardBackground(i);
    }
  } catch (error: any) {
    console.error('An error occurred while fetching courses:', error);
  }
};

async function fetchTeacher() {
  const params = new URLSearchParams();
  params.append('id', route.params.id[0]);

  try {
    const response = await axios.get('/api/teacher/getname', {params: params});
    console.log(response.data);
    teacher.value = response.data[0];
    getCourses();
  } catch (error) {
      console.error('Failed to get name:', error);
    }
}


onMounted(() => {
  fetchTeacher();
});


const handleDragStart = (course: { id: number }, index: number) => {
  draggedItem.value = { id: course.id, index };
};

const handleDragOver = (event: DragEvent, index: number) => {
  event.preventDefault(); // Allow dropping
  const draggedOverIndex = draggedItem.value?.index;
  if (draggedOverIndex !== index) {
    const draggedCourse = courses.value[draggedOverIndex!];
    courses.value.splice(draggedOverIndex!, 1);
    courses.value.splice(index, 0, draggedCourse);
    draggedItem.value = { id: draggedCourse.id, index };
  }
};

const handleDragEnd = () => {
  draggedItem.value = null;
};

</script>

<template>
  <div id="main-page" class="main-container">
    <header class="header">
      <h1>{{ teacher.name + " courses"}} </h1>
      <div class="teacher-rating">Rating: {{ teacher.rating }} ★</div>
    </header>

    <main>
      <div class="course-grid">
        <div class="course-card" v-for="(course, index) in courses" :key="course.id" :style="{ background: course.color }"
          draggable="true" @dragstart="handleDragStart(course, index)" @dragover="(event) => handleDragOver(event, index)"
          @dragend="handleDragEnd">
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
      
    </main>

  </div>
</template>

<style scoped>


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
  transition: transform 0.4s ease, box-shadow 0.4s ease, opacity 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  z-index: 1;
  cursor: grab;
  opacity: 1;
}

.course-card.dragging {
  opacity: 0.5;
  cursor: grabbing;
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
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2), rgba(0, 0, 0, 0));
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

.container {
  display: flex;
  justify-content: center;
  align-items: center;
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
  background-image: url('/icons/user.svg'); /* Placeholder SVG URL */
}

.icon.date {
  background-image: url('/icons/calendar.svg');
}

.icon.likes {
  background-image: url('/icons/heart.svg');
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

.teacher-rating {
    margin-top: 10px;
    font-size: 1rem;
    color: #f39c12;
  }

/* Pulse Animation */
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5), 0 0 0 0 rgba(42, 230, 149, 0.3);
  }
  50% {
    box-shadow: 0 15px 45px rgba(42, 230, 149, 0.7), 0 0 20px 10px rgba(42, 230, 149, 0);
  }
}

/* Gradient Shift Animation */
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
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
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

</style>
