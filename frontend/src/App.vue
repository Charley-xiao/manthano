<script setup lang="ts">
import axios from 'axios';
import { isLoggedIn } from './store/index.d';
axios.defaults.withCredentials = true;

enum Themes {
  light = 'light',
  dark = 'dark'
}

const theme = ref<Themes>(Themes.light);
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
      // router.push('/course');
    } else {
      isLoggedIn.value = false;
      console.log('User is not logged in');
      // router.push('/login');
    }
  } catch (error: any) {
    if (error.response && error.response.status === 401) {
      isLoggedIn.value = false;
      // router.push('/login');
    } else {
      console.error('An error occurred while fetching login status:', error);
    }
  }
}
</script>

<template>
  <div :class="['app', theme]">
    <nav>
      <div class="logo">
        <img src="./assets/logo.jpg" alt="logo" />
        Manthano
      </div>

      <div class="top-bar">
        <div v-if="isLoggedIn">
          <router-link to="/course" class="nav-item">My Courses</router-link>
          <router-link to="/community" class="nav-item">Community</router-link>
        </div>
        <router-link to="/explore" class="nav-item">Explore</router-link>
        <router-link to="/support" class="nav-item">Support</router-link>
      </div>

      <div class="nav-links">
        <div v-if="isLoggedIn" class="user-info">
          <p>Welcome, {{ username }}!</p>
          <p v-if="role === 'student'">Student</p>
          <p v-else-if="role === 'teacher'">Teacher</p>
          <p v-else>Admin</p>
        </div>
        <div v-else class="auth-button">
          <router-link to="/login" class="auth-link" id="login">Login</router-link>
          <router-link to="/register" class="auth-link">Register</router-link>
        </div>
        <div v-if="isLoggedIn" class="auth-button" id="logout-button">
          <router-link to="/logout" class="auth-link">Logout</router-link>
        </div>
      </div>

      <div class="theme-toggle">
        <button @click="toggleTheme" class="theme-button">Switch Theme</button>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<style scoped lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap");

.app {
  font-family: 'Montserrat', sans-serif;
  color: var(--text-color);
  background: var(--app-bg);
  transition: background-color 0.5s ease, color 0.5s ease;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid var(--nav-border);
}

.logo {
  display: flex;
  align-items: flex-end;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

.logo img {
  width: 40px;
  height: 40px;
  margin-right: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
}

.nav-links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.user-info p {
  margin: 0 10px;
  color: #fff;
}

.auth-button {
  display: flex;
  justify-content: center;
  align-items: center;

  background: #1b09e5;
  border: medium solid #848de9;
  border-radius: 5px;
  cursor: pointer;
  margin: 0 15px;
  padding: 7px 15px;

  #login::after {
    content: "/";
    margin: 0 2px;
    color: #b2ccef;
    pointer-events: none;
  }

  .auth-link {
    margin: 0;
    font-size: 18px;
    color: #fff;
    text-decoration: none;
    transition: color 0.3s;
  }

  .auth-link:hover {
    color: #ffdd57;
  }
}

#logout-button {
  background-color: #d51010;
  border: medium solid #e87878;
}

.top-bar {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-left: auto;
  padding: 10px;
}

.nav-item {
  color: #fff;
  margin: 0 15px;
  font-size: 18px;
  text-decoration: none;
  position: relative;
}

.nav-item::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 2px;
  background-color: #ffdd57;
  bottom: -5px;
  left: 0;
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.nav-item:hover::after {
  transform: scaleX(1);
}

.theme-button {
  padding: 10px 20px;
  background: #ffdd57;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: background 0.3s;
}

.theme-button:hover {
  background: #ffc107;
}
</style>
