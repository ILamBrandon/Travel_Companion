// src/api.ts
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/', // Adjust if necessary
});

// Request interceptor to attach the token and refresh it if needed.
api.interceptors.request.use(
  async (config) => {
    const authStore = useAuthStore();

    // Log current tokens (for debugging)
    console.log("Current access token:", authStore.accessToken);
    console.log("Current refresh token:", authStore.refreshToken);

    if (authStore.accessToken) {
      // Check if the access token will expire within 60 seconds.
      if (authStore.tokenWillExpireSoon(60)) {
        console.log("Access token is about to expire. Attempting refresh...");
        try {
          // Request a new access token using the refresh token.
          const response = await axios.post(
            'http://localhost:8000/api/users/token/refresh/',
            {
              refresh: authStore.refreshToken,
            }
          );
          console.log("Refresh successful, new token:", response.data.access);
          // Update the store with the new access token.
          authStore.setTokens(response.data.access, authStore.refreshToken);
          config.headers.Authorization = `Bearer ${response.data.access}`;
        } catch (error) {
          console.error("Error refreshing token:", error);
          // If token refresh fails, clear tokens (and optionally redirect to login).
          authStore.clearTokens();
          // Optionally, redirect the user to login.
          // window.location.href = '/login';
        }
      } else {
        // Token is valid; attach it to the request.
        config.headers.Authorization = `Bearer ${authStore.accessToken}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
