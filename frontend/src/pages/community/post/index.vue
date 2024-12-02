<script setup lang="ts">
const route = useRoute();
const postId = route.params.id;

onMounted(() => {
    console.log(postId);
});
</script>

<template>
    <div id="post-page" class="post-page-container">

    </div>
</template>

<style scoped></style>