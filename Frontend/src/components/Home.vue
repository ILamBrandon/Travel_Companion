<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="home-container">
    <div class="content-box">
      <h1 class="title">Welcome to Travel Planner</h1>
      <p class="subtitle">
        <strong>Your ultimate travel companion!</strong> Plan your trips, check real-time weather updates, and discover exciting attractions—all in one place.
      </p>

      <div class="features">
        <p>🌍 <strong>Explore</strong> new destinations effortlessly</p>
        <p>☀️ <strong>Get real-time</strong> weather updates for your travels</p>
        <p>📝 <strong>Organize</strong> and customize your trip</p>
        <p>🎟️ <strong>Find</strong> the best attractions and events</p>
      </div>

      <!-- Buttons for Login and Register -->
      <div class="auth-buttons">
        <RouterLink to="/login" class="button login-btn">Login</RouterLink>
        <RouterLink to="/register" class="button register-btn">Create Account</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

.home-container {
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Moves content higher */
  height: 100vh;
  padding-top: 10vh; /* Pushes content slightly up */
  font-family: 'Poppins', sans-serif;
  background-image: url('@/assets/Pictures/Airplane_Background.jpg'); /* Replace with your image file */
  background-size: cover;
  background-position: center;
  text-align: center;
}

/* Slightly higher positioned content box */
.content-box {
  background: rgba(0, 0, 0, 0.6); /* Dark background for contrast */
  padding: 40px;
  border-radius: 12px;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  color: #fff;
}

/* Blue title */
.title {
  font-size: 2.8rem;
  font-weight: 700;
  color: #007bff; /* Blue title */
  margin-bottom: 15px;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.7);
}

.subtitle {
  font-size: 1.3rem;
  font-weight: 600;
  line-height: 1.6;
  margin-bottom: 20px;
}

.features {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 30px;
}

.features p {
  margin: 10px 0;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}

.auth-buttons {
  margin-top: 20px;
}

/* Buttons */
.button {
  display: inline-block;
  padding: 12px 24px;
  margin: 10px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1.2rem;
  transition: all 0.3s ease-in-out;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
}

.login-btn {
  background-color: #007bff;
  color: white;
}

.login-btn:hover {
  background-color: #0056b3;
}

.register-btn {
  background-color: #28a745;
  color: white;
}

.register-btn:hover {
  background-color: #1e7e34;
}
</style>
