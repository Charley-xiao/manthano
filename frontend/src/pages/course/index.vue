<script lang="ts" setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';
axios.defaults.withCredentials = true;

const router = useRouter();

const courses = ref<Array<{ id: number; title: string; description: string; color?: string }>>([]);
const draggedItem = ref<{ id: number; index: number } | null>(null);
const currentUsername = ref('');
const role = ref('');

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
  try {
    const response = await axios.get('/api/my/course');
    courses.value = response.data;
    for (let i = 0; i < courses.value.length; i++) {
      courses.value[i].color = getCardBackground(i);
    }
    // fetch the first course and see if the user is a teacher
    if (courses.value.length > 0) {
      const response = await axios.get(`/api/courses/${courses.value[0].id}`);
      role.value = response.data.owner === currentUsername.value ? 'teacher' : 'student';
    }
  } catch (error: any) {
    console.error('An error occurred while fetching courses:', error);
  }
};

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

onMounted(() => {
  currentUsername.value = localStorage.getItem('username') || '';
  getCourses();
});
</script>

<template>
  <div v-if="role === 'teacher'" class="sticky-button-container">
    <button class="super-funky-button" @click="router.push('/course/add')">Add Course</button>
  </div>
  <div class="course-grid">
    <div
      class="course-card"
      v-for="(course, index) in courses"
      :key="course.id"
      :style="{ background: course.color }"
      draggable="true"
      @dragstart="handleDragStart(course, index)"
      @dragover="(event) => handleDragOver(event, index)"
      @dragend="handleDragEnd"
    >
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

.sticky-button-container {
  position: fixed;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  animation: slideDown 0.8s ease-out;
}

.floating-button-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
}

/* Super Funky Button */
.super-funky-button {
  font-family: 'Montserrat', sans-serif;
  font-size: 22px;
  font-weight: 700;
  padding: 18px 36px;
  border: none;
  border-radius: 50px;
  background: linear-gradient(135deg, #42e695, #3bb2b8, #ff512f, #dd2476);
  background-size: 300% 300%;
  color: white;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(42, 230, 149, 0.5);
  position: relative;
  overflow: hidden;
  animation: pulse 2s infinite, gradientShift 6s infinite;
  transition: transform 0.2s ease, box-shadow 0.4s ease;
}

/* Ripple Effect on Hover */
.super-funky-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 300%;
  height: 300%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3), transparent);
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.6s ease-out;
  opacity: 0.8;
  pointer-events: none;
}

.super-funky-button:hover::before {
  transform: translate(-50%, -50%) scale(1);
}

.super-funky-button:hover {
  transform: translateY(-8px) scale(1.1);
  box-shadow: 0 15px 45px rgba(59, 178, 184, 0.7);
}

/* Bounce Effect on Hover */
.super-funky-button:active {
  transform: scale(0.95);
  box-shadow: 0 8px 20px rgba(42, 230, 149, 0.5);
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

/* Mobile Adjustments */
@media (max-width: 600px) {
  .sticky-button-container {
    top: 10px;
  }
  .super-funky-button {
    font-size: 18px;
    padding: 14px 28px;
  }
}
</style>
