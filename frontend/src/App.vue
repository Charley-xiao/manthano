<script setup lang="ts">
const courses = ref([
  {
    id: 1,
    title: 'Introduction to Programming',
    description: 'Learn the basics of programming with this course.',
    image: 'https://via.placeholder.com/300',
  },
  {
    id: 2,
    title: 'Web Development Bootcamp',
    description: 'A comprehensive guide to web development.',
    image: 'https://via.placeholder.com/300',
  },
  {
    id: 3,
    title: 'UI/UX Design Fundamentals',
    description: 'Master the essentials of user experience and design.',
    image: 'https://via.placeholder.com/300',
  },
]);

enum Themes {
  light = 'light',
  dark = 'dark'
}

const theme = ref<Themes>(Themes.light);

function toggleTheme() {
  theme.value = theme.value === Themes.light ? Themes.dark : Themes.light;
  // get html data-theme and change it
}
</script>

<template>
  <div :class="['app', theme]">
    <nav>
      <div class="logo">CourseSite</div>
      <div>
        <button @click="$router.push('/RegistrationAndLogin')">
          Go to Registration and Login
        </button>
        <RouterView />
      </div>
      <div class="theme-toggle">
        <button @click="toggleTheme">Switch Theme</button>
      </div>
    </nav>

    <div class="course-grid">
      <div class="course-card" v-for="course in courses" :key="course.id">
        <img :src="course.image" alt="course image" />
        <h2>{{ course.title }}</h2>
        <p>{{ course.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Global Styles */
.app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: var(--nav-bg);
}

.logo {
  font-size: 24px;
  font-weight: bold;
}

.theme-toggle button {
  padding: 10px 20px;
  background-color: var(--button-bg);
  color: var(--button-text);
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.theme-toggle button:hover {
  background-color: var(--button-hover-bg);
}

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