<template>
  <div class="teacher-info">
    <img class="teacher-image" :src="`https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg`" alt="Teacher Image">
    <div class="teacher-details">
      <h1 class="teacher-name">Name </h1>
      <p class="teacher-description">{{ $route.params.teacherId }}</p>
      <p class="teacher-description">This is a sample introduction</p>
    </div>
  </div>
</template>

<style scoped>
.teacher-info {
  max-width: 600px;
  margin: 50px auto 0;
  display: flex; 
  height: 100vh; 
}

.teacher-image {
  max-width: 50%; 
  max-height: 50%;
  margin-right: 20px;
}

.teacher-details {
  flex: 1;
}

.teacher-name {
  font-size: 24px;
  font-weight: bold;
}

.teacher-description {
  font-size: 16px;
  color: #333;
  margin-top: 10px;
}
</style>