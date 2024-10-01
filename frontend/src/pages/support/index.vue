<script lang="ts" setup>
import { ref } from 'vue';
import axios from 'axios';

const faqData = ref([
    { question: 'How do I join a course?', answer: 'To join a course, click on the "Explore" tab in the navigation bar. Then, click on the course you want to join.' },
    { question: 'How do I submit an assignment?', answer: 'To submit an assignment, click on the "Assignments" tab in the course page. Then, click on the assignment you want to submit and follow the instructions.' },
    { question: 'How do I contact support?', answer: 'To contact support, click on the "Support" tab in the navigation bar. Then, fill out the form with your name, email, and issue, and click "Submit". Our support team will get back to you by email as soon as possible.' },
]);

const showFaq = ref<number | null>(null);
const toggleFaq = (index: number) => {
    showFaq.value = showFaq.value === index ? null : index;
};

const name = ref<string>('');
const email = ref<string>('');
const issue = ref<string>('');
const isSubmitting = ref<boolean>(false);

const submitTicket = async () => {
    isSubmitting.value = true;
    try {
        const params = new URLSearchParams();
        params.append('name', name.value);
        params.append('email', email.value);
        params.append('issue', issue.value);

        const response = await axios.post('/api/submit-ticket', params);
        if (response.status === 200) {
            alert('Your ticket has been submitted.');
        }
    } catch (error) {
        console.error('Error submitting ticket:', error);
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<template>
    <div id="support" class="slide-in">
        <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            <div class="faq-container">
                <div v-for="(faq, index) in faqData" :key="index" class="faq-item">
                    <h3 @click="toggleFaq(index)" class="faq-question">
                        {{ faq.question }}
                        <span v-if="showFaq === index">-</span>
                        <span v-else>+</span>
                    </h3>
                    <p v-if="showFaq === index" class="faq-answer">{{ faq.answer }}</p>
                </div>
            </div>
        </div>

        <div class="ticket-section">
            <h2>Submit a Ticket</h2>
            <form @submit.prevent="submitTicket" class="ticket-form">
                <label for="name">Name:</label>
                <input type="text" id="name" v-model="name" class="input3d-flip" required />

                <label for="email">Email:</label>
                <input type="email" id="email" v-model="email" class="input3d-flip" required />

                <label for="issue">Issue:</label>
                <textarea id="issue" v-model="issue" class="input3d-flip" required></textarea>

                <button type="submit" class="submit-button-rotate">
                    <span v-if="!isSubmitting">Submit</span>
                </button>
            </form>
        </div>
    </div>
</template>

<style scoped>
.slide-in {
  animation: slideIn 1s ease-in-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.faq-section {
  padding: 40px;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.faq-container {
  margin-top: 20px;
}

.faq-item {
  margin-bottom: 20px;
}

.faq-question {
  cursor: pointer;
  font-size: 18px;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.faq-question:hover {
  background-color: #e0e0e0;
}

.faq-answer {
  margin-top: 10px;
  font-size: 16px;
  padding-left: 15px;
  transition: opacity 0.3s ease;
}

.ticket-section {
  padding: 40px;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.ticket-form {
  display: flex;
  flex-direction: column;
}

.input3d-flip {
  width: 100%;
  padding: 15px;
  margin-bottom: 20px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 16px;
  transition: transform 0.4s ease-in-out, box-shadow 0.3s ease;
}

.input3d-flip:focus {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: scale(1.005);
  outline: none;
}

.submit-button-rotate {
  width: 100%;
  padding: 15px;
  background: linear-gradient(45deg, #f39c12, #e67e22);
  color: #fff;
  font-size: 18px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s ease-in-out, background 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-button-rotate:hover {
  transform: rotate(0deg);
  background: linear-gradient(45deg, #e67e22, #f39c12);
}
</style>
