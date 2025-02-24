import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/components/Home.vue'
import Register from '@/components/Register.vue'
import Login from '@/components/Login.vue'
import CalendarView from '@/components/CalendarView.vue'
import ItineraryForm from '@/components/ItineraryForm/ItineraryForm.vue'
import WeatherUI from '@/components/WeatherUI.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/calendar', name: 'CalendarView', component: CalendarView },
  { path: '/itineraries', name: 'ItineraryForm', component: ItineraryForm },
  { path: '/weather', name: 'WeatherUI', component: WeatherUI },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
