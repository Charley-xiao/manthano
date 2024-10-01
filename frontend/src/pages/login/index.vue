<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;
const router = useRouter();

const username = ref<string>('');
const password = ref<string>('');
const isLoading = ref<boolean>(false);

const login = async () => {
    isLoading.value = true;
    try {
        const params = new URLSearchParams();
        params.append('username', username.value);
        params.append('password', password.value);
        const response = await axios.post('/api/login', params, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        if (response.data.success) {
            router.push('/course');
            window.location.reload();
        } else {
            console.log(response.data.message);
        }
    } catch (error: any) {
        console.error('An error occurred while logging in:', error);
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div id="login" class="fade-in">
        <div class="login-container">
            <h2>Login</h2>
            <form @submit.prevent="login" class="login-form">
                <label for="username">Username:</label>
                <input type="text" id="username" v-model="username" required class="input3d" />

                <label for="password">Password:</label>
                <input type="password" id="password" v-model="password" required class="input3d" />

                <button type="submit" class="submit-button">
                    <span v-if="!isLoading">Login</span>
                    <span v-else class="spinner"></span>
                </button>
            </form>
            <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
        </div>
    </div>
</template>

<style scoped>
.fade-in {
  animation: fadeIn 0.8s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 20px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  transform: perspective(1000px) rotateX(0deg);
  transition: transform 0.6s;
}

.login-container:hover {
  transform: perspective(1000px) rotateX(5deg);
}

.input3d {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  transition: box-shadow 0.3s, transform 0.3s;
}

.input3d:focus {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  transform: translateZ(5px);
  outline: none;
}

.submit-button {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #6b46c1, #d53f8c);
  color: #fff;
  font-size: 18px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-button:hover {
  background: linear-gradient(135deg, #d53f8c, #6b46c1);
  transform: translateY(-5px);
}

.spinner {
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top: 3px solid #6b46c1;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

p {
  margin-top: 20px;
}

p a {
  color: #6b46c1;
  text-decoration: none;
}

p a:hover {
  text-decoration: underline;
}
</style>
