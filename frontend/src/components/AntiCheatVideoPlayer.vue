<template>
    <div class="anti-cheat-video-player">
      <video
        ref="video"
        :src="src"
        @timeupdate="onTimeUpdate"
        @play="onPlay"
        @pause="onPause"
        @ended="onVideoEnd"
        controls
        preload="metadata"
      ></video>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, watch, onMounted, onUnmounted } from 'vue';
  import { throttle } from 'lodash';
  
  export default defineComponent({
    name: 'AntiCheatVideoPlayer',
    props: {
      src: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const video = ref<HTMLVideoElement | null>(null);
      const inactivityThreshold = 3; // seconds of inactivity to detect cheating
      let lastActiveTime = Date.now(); // Last recorded active time
      let inactivityTimer: ReturnType<typeof setTimeout> | null = null;
  
      const resetInactivity = () => {
        lastActiveTime = Date.now();
      };
  
      const detectInactivity = () => {
        const timeSinceLastActive = (Date.now() - lastActiveTime) / 1000;
        if (timeSinceLastActive > inactivityThreshold) {
          if (video.value) {
            video.value.pause(); // Pause video on inactivity
            alert('Inactivity detected! Please continue watching.');
          }
        }
      };
  
      const onTimeUpdate = throttle(() => {
        resetInactivity(); // Reset inactivity whenever the video is progressing
      }, 1000);
  
      const onPlay = () => {
        resetInactivity(); // Reset inactivity on play
        if (inactivityTimer) clearInterval(inactivityTimer); // Clear previous timers
        inactivityTimer = setInterval(detectInactivity, 5000); // Check every 5 seconds
      };
  
      const onPause = () => {
        if (inactivityTimer) clearInterval(inactivityTimer); // Stop inactivity checks on pause
      };
  
      const onVideoEnd = () => {
        if (inactivityTimer) clearInterval(inactivityTimer); // Clean up on video end
      };
  
      watch(() => props.src, () => {
        // Reset everything when the video source changes
        if (video.value) video.value.currentTime = 0;
        resetInactivity();
      });
  
      onMounted(() => {
        window.addEventListener('mousemove', resetInactivity);
        window.addEventListener('keydown', resetInactivity);
      });
  
      onUnmounted(() => {
        if (inactivityTimer) clearInterval(inactivityTimer); // Clean up
        window.removeEventListener('mousemove', resetInactivity);
        window.removeEventListener('keydown', resetInactivity);
      });
  
      return {
        video,
        onTimeUpdate,
        onPlay,
        onPause,
        onVideoEnd,
      };
    },
  });
  </script>
  
  <style scoped>
  .anti-cheat-video-player {
    max-width: 100%;
    display: flex;
    justify-content: center;
  }
  video {
    width: 100%;
    height: auto;
  }
  </style>
  