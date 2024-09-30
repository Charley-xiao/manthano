<script setup lang="ts">
import axios from 'axios';
axios.defaults.withCredentials = true;
const router = useRouter();

enum Themes {
  light = 'light',
  dark = 'dark'
}

const theme = ref<Themes>(Themes.light);
const isLoggedIn = ref<boolean>(false);
const username = ref<string>('');
const role = ref<string>('student');

onMounted(() => {
  getLoginStatus();
});

function toggleTheme() {
  theme.value = theme.value === Themes.light ? Themes.dark : Themes.light;
}

const getLoginStatus = async () => {
  try {
    const response = await axios.get('/api/');
    console.log('Login status:', response.data);
    if (response.data.username) {
      isLoggedIn.value = true;
      username.value = response.data.username;
      role.value = response.data.role;
      router.push('/course');
    } else {
      isLoggedIn.value = false;
      console.log('User is not logged in');
      router.push('/login');
    }
  } catch (error: any) {
    if (error.response && error.response.status === 401) {
      isLoggedIn.value = false;
      router.push('/login');
    } else {
      console.error('An error occurred while fetching login status:', error);
    }
  }
}
</script>

<template>
  <div :class="['app', theme]">
    <nav>
      <div class="logo"><img src="./assets/logo.jpg" alt="logo" style="width: 80px; height: 80px;" />Manthano</div>
      <div class="theme-toggle">
        <button @click="toggleTheme">Switch Theme</button>
      </div>
    </nav>

    <!-- <div class="left-bar">
      <ul>
      <li><router-link to="/"><img src="./assets/icons/my-courses-icon.png" alt="My Courses Icon" /> My Courses</router-link></li>
      <li><router-link to="/explore"><img src="./assets/icons/explore-icon.png" alt="Explore Icon" /> Explore</router-link></li>
      <li><router-link to="/community"><img src="./assets/icons/community-icon.png" alt="Community Icon" /> Community</router-link></li>
      <li><router-link to="/support"><img src="./assets/icons/support-icon.png" alt="Support Icon" /> Support</router-link></li>
      </ul>
    </div> -->

    <router-view />
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

/* Left Bar */
.left-bar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 200px;
  background-color: var(--nav-bg);
  padding: 20px;
}

.left-bar ul {
  list-style: none;
  padding: 0;
}

.left-bar li {
  margin-bottom: 20px;
}

.left-bar a {
  color: var(--text-color);
  text-decoration: none;
}

.left-bar a:hover {
  text-decoration: underline;
}
</style>