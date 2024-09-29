<script lang="ts" setup>
console.log("Registration and Login Page");
</script>

<template>
    <div class="registration-and-login">
        <div class="registration">
            <h1>Registration</h1>
            <form>
                <input type="text" placeholder="First Name" />
                <input type="text" placeholder="Last Name" />
                <input type="email" placeholder="Email" />
                <input type="password" placeholder="Password" />
                <input type="password" placeholder="Confirm Password" />
                <button>Register</button>
            </form>
        </div>
        <div class="login">
            <h1>Login</h1>
            <form>
                <input type="email" placeholder="Email" />
                <input type="password" placeholder="Password" />
                <button>Login</button>
            </form>
        </div>
    </div>
</template>

<style scoped lang="scss"></style>