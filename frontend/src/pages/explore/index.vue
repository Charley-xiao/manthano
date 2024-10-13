<template>
    <div class="explore-page">
      <div class="header-section">
        <h1>Explore Courses</h1>
        <p>Discover trending and recommended courses tailored for you</p>
      </div>
  
      <div class="sort-filter">
        <div class="sort-select">
          <label for="sort">Sort by: </label>
          <select v-model="selectedSort" @change="sortCourses">
            <option value="trending">Trending</option>
            <option value="newest">Newest</option>
            <option value="popularity">Popularity</option>
            <option value="rating">Rating</option>
          </select>
        </div>
  
        <div class="filter-options">
          <span>Filter by: </span>
          <button
            v-for="filter in filters"
            :key="filter"
            @click="applyFilter(filter)"
            :class="{'active-filter': selectedFilter === filter}"
          >
            {{ filter }}
          </button>
        </div>
      </div>
  
      <div class="course-grid">
        <div
          v-for="course in sortedCourses"
          :key="course.id"
          class="course-card"
          @click="goToCourse(course.id)"
        >
          <div class="course-thumbnail">
            <img :src="course.thumbnail" alt="Course thumbnail" />
            <div class="overlay">
              <button @click.stop="goToCourse(course.id)">View Course</button>
            </div>
          </div>
          <div class="course-info">
            <h3>{{ course.title }}</h3>
            <p>{{ course.instructor }}</p>
            <div class="course-rating">Rating: {{ course.rating }} ★</div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  
  export default defineComponent({
    name: 'ExplorePage',
    setup() {
      const selectedSort = ref<string>('trending');
      const selectedFilter = ref<string>('All');
      const filters = ref<string[]>(['All', 'Development', 'Design', 'Business']);
      const courses = ref([
        {
          id: 1,
          title: 'Introduction to TypeScript',
          instructor: 'John Doe',
          thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
          rating: 4.5,
        },
        {
          id: 2,
          title: 'Advanced Vue.js Techniques',
          instructor: 'Jane Smith',
          thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
          rating: 4.7,
        },
        // more courses
      ]);
  
      const sortedCourses = ref([...courses.value]);
  
      const sortCourses = () => {
        if (selectedSort.value === 'trending') {
          // Sort by trending logic
        } else if (selectedSort.value === 'newest') {
          // Sort by newest logic
        }
      };
  
      const applyFilter = (filter: string) => {
        selectedFilter.value = filter;
        // Filter logic based on selected filter
      };
  
      const goToCourse = (courseId: number) => {
        // Navigate to the course details
      };
  
      return {
        selectedSort,
        selectedFilter,
        filters,
        sortedCourses,
        sortCourses,
        applyFilter,
        goToCourse,
      };
    },
  });
  </script>
  
  <style scoped>
  .explore-page {
    padding: 40px;
    background-color: #f9f9f9;
    color: #333;
  }
  
  .header-section {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .header-section h1 {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2c3e50;
  }
  
  .header-section p {
    font-size: 1.2rem;
    color: #7f8c8d;
  }
  
  .sort-filter {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
  
  .sort-select select {
    padding: 10px;
    font-size: 1rem;
    border: 1px solid #bdc3c7;
    border-radius: 5px;
    background-color: #ecf0f1;
    color: #34495e;
  }
  
  .filter-options {
    display: flex;
    gap: 10px;
  }
  
  .filter-options button {
    padding: 10px 20px;
    border: 1px solid #bdc3c7;
    background-color: #ecf0f1;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .filter-options button.active-filter {
    background-color: #3498db;
    color: white;
  }
  
  .filter-options button:hover {
    background-color: #3498db;
    color: white;
  }
  
  .course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
  
  .course-card {
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
  }
  
  .course-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  }
  
  .course-thumbnail {
    position: relative;
  }
  
  .course-thumbnail img {
    width: 100%;
    height: auto;
  }
  
  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: none;
    background: rgba(0, 0, 0, 0.5);
    justify-content: center;
    align-items: center;
    transition: display 0.3s;
  }
  
  .course-card:hover .overlay {
    display: flex;
  }
  
  .overlay button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .overlay button:hover {
    background-color: #2980b9;
  }
  
  .course-info {
    padding: 15px;
    text-align: center;
  }
  
  .course-info h3 {
    font-size: 1.2rem;
    color: #2c3e50;
  }
  
  .course-info p {
    font-size: 1rem;
    color: #7f8c8d;
  }
  
  .course-rating {
    margin-top: 10px;
    font-size: 1rem;
    color: #f39c12;
  }
  </style>
  