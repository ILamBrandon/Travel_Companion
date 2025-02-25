<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <!-- Bigger Container -->
    <div class="relative w-full max-w-5xl h-[500px] bg-white rounded-xl shadow-2xl overflow-hidden">
      <!-- Form Panel -->
      <div
        class="absolute top-0 left-0 w-1/2 h-full transition-transform duration-1000 ease-in-out"
        :class="{
          'translate-x-0': isLogin,
          'translate-x-full': !isLogin
        }"
      >
        <div class="flex flex-col justify-center items-center h-full p-10">
          <h2 class="text-3xl font-bold text-gray-800 mb-6">
            {{ isLogin ? 'Welcome Back' : 'Create an Account' }}
          </h2>
          <form @submit.prevent="isLogin ? loginUser() : registerUser()" class="w-full">
            <!-- Username Input -->
            <div class="mb-4">
              <label class="block text-gray-700 mb-2">Username</label>
              <input
                v-model="username"
                type="text"
                placeholder="Enter your username"
                autocomplete="off"
                required
                class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300 text-black"
              />
              <p v-if="errors.username" class="text-red-500 text-sm mt-1">
                {{ Array.isArray(errors.username) ? errors.username[0] : errors.username }}
              </p>
            </div>
            <!-- Email Input (only for register) -->
            <div v-if="!isLogin" class="mb-4">
              <label class="block text-gray-700 mb-2">Email</label>
              <input
                v-model="email"
                type="email"
                placeholder="Enter your email"
                autocomplete="off"
                required
                class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300 text-black"
              />
              <p v-if="errors.email" class="text-red-500 text-sm mt-1">
                {{ Array.isArray(errors.email) ? errors.email[0] : errors.email }}
              </p>
            </div>
            <!-- Password Input -->
            <div class="mb-4">
              <label class="block text-gray-700 mb-2">Password</label>
              <input
                v-model="password"
                type="password"
                placeholder="Enter your password"
                autocomplete="off"
                required
                class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-300 text-black"
              />
              <p v-if="errors.password" class="text-red-500 text-sm mt-1">
                {{ Array.isArray(errors.password) ? errors.password[0] : errors.password }}
              </p>
            </div>
            <!-- Non-field Errors -->
            <div v-if="errors.non_field_errors" class="mb-4">
              <p class="text-red-500 text-sm">
                {{ Array.isArray(errors.non_field_errors) ? errors.non_field_errors[0] : errors.non_field_errors }}
              </p>
            </div>
            <!-- Submit Button with Conditional Spinner/Text -->
            <button
              type="submit"
              class="w-full py-3 mt-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-300 flex justify-center items-center focus:outline-none border-0"
            >
              <template v-if="loading">
                <svg
                  class="animate-spin h-6 w-6 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  ></path>
                </svg>
              </template>
              <template v-else>
                <span>{{ isLogin ? 'Login' : 'Register' }}</span>
              </template>
            </button>
          </form>
        </div>
      </div>
      <!-- Info Panel -->
      <div
        class="absolute top-0 left-1/2 w-1/2 h-full transition-transform duration-1000 ease-in-out"
        :class="{
          'translate-x-0': isLogin,
          '-translate-x-full': !isLogin
        }"
      >
        <div class="flex flex-col justify-center items-center h-full p-10 bg-blue-500">
          <h2 class="text-3xl font-bold text-white mb-4">
            {{ isLogin ? "Don't have an account?" : 'Already have an account?' }}
          </h2>
          <p class="text-white text-center mb-8">
            {{ isLogin ? 'Sign up now and join us!' : 'Sign in to continue your journey!' }}
          </p>
          <button
            @click="toggleMode"
            class="bg-white text-blue-500 px-8 py-3 rounded-md font-bold hover:bg-gray-200 transition duration-300 focus:outline-none border-0"
          >
            {{ isLogin ? 'Sign Up' : 'Login In' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'LoginRegister',
  data() {
    return {
      isLogin: true,
      username: '',
      email: '',
      password: '',
      errors: {},
      loading: false,
    };
  },
  methods: {
    toggleMode() {
      // Clear the form fields and errors when toggling modes
      this.username = '';
      this.email = '';
      this.password = '';
      this.errors = {};
      this.isLogin = !this.isLogin;
    },
    async loginUser() {
      this.loading = true;
      this.errors = {};
      try {
        const response = await api.post('users/login/', {
          username: this.username,
          password: this.password,
        });
        const { access, refresh } = response.data;
        // Use the auth store to set tokens
        const authStore = useAuthStore();
        authStore.setTokens(access, refresh);
        localStorage.setItem('username', this.username);
        this.$router.push('/calendar');
      } catch (err) {
        this.errors.non_field_errors = 'Invalid username or password. Please try again.';
      } finally {
        this.loading = false;
      }
    },
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
          confirmButtonText: 'OK',
        });
        this.toggleMode();
      } catch (err) {
        if (err.response && err.response.data) {
          this.errors = err.response.data;
          if (
            this.errors.username &&
            Array.isArray(this.errors.username) &&
            this.errors.username[0] === 'A user with that username already exists.'
          ) {
            this.errors.username = 'Username already exists.';
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