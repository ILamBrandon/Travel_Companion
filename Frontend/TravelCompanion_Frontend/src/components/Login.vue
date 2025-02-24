<template>
  <div class="wrapper">
    <div class="glass-container">
      <h2 class="title">Welcome Back</h2>
      <form @submit.prevent="loginUser" class="form">
        <!-- Username Input -->
        <div class="input-group">
          <label>Username</label>
          <input
            v-model="username"
            type="text"
            placeholder="Enter your username"
            @blur="validateField('username')"
            required
          />
        </div>
        <!-- Password Input -->
        <div class="input-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            @blur="validateField('password')"
            required
          />
        </div>
        <!-- Error Message -->
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <!-- Login Button -->
        <button type="submit" class="login-button" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Signing in...' : 'Login' }}
        </button>
      </form>
      <!-- Additional Options -->
      <p class="signup">
        Don't have an account?
        <router-link to="/register" class="signup-link">Sign up</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      errorMessage: ''
    };
  },
  methods: {
    async loginUser() {
      this.loading = true;
      this.errorMessage = '';
      try {
        const response = await api.post('users/login/', {
          username: this.username,
          password: this.password
        });
        const access = response.data.access;
        const refresh = response.data.refresh;
        const authStore = useAuthStore();
        authStore.setTokens(access, refresh);
        localStorage.setItem('username', this.username);
        this.$router.push('/calendar');
      } catch (err) {
        this.errorMessage = 'Invalid username or password. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    validateField(field) {
      // Optional: add field validation here if needed.
    }
  }
};
</script>

<style scoped>
.wrapper {
  width: 100vw;
  min-height: 100vh;
  background-size: 100% auto;
  background-image: url('@/assets/Pictures/Airplane_Background.jpg');
  background-repeat: no-repeat;
  background-position: center;
}

.glass-container {
  position: absolute;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -46%);
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 440px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.title {
  font-size: 2.8rem;
  font-weight: bold;
  color: white;
  margin-bottom: 2rem;
}

.input-group {
  width: 100%;
  margin-bottom: 1.5rem;
  transform: translateX(-10%);
}

.input-group label {
  display: block;
  font-size: 1.3rem;
  color: white;
  margin-bottom: 0.5rem;
  text-align: left;
}

.input-group input {
  width: 120%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 1.2rem;
  text-align: left;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.2);
  outline: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.input-group input:focus {
  background: rgba(255, 255, 255, 0.4);
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.4);
}

.error {
  color: red;
  font-size: 0.8rem;
  margin-bottom: 1rem;
  text-align: center;
  transform: translateX(-2%);
}

.form {
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-button {
  width: 120%;
  padding: 18px;
  background: linear-gradient(135deg, #007bff, #00c6ff);
  color: white;
  font-size: 1.4rem;
  font-weight: bold;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1rem;
}

.login-button:hover {
  background: linear-gradient(135deg, #0056b3, #0096c7);
  transform: scale(1.05);
}

.login-button:disabled {
  background: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
}

.loading-spinner {
  border: 2px solid white;
  border-top: 2px solid transparent;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.signup {
  margin-top: 2rem;
  color: white;
  font-size: 1.1rem;
}

.signup-link {
  color: #00c6ff;
  font-weight: bold;
  text-decoration: none;
}

.signup-link:hover {
  text-decoration: underline;
}
</style>
