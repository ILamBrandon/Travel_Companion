<template>
  <div id="app">
    <div class="layout">
      <!-- Sidebar -->
      <div v-if="sidebarOpen" class="sidebar">
        <div>
          <div class="sidebar-header">
            <button class="icon-button" @click="toggleSidebar" title="Close Sidebar">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
            <div class="search-wrapper">
              <input
                v-if="searchVisible"
                type="text"
                class="search-input"
                placeholder="Search..."
                v-model="searchQuery"
              />
              <button class="icon-button" @click="toggleSearch" title="Search">
                <svg width="24" height="24" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M15.5,14H14.71L14.43,13.73A6.96,6.96,0,0,0,16,9.5,7,7,0,1,0,9,16.5,6.96,6.96,0,0,0,13.73,14.43L14,14.71V15.5L19,20.49,20.49,19,15.5,14ZM9,14A5,5,0,1,1,14,9,5,5,0,0,1,9,14Z"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="sidebar-create">
            <button class="itinerary-button" @click="createItinerary">
              <svg width="24" height="24" viewBox="0 0 24 24" class="itinerary-icon">
                <path fill="currentColor" d="M3 17.25V21h3.75l11-11.03-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a1 1 0 0,0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
              </svg>
              <span>Create Itinerary</span>
            </button>
            <button class="itinerary-button" @click="getWeather" title="Get Weather">
              <svg width="24" height="24" viewBox="0 0 24 24" class="weather-icon">
                <path fill="currentColor" d="M19.35 10.04A7.49 7.49 0 0 0 12 4a7.5 7.5 0 0 0-7.07 4.36A5.5 5.5 0 0 0 6.5 19h12a4.5 4.5 0 0 0 .85-8.96z"/>
              </svg>
              <span>Get Weather</span>
            </button>
            <!-- Itinerary summaries -->
            <div class="itinerary-summaries" v-if="filteredItineraries.length">
              <div class="itinerary-summary" v-for="(itinerary, index) in filteredItineraries" :key="itinerary.id">
                <div class="itinerary-dates">
                  {{ formatDate(itinerary.start_date) }} - {{ formatDate(itinerary.end_date) }}
                </div>
                <div class="itinerary-title-container">
                  <span
                    class="itinerary-title"
                    @click="goToItinerary(itinerary)"
                    :title="`Go to start date: ${itinerary.start_date}`"
                  >
                    {{ itinerary.title }}
                  </span>
                  <!-- Group action buttons -->
                  <div class="action-buttons">
                    <button class="edit-button" @click="editItinerary(itinerary)" title="Edit This Trip">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#e74c3c" class="bi bi-wrench" viewBox="0 0 16 16">
                        <path d="M.102 2.223A3.004 3.004 0 0 0 3.78 5.897l6.341 6.252A3.003 3.003 0 0 0 13 16a3 3 0 1 0-.851-5.878L5.897 3.781A3.004 3.004 0 0 0 2.223.1l2.141 2.142L4 4l-1.757.364z"/>
                      </svg>
                    </button>
                    <button class="trash-button" @click="confirmDelete(itinerary)" title="Delete This Trip">
                      <svg width="16" height="16" viewBox="0 0 24 24">
                        <path fill="currentColor" d="M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9Z"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Sidebar footer -->
        <div class="sidebar-footer">
          <span class="username">{{ username }}</span>
          <button class="logout-button" @click="logout">Logout</button>
        </div>
      </div>
      <!-- Open-sidebar button -->
      <button v-else class="open-sidebar-button" @click="toggleSidebar" title="Open Sidebar">
        <svg width="24" height="24" viewBox="0 0 24 24">
          <path fill="currentColor" d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"/>
        </svg>
      </button>
      <!-- Main content area -->
      <div :class="['main', { 'full-width': !sidebarOpen }]">
        <vue-cal
          ref="vueCal"
          :events="events"
          :views="['years', 'year', 'month', 'week', 'day', 'agenda']"
          :disable-views="['years', 'year', 'day']"
          :time="true"
          :min-time="8"
          :max-time="18"
          :time-formatter="formatTime"
          twelve-hour
          @event-click="handleEventClick"
          @view-change="handleViewChange"
          @event-create="handleEventCreate"
          locale="en"
          title-position="center"
          :drag-and-drop="true"
          :resize="true"
        />
      </div>
    </div>
  </div>
</template>

<script>
import VueCal from 'vue-cal';
import 'vue-cal/dist/vuecal.css';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';
import api from "@/services/api";


export default {
  name: 'CalendarView',
  components: { VueCal },
  data() {
    return {
      sidebarOpen: true,
      searchVisible: false,
      searchQuery: '',
      events: [],
      submittedItineraries: []
    };
  },
  computed: {
    username() {
      return localStorage.getItem('username') || 'Guest';
    },
    sortedItineraries() {
      return this.submittedItineraries.slice().sort((a, b) => {
        const startA = new Date(a.start_date);
        const startB = new Date(b.start_date);
        if (startA.getTime() !== startB.getTime()) {
          return startA - startB;
        }
        const endA = new Date(a.end_date);
        const endB = new Date(b.end_date);
        return endA - endB;
      });
    },
    filteredItineraries() {
      // If no search query is provided, return all sorted itineraries.
      if (!this.searchQuery) {
        return this.sortedItineraries;
      }
      return this.sortedItineraries.filter(itinerary =>
        itinerary.title.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    getStorageKey(keyBase) {
      return `${keyBase}_${this.username}`;
    },
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
      if (!this.sidebarOpen) {
        this.searchVisible = false;
      }
    },
    toggleSearch() {
      this.searchVisible = !this.searchVisible;
    },
    logout() {
      const authStore = useAuthStore();
      authStore.clearTokens();
      localStorage.removeItem('username');
      this.$router.push('/');
    },
    createItinerary() {
      this.$router.push('/itineraries');
    },
    getWeather() {
      this.$router.push('/weather');
    },
    goToItinerary(itinerary) {
      if (this.$refs.vueCal) {
        this.$refs.vueCal.switchView('week');
        this.$refs.vueCal.goToDate(itinerary.start_date);
      }
    },
    handleEventClick(event) {
      const { title, planningDetail = {}, city, state, country } = event;
      const rawCategory = planningDetail.category || 'Unknown Category';
      const formattedCategory = rawCategory.replace(/_/g, ' ');
      const startTime =
        planningDetail.startTime ||
        event.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
      const durationText = `${planningDetail.durationHours || 0}h ${planningDetail.durationMinutes || 0}m`;
      const endTime =
        planningDetail.endTime ||
        event.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });

      // Build the location string using available data.
      const locationStr = [city,country].filter(Boolean).join(', ');
      Swal.fire({
        title: `Event: ${title}`,
        html: `<div style="text-align:left">
          <p><strong>Category:</strong> ${formattedCategory}</p>
          <p><strong>Start Time:</strong> ${startTime}</p>
          <p><strong>Duration:</strong> ${durationText}</p>
          <p><strong>End Time:</strong> ${endTime}</p>
          <p><strong>Location:</strong> ${locationStr}</p>
        </div>`,
        icon: 'info'
      });
    },
    handleViewChange(view) {
      console.log('Current view:', view);
    },
    handleEventCreate(newEvent) {
      console.log('New event created:', newEvent);
      this.events.push(newEvent);
      this.saveEvents();
    },
    loadEvents() {
      const saved = localStorage.getItem(this.getStorageKey('calendarEvents'));
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          this.events = parsed.map(event => ({
            ...event,
            start: new Date(event.start),
            end: new Date(event.end)
          }));
        } catch (e) {
          console.error('Error parsing saved events:', e);
          this.events = [];
        }
      }
    },
    saveEvents() {
      localStorage.setItem(
        this.getStorageKey('calendarEvents'),
        JSON.stringify(this.events)
      );
    },
    loadSubmittedItineraries() {
      const saved = localStorage.getItem(this.getStorageKey('submittedItineraries'));
      if (saved) {
        try {
          this.submittedItineraries = JSON.parse(saved);
        } catch (e) {
          console.error('Error parsing submitted itineraries:', e);
          this.submittedItineraries = [];
        }
      }
    },
    saveSubmittedItineraries() {
      localStorage.setItem(
        this.getStorageKey('submittedItineraries'),
        JSON.stringify(this.submittedItineraries)
      );
    },
    checkSubmittedItinerary() {
      const itineraryData = localStorage.getItem('submittedItinerary');
      if (itineraryData) {
        try {
          const itinerary = JSON.parse(itineraryData);
          const itineraryId = itinerary.id;
          itinerary.id = itineraryId;
          const attractions = itinerary.addedAttractions || [];

          // Remove any events that belong to this itinerary so we only show the current stage.
          this.events = this.events.filter(event => event.itineraryId !== itineraryId);

          if (itinerary.planningDetails) {
            Object.keys(itinerary.planningDetails)
              .filter(key => key.startsWith("planned_"))
              .forEach(key => {
                const detail = itinerary.planningDetails[key];
                if (
                  detail.date &&
                  detail.time &&
                  detail.durationHours != null &&
                  detail.durationMinutes != null
                ) {
                  const startDateTime = new Date(`${detail.date}T${detail.time}`);
                  const durationMs =
                    (parseInt(detail.durationHours, 10) * 3600 +
                      parseInt(detail.durationMinutes, 10) * 60) * 1000;
                  const endDateTime = new Date(startDateTime.getTime() + durationMs);
                  const eventTitle = detail.attractionName || itinerary.title || 'Untitled';
                  const matchingAttraction = attractions.find(attr => {
                    return (attr.osm_id && detail.osm_id && attr.osm_id === detail.osm_id) ||
                          (attr.name && detail.attractionName && attr.name === detail.attractionName);
                  });
                  const event = {
                    title: eventTitle,
                    start: startDateTime,
                    end: endDateTime,
                    allDay: false,
                    planningDetail: {
                      ...detail,
                      category: detail.category || (matchingAttraction && matchingAttraction.tourism) || itinerary.category,
                      endTime: endDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
                    },
                    city: (matchingAttraction && matchingAttraction.city) || itinerary.city,
                    state: (matchingAttraction && matchingAttraction.state) || itinerary.state,
                    country: (matchingAttraction && matchingAttraction.country) || itinerary.country,
                    reason: itinerary.reason,
                    itineraryId
                  };
                  this.events.push(event);
                }
              });
            this.saveEvents();
          }

          this.loadSubmittedItineraries();
          // Check if this itinerary already exists in our array
          const index = this.submittedItineraries.findIndex(item => item.id === itineraryId);
          if (index !== -1) {
            // Update the existing itinerary
            this.submittedItineraries.splice(index, 1, itinerary);
          } else {
            // Add as a new itinerary if it wasn’t found
            this.submittedItineraries.push(itinerary);
          }

          this.saveSubmittedItineraries();

          // Clear cached trip weather if the itinerary is within the next week.
          const now = new Date();
          const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
          const itineraryStart = new Date(itinerary.start_date);
          itineraryStart.setDate(itineraryStart.getDate() + 1);
          if (itineraryStart >= now && itineraryStart <= weekLater) {
            console.log("Itinerary is within one week. Clearing cached trip weather.");
            localStorage.removeItem("cachedTripWeather");
          } 

          localStorage.removeItem('submittedItinerary');
        } catch (e) {
          console.error('Error parsing submitted itinerary:', e);
        }
      }
    },
    confirmDelete(itinerary) {
      Swal.fire({
        title: `Are you sure you want to delete "${itinerary.title}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it',
        cancelButtonText: 'No, keep it'
      }).then(result => {
        if (result.isConfirmed) {
          // Call the backend API to delete the itinerary from the MySQL database.
          api.delete(`itineraries/${itinerary.id}/`, { withCredentials: true })
            .then(response => {
              localStorage.removeItem("cachedTripWeather");
              this.deleteItinerarySummary(itinerary.id);
              Swal.fire({
                title: 'Deleted!',
                text: `"${itinerary.title}" has been deleted.`,
                icon: 'success'
              });
            })
            .catch(error => {
              console.error("Error deleting itinerary:", error);
              Swal.fire({
                title: 'Error!',
                text: 'There was a problem deleting the itinerary.',
                icon: 'error'
              });
            });
        }
      });
    },
    deleteItinerarySummary(itineraryId) {
      this.events = this.events.filter(event => event.itineraryId !== itineraryId);
      this.saveEvents();
      this.submittedItineraries = this.submittedItineraries.filter(item => item.id !== itineraryId);
      this.saveSubmittedItineraries();
    },
    editItinerary(itinerary) {
      // Clear the cached trip weather data since the trip is being edited.
      localStorage.removeItem("cachedTripWeather");
      localStorage.setItem('editItinerary', JSON.stringify(itinerary));
      this.$router.push('/itineraries');
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      date.setDate(date.getDate() + 1);
      const options = { month: 'short', day: 'numeric', year: 'numeric' };
      return date.toLocaleDateString('en-US', options);
    },
    formatTime(date) {
      return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
    }
  },
  mounted() {
    this.loadEvents();
    this.loadSubmittedItineraries();
    this.checkSubmittedItinerary();
  }
};
</script>

<style>
/* (existing styles remain unchanged) */
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}
.layout {
  display: flex;
  flex-wrap: nowrap;
  height: 100vh;
  width: 100vw;
}
.icon-button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
}
.open-sidebar-button {
  position: absolute;
  top: 0.3rem;
  left: 0.5rem;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
  z-index: 10;
}
.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  width: 20%;
  background-color: #141414;
  color: white;
  padding: 1rem;
  box-sizing: border-box;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.search-wrapper {
  display: flex;
  align-items: center;
}
.search-input {
  margin-right: 0.5rem;
  padding: 0.4rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  color: #000;
  max-width: 200px;
}
.sidebar-create {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.itinerary-button {
  display: flex;
  align-items: center;
  background-color: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}
.itinerary-button .itinerary-icon,
.itinerary-button .weather-icon {
  margin-right: 0.5rem;
}
.itinerary-summary:first-child {
  border-top: 1px solid #ccc;
  margin-bottom: 0;
  padding-bottom: 0;
}
.itinerary-summary {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #444;
}
.itinerary-dates {
  font-size: 0.85rem;
  color: #aaa;
}
.itinerary-title-container {
  display: flex;
  align-items: center;
  margin-top: 0.25rem;
  gap: 0.3rem;
}
.itinerary-title {
  font-weight: bold;
  font-size: 1rem;
  color: #fff;
  cursor: pointer;
  margin-right: auto;
}
.itinerary-title:hover {
  text-decoration: underline;
}
.action-buttons svg.bi.bi-wrench{
  height: 14px;
  width: 14px;
}
.edit-button {
  background: transparent;
  border: none;
  cursor: pointer;
  margin-left: 0;
}
.trash-button {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #e74c3c;
  margin-left: 0;
}
.action-buttons {
  display: flex;
  gap: 0.1rem;
}
.sidebar-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #333;
}
.username {
  font-size: 0.9rem;
  opacity: 0.8;
}
.logout-button {
  padding: 0.5rem 1rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  cursor: pointer;
}
.main {
  width: 80%;
  height: 100%;
  box-sizing: border-box;
  transition: width 0.3s ease;
  background-color: #1C1C1C;
}
.main.full-width {
  width: 100%;
}
.main > .vuecal {
  width: 100% !important;
  height: 100% !important;
}
.vuecal__event {
  cursor: pointer;
  max-height: 50px;
  overflow-y: auto;
}
.vuecal__event * {
  pointer-events: none;
}
.vuecal__header,
.vuecal__header .vuecal__nav,
.vuecal__header .vuecal__title,
.vuecal__cell-date,
.vuecal__header button {
  color: white !important;
}
</style>
