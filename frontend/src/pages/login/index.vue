<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;
const router = useRouter();

const username = ref<string>('');
const password = ref<string>('');

const login = async () => {
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
    }
};
</script>

<template>
    <div id="login">
        <h2>Login</h2>
        <form @submit.prevent="login">
            <label for="username">Username:</label>
            <input type="text" id="username" v-model="username" required />
            <label for="password">Password:</label>
            <input type="password" id="password" v-model="password" required />
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
    </div>
</template>

<style scoped lang="scss"></style>
