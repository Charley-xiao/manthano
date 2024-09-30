<script setup lang="ts">
import axios from 'axios';
axios.defaults.withCredentials = true;
const $router = useRouter();

enum Themes {
  light = 'light',
  dark = 'dark'
}

const theme = ref<Themes>(Themes.light);
const isLoggedIn = ref<boolean>(false);
const username = ref<string>('');
const role = ref<string>('student');
const courses = ref<Array<{ id: number; title: string; description: string }>>([]);

const getCourses = async () => {
  try {
    const response = await axios.get('/api/my/course');
    courses.value = response.data;
  } catch (error: any) {
    console.error('An error occurred while fetching courses:', error);
  }
};

onMounted(() => {
  getLoginStatus();
  getCourses();
});

function toggleTheme() {
  theme.value = theme.value === Themes.light ? Themes.dark : Themes.light;
}

const getLoginStatus = async () => {
  try {
    const response = await axios.get('/api/');
    if (response.data.username) {
      isLoggedIn.value = true;
      username.value = response.data.username;
      role.value = response.data.role;
    } else {
      isLoggedIn.value = false;
      $router.push('/login');
    }
  } catch (error: any) {
    if (error.response && error.response.status === 401) {
      isLoggedIn.value = false;
      $router.push('/login');
    } else {
      console.error('An error occurred while fetching login status:', error);
    }
  }
}

onMounted(() => {
  getLoginStatus();
});
</script>

<template>
  <div :class="['app', theme]">
    <nav>
      <div class="logo"><img src="./assets/logo.jpg" alt="logo" style="width: 80px; height: 80px;" />Manthano</div>
      <div class="theme-toggle">
        <button @click="toggleTheme">Switch Theme</button>
      </div>
    </nav>

    <div class="course-grid">
      <div class="course-card" v-for="course in courses" :key="course.id">
        <!--<img :src="course.image" alt="course image" />-->
        <h2>{{ course.title }}</h2>
        <p>{{ course.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat&display=swap");

.app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  text-align: center;
  color: var(--text-color);
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: var(--nav-bg);
}

.logo {
  font-family: "Montserrat", sans-serif;
  font-size: 52px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
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