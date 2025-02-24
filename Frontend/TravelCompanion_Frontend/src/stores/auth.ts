// src/stores/auth.ts
import { defineStore } from 'pinia'
import * as jwtDecode from 'jwt-decode'

interface JwtPayload {
  exp: number; // expiration time in seconds since epoch
  // add other fields as needed
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
  }),
  actions: {
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      localStorage.setItem('accessToken', access)
      localStorage.setItem('refreshToken', refresh)
    },
    loadTokens() {
      const access = localStorage.getItem('accessToken')
      const refresh = localStorage.getItem('refreshToken')
      if (access && refresh) {
        this.accessToken = access
        this.refreshToken = refresh
      }
    },
    clearTokens() {
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    },
    tokenWillExpireSoon(bufferSeconds = 60): boolean {
      if (!this.accessToken) return true
      try {
        const decoded = jwtDecode<JwtPayload>(this.accessToken)
        const now = Date.now() / 1000 // current time in seconds
        // If the token expires within the buffer period, return true
        return (decoded.exp - now) < bufferSeconds
      } catch (error) {
        return true
      }
    },
  },
})
