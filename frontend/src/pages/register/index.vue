<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;
const router = useRouter();

const username = ref<string>('');
const password = ref<string>('');
const email = ref<string>('');
const role = ref<string>('student');
const isLoading = ref<boolean>(false);

const register = async () => {
    isLoading.value = true;
    try {
        const params = new URLSearchParams();
        params.append('username', username.value);
        params.append('password', password.value);
        params.append('email', email.value);
        params.append('role', role.value);

        const response = await axios.post('/api/register', params);
        if (response.status === 200) {
            router.push('/login');
        }
    } catch (error: any) {
        console.error('An error occurred while registering:', error);
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div id="registration" class="slide-in">
        <div class="registration-container">
            <h2>Register</h2>
            <form @submit.prevent="register" class="registration-form">
                <label for="username">Username:</label>
                <input type="text" id="username" v-model="username" required class="input3d-flip" />

                <label for="password">Password:</label>
                <input type="password" id="password" v-model="password" required class="input3d-flip" />

                <label for="email">Email:</label>
                <input type="email" id="email" v-model="email" required class="input3d-flip" />

                <label for="role">Role:</label>
                <select id="role" v-model="role" class="input3d-flip">
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                </select>

                <button type="submit" class="submit-button-rotate">
                    <span v-if="!isLoading">Register</span>
                    <span v-else class="spinner"></span>
                </button>
            </form>
        </div>
    </div>
</template>

<style scoped>
.slide-in {
  animation: slideIn 1s ease-in-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.registration-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: transform 0.5s ease-in-out;
  transform: perspective(1000px) rotateY(0deg);
}

.registration-container:hover {
  transform: perspective(1000px) rotateY(8deg);
}

.input3d-flip {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  transition: transform 0.4s ease-in-out, box-shadow 0.3s ease;
}

.input3d-flip:focus {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: perspective(600px) rotateY(10deg);
  outline: none;
}

.submit-button-rotate {
  width: 100%;
  padding: 15px;
  background: linear-gradient(45deg, #2ecc71, #1abc9c);
  color: #fff;
  font-size: 18px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s ease-in-out, background 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-button-rotate:hover {
  transform: rotate(360deg);
  background: linear-gradient(45deg, #1abc9c, #2ecc71);
}

.spinner {
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top: 3px solid #2ecc71;
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
  color: #1abc9c;
  text-decoration: none;
}

p a:hover {
  text-decoration: underline;
}
</style>
