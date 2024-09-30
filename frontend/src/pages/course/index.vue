<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;

const courses = ref<Array<{ id: number; title: string; description: string }>>([]);

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
      <div class="course-card" v-for="course in courses" :key="course.id">
        <!--<img :src="course.image" alt="course image" />-->
        <h2>{{ course.title }}</h2>
        <p>{{ course.description }}</p>
      </div>
    </div>
</template>

<style scoped>
/* Course Grid */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.course-card {
  background-color: var(--card-bg);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.course-card:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
}

.course-card img {
  width: 100%;
  border-radius: 10px;
  margin-bottom: 20px;
}

.course-card h2 {
  font-size: 18px;
  margin-bottom: 10px;
}

.course-card p {
  font-size: 14px;
}

@media (max-width: 600px) {
  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>