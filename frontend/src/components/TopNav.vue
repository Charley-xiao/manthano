<script setup lang="ts">
</script>

<template>
  <div class="topnav">

    <div class="context">

      <img src="../assets/logo.jpg" alt="logo" style="width: 40px; height: 40px;" />

      <div class="title">
        <h2>Open Course Platform</h2>
      </div>

    </div>

    <div class="misc">

      <div class="search">
        <input type="text" placeholder="Search" />
        <button>Search</button>
      </div>

      <!-- <button @click="toRegOrLog">Sign In / Up</button> -->
      <RouterLink to="/RegistrationAndLogin">Sign In / Up</RouterLink>

      <div class="mode">
        <img src="../assets/moon.svg" alt="moon" />
        <img src="../assets/sun.svg" alt="sun" />
      </div>

    </div>

  </div>

</template>

<style scoped lang="scss">
// button {
//   background-color: transparent;
//   border: rgb(from blue r g b) 1px solid;
//   cursor: pointer;
//   padding: 0.5em;
//   height: 70%;
// }

.topnav {
  width: 100%;
  height: max(7%, 50px);
  border-bottom: 1px solid #ccc;
  display: flex;
  justify-content: space-between;

  .context {
    display: flex;
    justify-content: start;
    align-items: center;
    width: max-content;
    margin: 0 5px;

    .title {
      margin: 0 5px;

      h2 {
        margin: 0;
        font-size: 1.5rem;
        display: flex;
        justify-content: start;
        align-items: start;
        color: rebeccapurple;
      }
    }
  }

  .misc {
    display: flex;
    justify-content: end;
    align-items: center;
    width: max-content;
    margin: 0 5px;

    .search {
      display: flex;
      align-items: center;
      margin-right: 10px;

      input {
        padding: 0.5em;
        margin-right: 5px;
        border: 1px solid #ccc;
        border-radius: 4px;
      }

    }

    button {
      margin-left: 10px;
      padding: 0.5em 1em;
      border: 1px solid #ccc;
      border-radius: 4px;
      background-color: #f0f0f0;
    }

    .mode {
      display: flex;
      align-items: center;
      margin-left: 10px;

      img {
        width: 24px;
        height: 24px;
        margin-left: 5px;
        cursor: pointer;
      }
    }
  }
}
</style>