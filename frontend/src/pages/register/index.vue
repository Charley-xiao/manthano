<script lang="ts" setup>
import axios from 'axios';
axios.defaults.withCredentials = true;
const router = useRouter();

const username = ref<string>('');
const password = ref<string>('');
const email = ref<string>('');
const role = ref<string>('student');

const register = async () => {
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
    }
};
</script>

<template>
    <div id="registration">
        <h2>Registration</h2>
        <form @submit.prevent="register">
            <label for="username">Username:</label>
            <input type="text" id="username" v-model="username" required />
            <label for="password">Password:</label>
            <input type="password" id="password" v-model="password" required />
            <label for="email">Email:</label>
            <input type="email" id="email" v-model="email" required />
            <label for="role">Role:</label>
            <select id="role" v-model="role">
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
            </select>
            <button type="submit">Register</button>
        </form>
    </div>
</template>

<style scoped lang="scss"></style>