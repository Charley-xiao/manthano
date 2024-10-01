<script lang="ts" setup>
import { useRouter } from 'vue-router';
import axios from 'axios';
axios.defaults.withCredentials = true;

const router = useRouter();
const isLoading = ref<boolean>(false);

const logout = async () => {
    isLoading.value = true;
    try {
        document.cookie.split(";").forEach((c) => {
            document.cookie = c
                .replace(/^ +/, "")
                .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        router.push('/login');
        window.location.reload();
    } catch (error) {
        console.error('An error occurred while logging out:', error);
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div id="logout" class="fade-in">
        <div class="logout-container">
            <h2>Log Out?</h2>
            <h3>This cannot be undone.</h3>
            <button @click="logout" class="logout-button-shake">
                <span v-if="!isLoading">Logout</span>
                <span v-else class="spinner"></span>
            </button>
            <router-link to="/course" class="cancel-link">Keep my session</router-link>
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

.logout-container {
  max-width: 400px;
  margin: 150px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.5s ease-in-out;
  transform: perspective(1000px) rotateX(0deg);
}

.logout-container:hover {
  transform: perspective(1000px) rotateX(8deg);
}

.logout-button-shake {
  width: 100%;
  padding: 15px;
  background: linear-gradient(45deg, #e74c3c, #c0392b);
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

.logout-button-shake:hover {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% {
    transform: translate3d(-1px, 0, 0);
  }
  20%, 80% {
    transform: translate3d(2px, 0, 0);
  }
  30%, 50%, 70% {
    transform: translate3d(-4px, 0, 0);
  }
  40%, 60% {
    transform: translate3d(4px, 0, 0);
  }
}

.spinner {
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top: 3px solid #e74c3c;
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

.cancel-link {
  display: block;
  margin-top: 20px;
  text-decoration: none;
  color: #3498db;
}

.cancel-link:hover {
  text-decoration: underline;
}
</style>
