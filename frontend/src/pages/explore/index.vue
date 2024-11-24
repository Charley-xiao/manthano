<template>
  <div class="explore-page">
    <div class="header-section">
      <h1>Explore</h1>
      <p>Discover trending and recommended courses and instructors</p>
    </div>


    <div class="tabs">
      <button :class="{ 'active-tab': activeTab === 'courses' }" @click="changeTab('courses')">
        Courses
      </button>
      <button :class="{ 'active-tab': activeTab === 'instructors' }" @click="changeTab('instructors')">
        Instructors
      </button>
    </div>

    <div v-if="activeTab === 'courses'" class="course-section">
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

        <div class="sort-select-right">
          <label for="sort">Filter by: </label>
          <select v-model="selectedFilter" @change="sortCourses">
            <option value="All">All</option>
            <option value="CS">Computer science</option>
            <option value="Math">Math</option>
            <option value="Physics">Physics</option>
          </select>
        </div>
      </div>

      <div class="course-grid">
        <div v-for="course in paginatedCourses" :key="course.id" class="course-card">
          <div class="course-info">
            <h3>{{ course.title }}</h3>
            <p>{{ course.instructor }}</p>
            <div class="course-rating">Rating: {{ course.rating }} ★</div>

            <div class="overlay">
              <router-link :to="'/community/course/' + course.id" class="view">View Course</router-link>
            </div>
          </div>
        </div>
      </div>

      <div class="choose">
        <div class="centered-container">
          <button v-for="page in displayedPages" :key="page" @click="changePage(page)"
            :class="{ 'button-round': true, 'selected-button': page === currentPage }">
            {{ page }}
          </button>
        </div>
      </div>

    </div>

    <div v-if="activeTab === 'instructors'" class="course-section">
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

        <div class="sort-select-right">
          <label for="sort">Filter by: </label>
          <select v-model="selectedFilter" @change="sortCourses">
            <option value="All">All</option>
            <option value="CS">Computer science</option>
            <option value="Math">Math</option>
            <option value="Physics">Physics</option>
          </select>
        </div>
      </div>

      <div class="course-grid">
        <div v-for="teacher in paginatedTeahcers" :key="teacher.id" class="course-card">
          <div class="course-thumbnail">
            <img :src="teacher.thumbnail" alt="Teacher thumbnail" />
            <div class="overlay">
              <router-link :to="'/community/teacher/' + teacher.id" class="view">View Teacher</router-link>
            </div>
          </div>
          <div class="course-info">
            <h3>{{ teacher.instructor }}</h3>
            <p>{{ teacher.intro }}</p>
            <div class="course-rating">Rating: {{ teacher.rating }} ★</div>
          </div>
        </div>
      </div>

      <div class="choose">
        <div class="centered-container">
          <button v-for="page in displayedPages" :key="page" @click="changePage(page)"
            :class="{ 'button-round': true, 'selected-button': page === currentPage }">
            {{ page }}
          </button>
        </div>
      </div>

    </div>

    <footer>
      <p>&copy; 2024 Study Forum. Built for learners.</p>
      <nav>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
      <br><br><br><br><br>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';

export default defineComponent({
  name: 'ExplorePage',
  setup() {
    const activeTab = ref<string>('courses');

    const changeTab = (tab: string) => {
      activeTab.value = tab;
      selectedSort.value = 'trending';
      selectedFilter.value = 'All';
      currentPage.value = 1;
      if (tab === 'courses') {
        itemsPerPage.value = 8;
      } else {
        itemsPerPage.value = 4;
      }
    };

    const selectedSort = ref<string>('trending');
    const selectedFilter = ref<string>('All');
    const currentPage = ref(1);
    const itemsPerPage = ref(8);
    const filters = ref<string[]>(['All', 'Development', 'Design', 'Business']);
    const courses = ref([
      {
        id: 1,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 2,
        title: 'Advanced Vue.js Techniques',
        instructor: 'Jane Smith',
        rating: 4.7,
      },
      {
        id: 3,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 4,
        title: 'Advanced Vue.js Techniques',
        instructor: 'Jane Smith',
        rating: 4.7,
      },
      {
        id: 5,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 6,
        title: 'Advanced Vue.js Techniques',
        instructor: 'Jane Smith',
        rating: 4.7,
      },
      {
        id: 7,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 8,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 9,
        title: 'Advanced Vue.js Techniques',
        instructor: 'Jane Smith',
        rating: 4.7,
      },
      {
        id: 10,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 11,
        title: 'Advanced Vue.js Techniques',
        instructor: 'Jane Smith',
        rating: 4.7,
      },
      {
        id: 12,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
      {
        id: 13,
        title: 'Introduction to TypeScript',
        instructor: 'John Doe',
        rating: 4.5,
      },
    ]);

    const teachers = ref([
      {
        id: 1,
        instructor: 'A',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 1.4,
      },
      {
        id: 2,
        instructor: 'B',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 4.5,
      },
      {
        id: 3,
        instructor: 'A',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 1.4,
      },
      {
        id: 4,
        instructor: 'B',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 4.5,
      },
      {
        id: 5,
        instructor: 'A',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 1.4,
      },
      {
        id: 6,
        instructor: 'B',
        thumbnail: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg',
        intro: 'This is a sample introduction',
        rating: 4.5,
      },
    ]);

    const sortedCourses = ref([...courses.value]);
    const sortedTeachers = ref([...teachers.value]);

    const sortCourses = () => {
      if (selectedSort.value === 'trending') {
        // Sort by trending logic
      } else if (selectedSort.value === 'newest') {
        // Sort by newest logic
      }
    };

    const paginatedCourses = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage.value;
      const endIndex = startIndex + itemsPerPage.value;
      return sortedCourses.value.slice(startIndex, endIndex);
    });

    const paginatedTeahcers = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage.value;
      const endIndex = startIndex + itemsPerPage.value;
      return sortedTeachers.value.slice(startIndex, endIndex);
    });

    const totalPages = computed(() => {
      if (activeTab.value === 'courses') {
        return Math.ceil(sortedCourses.value.length / itemsPerPage.value);
      } else {
        return Math.ceil(sortedTeachers.value.length / itemsPerPage.value);
      }
    });

    const displayedPages = computed(() => {
      const total = totalPages.value;
      let pages = [];

      for (let i = 1; i <= total; i++) {
        pages.push(i);
      }

      return pages;
    });

    const changePage = (page: number) => {
      currentPage.value = page;
    };
    return {
      selectedSort,
      selectedFilter,
      filters,
      sortedCourses,
      sortedTeachers,
      sortCourses,
      paginatedCourses,
      paginatedTeahcers,
      totalPages,
      displayedPages,
      changePage,
      activeTab,
      changeTab,
      currentPage,
    };
  },
});
</script>

<style scoped>
.explore-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  height: fit-content;

}

.header-section {
  text-align: center;
  padding: 50px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  animation: fade-in 1s ease-in-out;
}

.tabs {
  text-align: left;
  display: flex;
  justify-content: flex-start;
  margin-bottom: 10px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background-color: transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #333;
}

.tabs button.active-tab {
  color: #3498db;
  border-bottom: 2px solid #3498db;
}

.course-section {
  margin-left: 20px;
  margin-top: 20px;
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
  width: 150px;
}

.sort-select-right select {
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #bdc3c7;
  border-radius: 5px;
  background-color: #ecf0f1;
  color: #34495e;
  margin-right: 40px;
  width: 150px;
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
  margin-left: 20px;
  margin-right: 50px;

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

.instructor-section {
  display: none;
}

.active-tab-content {
  display: block;
}

.choose {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 5px;
  text-align: center;
}

.centered-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.button-round {
  display: inline-block;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 5px;
  border: 1px solid #ccc;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  font-size: 14px;
  font-family: Arial;
}

.selected-button {
  background-color: lightgray;
}

.button-round:hover {
  transform: translateY(-10px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
}


.view {
  display: inline-block;
  margin-top: 15px;
  background: #007bf0;
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  text-decoration: none;
  transition: background 0.3s ease;
}

footer {
  text-align: center;
  margin-top: 50px;
  font-size: 0.85rem;
  color: #555;
  animation: fade-in 1.2s ease-in-out;
}

footer nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #007BFF;
  font-weight: 600;
}

footer nav a:hover {
  color: #0056b3;
}
</style>