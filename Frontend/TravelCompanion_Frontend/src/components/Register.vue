<template>
  <div class="wrapper">
    <div class="glass-container">
      <h2 class="title">Create an Account</h2>
      <form @submit.prevent="registerUser" class="form">
        <!-- Username Input -->
        <div class="input-group">
          <label>Username</label>
          <input v-model="username" type="text" placeholder="Enter your username" required />
          <p v-if="errors.username" class="error">{{ errors.username[0] }}</p>
        </div>
        <!-- Email Input -->
        <div class="input-group">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="Enter your email" required />
          <p v-if="errors.email" class="error">{{ errors.email[0] }}</p>
        </div>
        <!-- Password Input -->
        <div class="input-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter your password" required />
          <p v-if="errors.password" class="error">{{ errors.password[0] }}</p>
        </div>
        <!-- General Error Messages -->
        <p v-if="errors.non_field_errors" class="error">{{ errors.non_field_errors[0] }}</p>
        <!-- Register Button -->
        <button type="submit" class="register-button" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>
      <!-- Additional Options -->
      <p class="login-link">
        Already have an account?
        <router-link to="/login" class="link">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import Swal from 'sweetalert2';

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      errors: {},
      loading: false,
    };
  },
  methods: {
    async registerUser() {
      this.loading = true;
      this.errors = {};
      try {
        await api.post('users/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
        });
        Swal.fire({
          title: 'Success!',
          text: 'Account created successfully.',
          icon: 'success',
          confirmButtonText: 'OK'
        });
        this.$router.push('/login');
      } catch (err) {
        if (err.response && err.response.data) {
          this.errors = err.response.data;
          if (this.errors.username && this.errors.username[0] === "A user with that username already exists.") {
            this.errors.username[0] = "Username already exists.";
          }
        } else {
          alert('Registration failed due to an unexpected error.');
        }
      } finally {
        this.loading = false;
      }
    },
  },
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
  transform: translate(-50%, -45%);
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 500px;
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
  width: 120%;
  margin-bottom: 1.5rem;
  transform: translateX(-20%);
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
  font-size: 1.1rem;
  margin-top: 0.5rem;
}

.register-button {
  width: 145%;
  padding: 18px;
  background: linear-gradient(135deg, #007bff, #00c6ff);
  color: white;
  font-size: 1.4rem;
  font-weight: bold;
  border-radius: 12px;
  cursor: pointer;
  transform: translateX(-18%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1rem;
}

.register-button:hover {
  background: linear-gradient(135deg, #0056b3, #0096c7);
  transform: scale(1.05);
}

.register-button:disabled {
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

.login-link {
  margin-top: 1.5rem;
  color: white;
  font-size: 1.1rem;
}

.link {
  color: #00c6ff;
  font-weight: bold;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
