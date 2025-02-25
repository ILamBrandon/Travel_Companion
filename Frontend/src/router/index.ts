import { createRouter, createWebHistory } from 'vue-router'
import LoginRegister from '@/components/LoginRegister.vue'
import CalendarView from '@/components/CalendarView.vue'
import ItineraryForm from '@/components/ItineraryForm/ItineraryForm.vue'
import WeatherUI from '@/components/WeatherUI.vue'

const routes = [
  { path: '/', name: 'LoginRegister', component: LoginRegister },
  { path: '/calendar', name: 'CalendarView', component: CalendarView },
  { path: '/itineraries', name: 'ItineraryForm', component: ItineraryForm },
  { path: '/weather', name: 'WeatherUI', component: WeatherUI },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
