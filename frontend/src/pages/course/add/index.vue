<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();

// Form data
const courseTitle = ref('');
const courseDescription = ref('');
const courseCategory = ref('');
const categories = [
  'Science',
  'Mathematics',
  'Literature',
  'Technology',
  'Art',
  'History',
  'Geography',
  'Physics',
  'Chemistry',
  'Biology',
  'Music',
  'Philosophy',
  'Economics',
  'Business',
  'Psychology',
  'Sociology',
  'Political Science',
  'Law',
  'Medicine',
  'Engineering',
  'Architecture',
  'Education',
  'Environmental Science',
  'Computer Science',
  'Statistics',
  'Anthropology',
  'Linguistics',
  'Religious Studies',
  'Performing Arts',
  'Visual Arts',
  'Media Studies',
  'Communication',
  'Astronomy',
  'Earth Science',
  'Agriculture',
  'Forestry',
  'Veterinary Science',
  'Nutrition',
  'Public Health',
  'Sports Science',
  'Library Science',
  'Information Technology',
  'Culinary Arts',
  'Fashion Design',
  'Graphic Design',
  'Interior Design',
  'Journalism',
  'Marketing',
  'Photography',
  'Theater',
  'Film Studies',
  'Animation',
  'Game Design',
  'Web Development',
  'Cybersecurity',
  'Data Science',
  'Artificial Intelligence',
  'Machine Learning',
  'Robotics',
  'Blockchain',
  'Quantum Computing',
  'Astrophysics',
  'Marine Biology',
  'Genetics',
  'Neuroscience',
  'Bioinformatics',
  'Biotechnology',
  'Materials Science',
  'Nanotechnology',
  'Renewable Energy',
  'Climate Science',
  'Urban Planning',
  'Real Estate',
  'Hospitality Management',
  'Tourism',
  'Event Management',
  'Human Resources',
  'Supply Chain Management',
  'Project Management',
  'Public Administration',
  'International Relations',
  'Criminology',
  'Forensic Science',
  'Social Work',
  'Counseling',
  'Speech Therapy',
  'Occupational Therapy',
  'Physical Therapy',
  'Radiology',
  'Dentistry',
  'Pharmacy',
  'Optometry',
  'Podiatry',
  'Chiropractic',
  'Alternative Medicine',
  'Health Informatics',
  'Biomedical Engineering',
  'Aerospace Engineering',
  'Civil Engineering',
  'Mechanical Engineering',
  'Electrical Engineering',
  'Chemical Engineering',
  'Industrial Engineering',
  'Systems Engineering',
  'Nuclear Engineering',
  'Petroleum Engineering',
  'Mining Engineering',
  'Textile Engineering',
  'Automotive Engineering',
  'Marine Engineering',
  'Structural Engineering',
  'Geotechnical Engineering',
  'Transportation Engineering',
  'Water Resources Engineering',
  'Construction Management',
  'Surveying',
  'Cartography',
  'Geographic Information Systems',
  'Remote Sensing',
  'Meteorology',
  'Oceanography',
  'Hydrology',
  'Seismology',
  'Volcanology',
  'Paleontology',
  'Archaeology',
  'Museology',
  'Archival Science',
  'Genealogy',
  'Heritage Studies',
  'Conservation Science',
  'Restoration',
  'Art History',
  'Art Therapy',
  'Music Therapy',
  'Dance',
  'Choreography',
  'Music Production',
  'Sound Engineering',
  'Music Theory',
  'Composition',
  'Conducting',
  'Music Performance',
  'Ethnomusicology',
  'Music Education',
  'Music Business',
  'Music Technology',
  'Musicology',
  'Opera',
  'Jazz Studies',
  'Popular Music',
  'World Music',
  'Music Therapy',
  'Music Production',
  'Sound Engineering',
  'Music Theory',
  'Composition',
  'Conducting',
  'Music Performance',
  'Ethnomusicology',
  'Music Education',
  'Music Business',
  'Music Technology',
  'Musicology',
  'Opera',
  'Jazz Studies',
  'Popular Music',
  'World Music',
  'Physics',
  'Chemistry',
  'Biology',
  'Mathematics',
  'Computer Science',
  'Data Science',
  'Artificial Intelligence',
  'Machine Learning',
  'Robotics',
  'Quantum Computing',
  'Nanotechnology',
  'Biotechnology',
  'Genetics',
  'Neuroscience',
  'Bioinformatics',
  'Biomedical Engineering',
  'Aerospace Engineering',
  'Civil Engineering',
  'Mechanical Engineering',
  'Electrical Engineering',
  'Chemical Engineering',
  'Industrial Engineering',
  'Systems Engineering',
  'Nuclear Engineering',
  'Petroleum Engineering',
  'Mining Engineering',
  'Textile Engineering',
  'Automotive Engineering',
  'Marine Engineering',
  'Structural Engineering',
  'Geotechnical Engineering',
  'Transportation Engineering',
  'Water Resources Engineering',
  'Environmental Science',
  'Renewable Energy',
  'Climate Science',
  'Earth Science',
  'Astronomy',
  'Astrophysics',
  'Marine Biology',
  'Materials Science',
  'Cybersecurity',
  'Web Development',
  'Software Engineering',
  'Hardware Engineering',
  'Network Engineering',
  'Cloud Computing',
  'Internet of Things',
  'Smart Cities',
  'Autonomous Vehicles',
  'Space Exploration',
  'Marine Exploration',
  'Environmental Planning',
  'Urban Planning',
  'Construction Management',
  'Surveying',
  'Cartography',
  'Geographic Information Systems',
  'Remote Sensing',
  'Meteorology',
  'Oceanography',
  'Hydrology',
  'Seismology',
  'Volcanology',
  'Paleontology',
  'Archaeology',
  'Conservation Science',
  'Restoration',
  'Art and Science',
  'Art and Technology',
  'Art and Environment',
  'Art and Sustainability',
  'Art and Innovation',
  'Art and Creativity',
  'Art and Communication',
  'Art and Media',
  'Art and Performance',
  'Art and Installation',
  'Art and Sculpture',
  'Art and Painting',
  'Art and Drawing',
  'Art and Printmaking',
  'Art and Photography',
  'Art and Film',
  'Art and Video',
  'Art and Animation',
  'Art and Game Design',
  'Art and Virtual Reality',
  'Art and Augmented Reality',
  'Art and Artificial Intelligence',
  'Art and Machine Learning',
  'Art and Robotics',
  'Art and Biotechnology',
  'Art and Nanotechnology',
  'Art and Quantum Computing',
  'Art and Blockchain',
  'Art and Data Science',
  'Art and Cybersecurity',
  'Art and Web Development',
  'Art and Mobile Development',
  'Art and Software Engineering',
  'Art and Hardware Engineering',
  'Art and Network Engineering',
  'Art and Cloud Computing',
  'Art and Internet of Things',
  'Art and Smart Cities',
  'Art and Autonomous Vehicles',
  'Art and Space Exploration',
  'Art and Marine Exploration',
  'Art and Environmental Science',
  'Art and Climate Change',
  'Art and Renewable Energy',
  'Art and Sustainable Development',
  'Art and Social Justice',
  'Art and Human Rights',
  'Art and Gender Studies',
  'Art and LGBTQ+ Studies',
  'Art and Disability Studies',
  'Art and Critical Race Theory',
  'Art and Postcolonial Studies',
  'Art and Indigenous Studies',
  'Art and Migration Studies',
  'Art and Globalization',
  'Art and Urban Studies',
  'Art and Rural Studies',
  'Art and Community Development',
  'Art and Public Policy',
  'Art and Governance',
  'Art and International Relations',
  'Art and Diplomacy',
  'Art and Conflict Resolution',
  'Art and Peace Studies',
  'Art and Security Studies',
  'Art and Intelligence Studies',
  'Art and Military Studies',
  'Art and Defense Studies',
  'Art and Strategic Studies',
  'Art and Terrorism Studies',
  'Art and Counterterrorism',
  'Art and Homeland Security',
  'Art and Emergency Management',
  'Art and Disaster Management',
  'Art and Crisis Management',
  'Art and Risk Management',
  'Art and Project Management',
  'Art and Operations Management',
  'Art and Supply Chain Management',
  'Art and Logistics',
  'Art and Transportation',
  'Art and Infrastructure',
  'Art and Urban Planning',
  'Art and Real Estate',
  'Art and Construction',
  'Art and Architecture',
  'Art and Interior Design',
  'Art and Landscape Architecture',
  'Art and Urban Design',
  'Art and Regional Planning',
  'Art and Environmental Planning',
  'Art and Transportation Planning',
  'Art and Housing Studies',
  'Art and Community Planning',
  'Art and Economic Development',
  'Art and Tourism',
  'Art and Hospitality',
  'Art and Event Management',
  'Art and Sports Management',
  'Art and Recreation',
  'Art and Leisure Studies',
  'Art and Entertainment',
  'Art and Media Studies',
  'Art and Journalism',
  'Art and Broadcasting',
  'Art and Film Studies',
  'Art and Television Studies',
  'Art and Radio Studies',
  'Art and Digital Media',
  'Art and Social Media',
  'Art and Advertising',
  'Art and Public Relations',
  'Art and Marketing',
  'Art and Consumer Behavior',
  'Art and Brand Management',
  'Art and Sales',
  'Art and E-commerce',
  'Art and Retail Management',
  'Art and Fashion Studies',
  'Art and Textile Studies',
  'Art and Costume Design',
  'Art and Jewelry Design',
  'Art and Industrial Design',
  'Art and Product Design',
  'Art and Graphic Design',
  'Art and Web Design',
  'Art and User Experience Design',
  'Art and User Interface Design',
  'Art and Interaction Design',
  'Art and Information Design',
  'Art and Communication Design',
  'Art and Exhibition Design',
  'Art and Set Design',
  'Art and Lighting Design',
  'Art and Sound Design',
  'Art and Music Production',
  'Art and Music Technology',
  'Art and Music Business',
  'Art and Music Education',
  'Art and Music Therapy',
  'Art and Music Performance',
  'Art and Music Composition',
  'Art and Music Theory',
  'Art and Music History',
  'Art and Musicology',
  'Art and Ethnomusicology',
  'Art and Jazz Studies',
  'Art and Popular Music',
  'Art and World Music',
  'Art and Opera',
  'Art and Dance',
  'Art and Choreography',
  'Art and Theater',
  'Art and Drama',
  'Art and Acting',
  'Others',
  'Classical Studies',
  'Medieval Studies',
  'Renaissance Studies',
  'Baroque Studies',
  'Romanticism',
  'Modernism',
  'Postmodernism',
  'Contemporary Art',
  'Digital Art',
  'Art Criticism',
  'Art Conservation',
  'Art Restoration',
  'Art Curation',
  'Art Exhibition Design',
  'Art Marketing',
  'Art Law',
  'Art Therapy',
  'Art Education',
  'Art History',
  'Art Management',
  'Art Business',
  'Art Entrepreneurship',
  'Art Technology',
  'Art and Design',
  'Art and Culture',
  'Art and Society',
  'Art and Politics',
  'Art and Religion',
  'Art and Science',
  'Art and Technology',
  'Art and Environment',
  'Art and Sustainability',
  'Art and Innovation',
  'Art and Creativity',
  'Art and Communication',
  'Art and Media',
  'Art and Performance',
  'Art and Installation',
  'Art and Sculpture',
  'Art and Painting',
  'Art and Drawing',
  'Art and Printmaking',
  'Art and Photography',
  'Art and Film',
  'Art and Video',
  'Art and Animation',
  'Art and Game Design',
  'Art and Virtual Reality',
  'Art and Augmented Reality',
  'Art and Artificial Intelligence',
  'Art and Machine Learning',
  'Art and Robotics',
  'Art and Biotechnology',
  'Art and Nanotechnology',
  'Art and Quantum Computing',
  'Art and Blockchain',
  'Art and Data Science',
  'Art and Cybersecurity',
  'Art and Web Development',
  'Art and Mobile Development',
  'Art and Software Engineering',
  'Art and Hardware Engineering',
  'Art and Network Engineering',
  'Art and Cloud Computing',
  'Art and Internet of Things',
  'Art and Smart Cities',
  'Art and Autonomous Vehicles',
  'Art and Space Exploration',
  'Art and Marine Exploration',
  'Art and Environmental Science',
  'Art and Climate Change',
  'Art and Renewable Energy',
  'Art and Sustainable Development',
  'Art and Social Justice',
  'Art and Human Rights',
  'Art and Gender Studies',
  'Art and LGBTQ+ Studies',
  'Art and Disability Studies',
  'Art and Critical Race Theory',
  'Art and Postcolonial Studies',
  'Art and Indigenous Studies',
  'Art and Migration Studies',
  'Art and Globalization',
  'Art and Urban Studies',
  'Art and Rural Studies',
  'Art and Community Development',
  'Art and Public Policy',
  'Art and Governance',
  'Art and International Relations',
  'Art and Diplomacy',
  'Art and Conflict Resolution',
  'Art and Peace Studies',
  'Art and Security Studies',
  'Art and Intelligence Studies',
  'Art and Military Studies',
  'Art and Defense Studies',
  'Art and Strategic Studies',
  'Art and Terrorism Studies',
  'Art and Counterterrorism',
  'Art and Homeland Security',
  'Art and Emergency Management',
  'Art and Disaster Management',
  'Art and Crisis Management',
  'Art and Risk Management',
  'Art and Project Management',
  'Art and Operations Management',
  'Art and Supply Chain Management',
  'Art and Logistics',
  'Art and Transportation',
  'Art and Infrastructure',
  'Art and Urban Planning',
  'Art and Real Estate',
  'Art and Construction',
  'Art and Architecture',
  'Art and Interior Design',
  'Art and Landscape Architecture',
  'Art and Urban Design',
  'Art and Regional Planning',
  'Art and Environmental Planning',
  'Art and Transportation Planning',
  'Art and Housing Studies',
  'Art and Community Planning',
  'Art and Economic Development',
  'Art and Tourism',
  'Art and Hospitality',
  'Art and Event Management',
  'Art and Sports Management',
  'Art and Recreation',
  'Art and Leisure Studies',
  'Art and Entertainment',
  'Art and Media Studies',
  'Art and Journalism',
  'Art and Broadcasting',
  'Art and Film Studies',
  'Art and Television Studies',
  'Art and Radio Studies',
  'Art and Digital Media',
  'Art and Social Media',
  'Art and Advertising',
  'Art and Public Relations',
  'Art and Marketing',
  'Art and Consumer Behavior',
  'Art and Brand Management',
  'Art and Sales',
  'Art and E-commerce',
  'Art and Retail Management',
  'Art and Fashion Studies',
  'Art and Textile Studies',
  'Art and Costume Design',
  'Art and Jewelry Design',
  'Art and Industrial Design',
  'Art and Product Design',
  'Art and Graphic Design',
  'Art and Web Design',
  'Art and User Experience Design',
  'Art and User Interface Design',
  'Art and Interaction Design',
  'Art and Information Design',
  'Art and Communication Design',
  'Art and Exhibition Design',
  'Art and Set Design',
  'Art and Lighting Design',
  'Art and Sound Design',
  'Art and Music Production',
  'Art and Music Technology',
  'Art and Music Business',
  'Art and Music Education',
  'Art and Music Therapy',
  'Art and Music Performance',
  'Art and Music Composition',
  'Art and Music Theory',
  'Art and Music History',
  'Art and Musicology',
  'Art and Ethnomusicology',
  'Art and Jazz Studies',
  'Art and Popular Music',
  'Art and World Music',
  'Art and Opera',
  'Art and Dance',
  'Art and Choreography',
  'Art and Theater',
  'Art and Drama',
  'Art and Acting',
  'Biomedical Engineering',
  'Interdisciplinary Studies',
  'Cognitive Science',
  'Environmental Studies',
  'Global Studies',
  'Health Sciences',
  'Humanities',
  'International Studies',
  'Neuroscience',
  'Science, Technology, and Society',
  'Sustainability Studies',
  'Women\'s Studies',
  'Cultural Studies',
  'Development Studies',
  'Ethnic Studies',
  'Gender Studies',
  'Peace and Conflict Studies',
  'Urban Studies',
  'Others'
];
const courseImage = ref<File | null>(null);

// Form status
const isSubmitting = ref(false);
const errors = ref<{ [key: string]: string }>({});

// Handle image upload preview
/*const previewImage = ref<string | ArrayBuffer | null>(null);
const handleImageUpload = (event: Event) => {
  const files = (event.target as HTMLInputElement).files;
  if (files && files[0]) {
    courseImage.value = files[0];
    const reader = new FileReader();
    reader.onload = () => (previewImage.value = reader.result);
    reader.readAsDataURL(files[0]);
  }
};*/

// Validate the form
const validateForm = () => {
  errors.value = {};
  if (!courseTitle.value) errors.value.title = 'Title is required';
  if (!courseDescription.value) errors.value.description = 'Description is required';
  if (!courseCategory.value) errors.value.category = 'Category is required';
  return Object.keys(errors.value).length === 0;
};

// Submit form
const submitCourse = async () => {
  if (!validateForm()) return;

  isSubmitting.value = true;

  const formData = new FormData();
  formData.append('title', courseTitle.value);
  formData.append('description', courseDescription.value);
  formData.append('category', courseCategory.value);
  formData.append('owner', localStorage.getItem('username') || '');
  if (courseImage.value) formData.append('image', courseImage.value);

  try {
    await axios.post('/api/add/course', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    alert('Request for adding course sent successfully!');
    router.push('/');
  } catch (error) {
    console.error('Error adding course:', error);
    alert('An error occurred while adding the course. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(() => {
  const uniqueCategories = Array.from(new Set(categories));
  categories.length = 0;
  categories.push(...uniqueCategories);
  categories.sort((a, b) => a.localeCompare(b));
});
</script>

<template>
  <div class="add-course-page">
    <h1>Add a New Course</h1>
    <form @submit.prevent="submitCourse" class="course-form">
      <!-- Course Title -->
      <div class="form-group">
        <label for="title">Course Title</label>
        <input type="text" id="title" v-model="courseTitle" placeholder="Enter course title" />
        <span v-if="errors.title" class="error">{{ errors.title }}</span>
      </div>

      <!-- Course Description -->
      <div class="form-group">
        <label for="description">Course Description</label>
        <textarea id="description" v-model="courseDescription" placeholder="Describe your course"></textarea>
        <span v-if="errors.description" class="error">{{ errors.description }}</span>
      </div>

      <!-- Course Category -->
      <div class="form-group">
        <label for="category">Category</label>
        <select id="category" v-model="courseCategory">
          <option value="" disabled>Select a category</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
        <span v-if="errors.category" class="error">{{ errors.category }}</span>
      </div>

      <!-- Course Image -->
      <!-- <div class="form-group">
        <label for="image">Course Image</label>
        <input type="file" id="image" @change="handleImageUpload" accept="image/*" />
        <div v-if="previewImage" class="image-preview">
          <img :src="previewImage" alt="Course Preview" />
        </div>
      </div> -->

      <!-- Submit Button -->
      <button type="submit" :disabled="isSubmitting" class="submit-button">
        {{ isSubmitting ? 'Submitting...' : 'Add Course' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.add-course-page {
  max-width: 600px;
  margin: 50px auto;
  padding: 30px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  font-family: 'Montserrat', sans-serif;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 28px;
  color: #333;
}

.course-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: bold;
  margin-bottom: 5px;
}

input,
textarea,
select {
  padding: 10px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

textarea {
  resize: vertical;
}

.error {
  color: red;
  font-size: 14px;
  margin-top: 5px;
}

.image-preview {
  margin-top: 10px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.submit-button {
  padding: 12px;
  border: none;
  background: linear-gradient(135deg, #42e695, #3bb2b8);
  color: white;
  font-weight: bold;
  font-size: 18px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.submit-button:hover {
  background: linear-gradient(135deg, #ff6a00, #ee0979);
}

.submit-button:disabled {
  background: #ddd;
  cursor: not-allowed;
}
</style>
