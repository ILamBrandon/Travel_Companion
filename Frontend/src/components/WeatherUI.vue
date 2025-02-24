<template>
  <div id="app">
    <div class="layout">
      <!-- Sidebar -->
      <div class="sidebar">
        <nav class="sidebar-nav">
          <ul>
            <!-- City Weather remains first -->
            <li :class="{ active: currentView === 'city' }" @click="currentView = 'city'" aria-label="City Weather">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor"
                  d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.8 1.42-1.42zm10.48 0l1.42 1.42 1.79-1.8-1.41-1.41-1.8 1.79zM12 2h-1v3h1V2zm-7 9H2v1h3v-1zm16 0h-3v1h3v-1zM6.76 19.16l-1.79 1.8 1.41 1.41 1.8-1.79-1.42-1.42zm10.48 0l-1.42 1.42 1.8 1.79 1.41-1.41-1.79-1.8zM12 19v3h1v-3h-1zM8 12c0-2.21 1.79-4 4-4s4 1.79 4 4-1.79 4-4 4-4-1.79-4-4z"/>
              </svg>
              <span class="tooltip">City Weather</span>
            </li>
            <!-- Favorites now second -->
            <li :class="{ active: currentView === 'favorites' }" @click="currentView = 'favorites'" aria-label="Favorite Cities">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor"
                  d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
              </svg>
              <span class="tooltip">Favorite Cities</span>
            </li>
            <!-- Trip Weather now third -->
            <li :class="{ active: currentView === 'trip' }" @click="currentView = 'trip'" aria-label="Trip Weather">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor"
                  d="M20 6h-4V4c0-1.11-.89-2-2-2H10C8.9 2 8 2.89 8 4v2H4c-1.11 0-2 .89-2 2v10c0 1.1.89 2 2 2h16c1.11 0 2-.9 2-2V8c0-1.11-.89-2-2-2zm-8 0V4h4v2h-4zM4 18V8h16v10H4z"/>
              </svg>
              <span class="tooltip">Trip Weather</span>
            </li>
          </ul>
        </nav>
        <div class="exit-container">
          <!-- Exit button routes to calendar -->
          <button class="exit-door-button" @click="goToCalendar" aria-label="Go to Calendar">
            <svg width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M4 2h10v20H4zM14 2h6v20h-6z" opacity=".3"/>
              <path fill="currentColor"
                d="M4 2h10v20H4zm2 2v16h6V4H6zm10 0h6v20h-6zM16 4v16h2V4h-2z"/>
            </svg>
          </button>
        </div>
      </div>
      <!-- Main Content Area -->
      <div class="main">
        <div class="weather-container">
          <!-- Search Bar for City Weather -->
          <div v-if="currentView === 'city'" class="search-container">
            <div class="weather-search">
              <input type="text" v-model="city" placeholder="Enter city" @blur="autoCapitalize('city')" />
              <input type="text" v-model="country" placeholder="Enter country" @blur="autoCapitalize('country')" />
              <button class="search-btn" @click="getWeather" :disabled="loading">
                <span v-if="loading" class="spinner"></span>
                <span v-else>Search</span>
              </button>
            </div>
            <div v-if="error" class="error-message">{{ error }}</div>
          </div>
          <!-- Output Section -->
          <div class="output-container">
            <!-- City Weather View -->
            <div v-if="currentView === 'city' && currentWeatherDetails" class="current-weather">
              <div class="left-column">
                <div class="location-container">
                  <p class="location">{{ displayCity }}, {{ displayCountry }}</p>
                </div>
                <!-- Use Luxon to format the current time in the city's timezone -->
                <p class="date">{{ currentDayHeader }}</p>
                <div class="temp-display">
                  <span class="temp-number">{{ Math.round(currentWeatherDetails.temperature) }}°</span>
                  <span class="temp-icon" v-html="getTempIcon(currentWeatherDetails.temperature, currentWeatherDetails.condition)"></span>
                </div>
                <p class="condition">{{ currentWeatherDetails.condition }}</p>
              </div>
              <div class="right-column">
                <button class="add-button" @click="addCity">Add City</button>
                <p class="wind">
                  Wind: {{ getWindCardinal(currentWeatherDetails.wind_direction) }} {{ currentWeatherDetails.wind_speed }} mph
                </p>
                <p class="humidity">Humidity: {{ currentWeatherDetails.humidity }}%</p>
                <p class="uv-index">UV Index: {{ currentWeatherDetails.uv_index }}</p>
                <p class="sun-times">
                  <img src="/Users/brandon/Documents/Resume_Project/Travel_Companion/Frontend/src/assets/Pictures/Sunrise.png" alt="Sunrise" class="sun-icon sunrise-icon" />
                  {{ formatSunTime(currentWeatherDetails.sunrise) }} |
                  <img src="/Users/brandon/Documents/Resume_Project/Travel_Companion/Frontend/src/assets/Pictures/Sunset.png" alt="Sunset" class="sun-icon sunset-icon" />
                  {{ formatSunTime(currentWeatherDetails.sunset) }}
                </p>
              </div>
            </div>
            <!-- City Weather Forecast -->
            <div v-if="currentView === 'city' && weatherData && weatherData.daily && weatherData.hourly" class="forecast-container">
              <!-- Hourly Forecast -->
              <div class="hourly-section">
                <h2 class="hourly-header">{{ currentDayHeader }} - Hourly Forecast</h2>
                <div class="hourly-row" v-if="next25Hourly.length">
                  <div class="hourly-forecast" v-for="(hour, index) in next25Hourly" :key="'hourly-' + index">
                    <p class="time">{{ index === 0 ? 'Now' : formatHourlyTime(hour.time) }}</p>
                    <p class="icon" v-html="getTempIcon(hour.temperature_2m, getWeatherDescription(hour.weathercode))"></p>
                    <p class="temp">{{ Math.round(hour.temperature_2m) }}°F</p>
                  </div>
                </div>
              </div>
              <!-- 10-Day Forecast -->
              <div class="daily-section">
                <h2 class="daily-header">10-Day Forecast</h2>
                <div class="daily-row">
                  <div class="daily-forecast" v-for="(day, index) in weatherData.daily.time" :key="'daily-' + index">
                    <!-- Removed the extra day offset -->
                    <p class="day">{{ index === 0 ? 'Today' : formatDailyDate(day) }}</p>
                    <span class="icon" v-html="getTempIcon(weatherData.daily.temperature_2m_max[index], getWeatherDescription(weatherData.daily.weathercode[index]))"></span>
                    <p class="temp">
                      {{ Math.round(weatherData.daily.temperature_2m_max[index]) }}° 
                      {{ Math.round(weatherData.daily.temperature_2m_min[index]) }}°
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <!-- Favorites View -->
            <div v-else-if="currentView === 'favorites'" class="output-container">
              <h1>Favorite Cities</h1>
              <div class="favorites-search-bar">
                <input type="text" v-model="favoriteSearch" placeholder="Search favorites..." />
              </div>
              <div class="favorites-list">
                <div v-for="(fav, index) in filteredFavorites" :key="'fav-' + index" class="fav-item" @click="loadFavorite(fav)">
                  <div class="fav-left">
                    <p class="fav-city">{{ fav.city }}, {{ fav.country }}</p>
                    <p class="fav-time">
                      Local Time: 
                      {{ fav.timezone ? new Intl.DateTimeFormat("en-US", {
                        timeZone: fav.timezone,
                        hour: "numeric",
                        minute: "numeric",
                        hour12: true
                      }).format(new Date()) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                    </p>
                    <p class="fav-condition">{{ fav.condition || 'N/A' }}</p>
                  </div>
                  <div class="fav-right">
                    <span class="trash-icon" @click.stop="removeFavorite(index)">🗑️</span>
                    <p class="fav-temp">{{ fav.currentTemp !== undefined ? fav.currentTemp + '°' : 'N/A' }}</p>
                    <p class="fav-high-low">
                      H: {{ fav.high !== undefined ? Math.round(fav.high) + '°' : 'N/A' }}
                      L: {{ fav.low !== undefined ? Math.round(fav.low) + '°' : 'N/A' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <!-- Trip Weather View (uses event dates from local storage directly) -->
            <div v-else-if="currentView === 'trip'" class="output-container trip-output">
              <h1>Trip Weather</h1>
              <div v-if="tripLoading" class="loading-container">
                <span class="spinner"></span> Loading trip weather...
              </div>
              <div v-else>
                <div v-if="tripEvents.length === 0" class="no-events">
                  <p>No events in 1 week distance</p>
                </div>
                <div v-else v-if="currentTripDayKey">
                  <div class="trip-weather-header-wrapper">
                    <div class="trip-weather-header">
                      <button class="nav-button" v-if="currentTripDayIndex > 0" @click="prevDay">&lt;</button>
                      <!-- For trip weather, we simply display the event's stored date -->
                      <div class="day-info">{{ currentTripDayKey }}</div>
                      <button class="nav-button" v-if="currentTripDayIndex < sortedTripDays.length - 1" @click="nextDay">&gt;</button>
                    </div>
                  </div>
                  <div class="trip-weather-content">
                    <div class="trip-day-group">
                      <div class="trip-weather-item" v-for="(item, index) in groupedTripWeatherByDate[currentTripDayKey]" :key="'trip-' + index">
                        <div class="trip-event-left">
                          <p class="event-title">
                            {{ item.event.title || 'Untitled Event' }} - 
                            {{
                              (item.event.planningDetail && item.event.planningDetail.category 
                                ? item.event.planningDetail.category 
                                : (item.event.category || 'N/A')
                              ).replace(/_/g, ' ')
                            }}
                          </p>
                          <p class="event-time">
                            {{ formatHourlyTime(adjustDate(item.event.start)) }} - {{ formatHourlyTime(adjustDate(item.event.end)) }}
                          </p>
                          <p class="event-duration">
                            Duration: {{ formatDuration(adjustDate(item.event.start), adjustDate(item.event.end)) }}
                          </p>
                          <p class="event-location">
                            Location: {{ item.event.city }}, {{ item.event.country }}
                          </p>
                        </div>
                        <div class="trip-event-right">
                          <p class="temp-range" v-if="item.weather.tempRange">
                            {{ Math.round(item.weather.tempRange.min) }}° - {{ Math.round(item.weather.tempRange.max) }}°
                          </p>
                          <p class="temp-range" v-else>
                            Temperature: N/A
                          </p>
                          <p class="weather-condition">
                            Condition: {{ item.weather.condition || 'N/A' }}
                          </p>
                          <p class="wind">
                            Wind: 
                            <span v-if="item.weather.wind_speed !== 'N/A'">
                              {{ getWindCardinal(item.weather.wind_direction) }} {{ item.weather.wind_speed }} mph
                            </span>
                            <span v-else>N/A</span>
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- End Trip Weather View -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";
import { DateTime } from "luxon";

export default {
  name: "Weather",
  data() {
    return {
      currentView: "city",
      city: "",
      country: "",
      displayCity: "",
      displayCountry: "",
      weatherData: null,
      loading: false,
      error: "",
      favoriteCities: [],
      favoriteSearch: "",
      tripWeatherData: [],
      tripLoading: false,
      currentTripDayIndex: 0,
      currentTime: new Date() // Reactive current time
    };
  },
  created() {
    const username = localStorage.getItem("username") || "Guest";
    const savedFavs = localStorage.getItem(`favoriteCities_${username}`);
    if (savedFavs) {
      this.favoriteCities = JSON.parse(savedFavs);
    }
  },
  mounted() {
    this.timer = setInterval(() => {
      this.currentTime = new Date();
    }, 60000);
  },
  beforeDestroy() {
    clearInterval(this.timer);
  },
  watch: {
    favoriteCities: {
      handler(newVal) {
        const username = localStorage.getItem("username") || "Guest";
        localStorage.setItem(`favoriteCities_${username}`, JSON.stringify(newVal));
      },
      deep: true
    },
    currentView(newVal) {
      if (newVal === "trip") {
        this.fetchTripWeather();
      }
    }
  },
  computed: {
    // Display current time in the city's timezone without an extra day offset
    currentDayHeader() {
      if (this.weatherData && this.weatherData.timezone) {
        return DateTime.fromJSDate(this.currentTime)
          .setZone(this.weatherData.timezone)
          .toFormat("EEEE, MMMM d, yyyy h:mm a");
      }
      return "";
    },
    // Truncate to the start of the hour
    next25Hourly() {
      if (!this.weatherData || !this.weatherData.hourly) return [];
      const tz = this.weatherData.timezone;
      const baseTime = DateTime.now().setZone(tz).startOf("hour");
      const next25 = baseTime.plus({ hours: 25 });
      const hourly = [];
      const times = this.weatherData.hourly.time;
      const temps = this.weatherData.hourly.temperature_2m;
      for (let i = 0; i < times.length; i++) {
        const forecastDate = DateTime.fromISO(times[i], { zone: tz });
        if (forecastDate >= baseTime && forecastDate <= next25) {
          hourly.push({
            time: forecastDate.toJSDate(),
            temperature_2m: temps[i]
          });
        }
      }
      return hourly;
    },
    currentWeatherDetails() {
      if (this.weatherData && this.weatherData.hourly && this.weatherData.daily) {
        const hourly = this.weatherData.hourly;
        const daily = this.weatherData.daily;
        const temperature = hourly.temperature_2m[0];
        const humidity = hourly.relativehumidity_2m ? hourly.relativehumidity_2m[0] : "N/A";
        const wind_speed = hourly.windspeed_10m ? hourly.windspeed_10m[0] : "N/A";
        const wind_direction = hourly.winddirection_10m ? hourly.winddirection_10m[0] : "N/A";
        const weathercode = hourly.weathercode ? hourly.weathercode[0] : 0;
        const condition = this.getWeatherDescription(weathercode);
        const uv_index = daily.uv_index_max ? daily.uv_index_max[0] : "N/A";
        const sunrise = daily.sunrise ? daily.sunrise[0] : "N/A";
        const sunset = daily.sunset ? daily.sunset[0] : "N/A";
        return {
          temperature,
          humidity,
          wind_speed,
          wind_direction,
          condition,
          uv_index,
          sunrise,
          sunset
        };
      }
      return null;
    },
    filteredFavorites() {
      if (!this.favoriteSearch) return this.favoriteCities;
      return this.favoriteCities.filter(fav =>
        fav.city.toLowerCase().includes(this.favoriteSearch.toLowerCase()) ||
        fav.country.toLowerCase().includes(this.favoriteSearch.toLowerCase())
      );
    },
    tripEvents() {
      const username = localStorage.getItem("username") || "Guest";
      const key = `calendarEvents_${username}`;
      let events = [];
      const saved = localStorage.getItem(key);
      if (saved) {
        try {
          events = JSON.parse(saved).map(event => ({
            ...event,
            start: new Date(event.start),
            end: new Date(event.end)
          }));
        } catch (e) {
          console.error("Error parsing calendar events:", e);
        }
      }
      const now = new Date();
      const weekLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      return events.filter(event => event.start >= now && event.start <= weekLater);
    },
    groupedTripWeatherByDate() {
      const groups = {};
      // Group events by the date string as stored in local storage
      this.tripWeatherData.forEach(item => {
        const key = new Date(item.event.start).toLocaleDateString('en-US', { 
          weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
        });
        if (!groups[key]) {
          groups[key] = [];
        }
        groups[key].push(item);
      });
      Object.keys(groups).forEach(key => {
        groups[key].sort((a, b) => new Date(a.event.start) - new Date(b.event.start));
      });
      return groups;
    },
    sortedTripDays() {
      return Object.keys(this.groupedTripWeatherByDate)
        .sort((a, b) => new Date(a) - new Date(b));
    },
    currentTripDayKey() {
      const sorted = this.sortedTripDays;
      if (sorted.length === 0) return null;
      return sorted[this.currentTripDayIndex];
    }
  },
  methods: {
    // Adjust a date string by one hour for the trip weather (if needed)
    adjustDate(input) {
      const d = new Date(input);
      d.setHours(d.getHours() + 1);
      return d;
    },
    goToCalendar() {
      this.$router.push('/calendar');
    },
    autoCapitalize(field) {
      if (this[field]) {
        this[field] = this[field]
          .split(" ")
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(" ");
      }
    },
    async getWeather() {
      this.error = "";
      this.weatherData = null;
      if (!this.city.trim() || !this.country.trim()) {
        this.error = "Both city and country are required to search.";
        return;
      }
      this.autoCapitalize("city");
      this.autoCapitalize("country");
      this.loading = true;
      try {
        const response = await api.get("/itineraries/weather/", {
          params: { city: `${this.city}, ${this.country}` }
        });
        this.weatherData = response.data;
        this.displayCity = this.city.trim();
        this.displayCountry = this.country.trim();
      } catch (err) {
        this.error = err.response?.data?.error || "Error fetching weather. Please try again.";
      } finally {
        this.loading = false;
      }
    },
    addCity() {
      if (!this.displayCity || !this.displayCountry) {
        this.error = "Both city and country are required to add a favorite.";
        return;
      }
      const exists = this.favoriteCities.find(
        fav =>
          fav.city.toLowerCase() === this.displayCity.toLowerCase() &&
          fav.country.toLowerCase() === this.displayCountry.toLowerCase()
      );
      if (!exists) {
        let favWeather = {};
        if (this.currentWeatherDetails) {
          favWeather = {
            condition: this.currentWeatherDetails.condition,
            currentTemp: Math.round(this.currentWeatherDetails.temperature),
            high: this.weatherData.daily.temperature_2m_max[0],
            low: this.weatherData.daily.temperature_2m_min[0],
            timezone: this.weatherData.timezone
          };
        }
        this.favoriteCities.push({
          city: this.displayCity,
          country: this.displayCountry,
          ...favWeather
        });
      }
    },
    async updateFavoriteWeather(fav) {
      try {
        const response = await api.get("/itineraries/weather/", {
          params: { city: `${fav.city}, ${fav.country}` }
        });
        const data = response.data;
        if (data && data.daily && data.hourly) {
          const updatedWeather = {
            condition: this.getWeatherDescription(data.hourly.weathercode[0]),
            currentTemp: Math.round(data.hourly.temperature_2m[0]),
            high: data.daily.temperature_2m_max[0],
            low: data.daily.temperature_2m_min[0],
            timezone: data.timezone
          };
          const index = this.favoriteCities.findIndex(
            item =>
              item.city.toLowerCase() === fav.city.toLowerCase() &&
              item.country.toLowerCase() === fav.country.toLowerCase()
          );
          if (index > -1) {
            this.favoriteCities.splice(index, 1, {
              ...fav,
              ...updatedWeather
            });
          }
        }
      } catch (err) {
        console.error("Failed to update favorite city weather", err);
      }
    },
    async loadFavorite(fav) {
      await this.updateFavoriteWeather(fav);
      this.city = fav.city;
      this.country = fav.country;
      this.currentView = "city";
      this.getWeather();
    },
    removeFavorite(index) {
      this.favoriteCities.splice(index, 1);
    },
    // Format daily forecast without adding an extra day
    formatDailyDate(dateStr) {
      const dt = DateTime.fromISO(dateStr);
      return dt.toFormat("ccc, LLL d");
    },
    formatHourlyTime(dateObj) {
      if (this.weatherData && this.weatherData.timezone) {
        return DateTime.fromJSDate(dateObj)
          .setZone(this.weatherData.timezone)
          .toFormat("h:mm a");
      }
      return new Date(dateObj).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    formatSunTime(timeStr) {
      const dt = DateTime.fromISO(timeStr);
      return dt.toFormat("h:mm a");
    },
    formatDuration(start, end) {
      const diffMs = end - start;
      const diffMinutes = Math.floor(diffMs / 60000);
      const hours = Math.floor(diffMinutes / 60);
      const minutes = diffMinutes % 60;
      return `${hours}h ${minutes}m`;
    },
    getTempIcon(temp, condition) {
      // Convert condition to lowercase for easier comparison
      const cond = condition ? condition.toLowerCase() : "";
      // If condition indicates rain-related weather, return the rain emoji
      if (cond.includes("rain") || cond.includes("drizzle")) {
        return "🌧️";
      }
      // Otherwise, choose based on temperature
      if (temp < 32) return "❄️";
      else if (temp < 60) return "☁️";
      else if (temp < 75) return "⛅";
      else return "☀️";
    },
    getWindCardinal(deg) {
      if (deg === "N/A") return "";
      const directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
      const index = Math.floor((deg + 11.25) / 22.5) % 16;
      return directions[index];
    },
    getWeatherDescription(code) {
      if (code === 0) return "Clear sky";
      if ([1, 2, 3].includes(code)) return "Partly cloudy";
      if ([45, 48].includes(code)) return "Fog";
      if ([51, 53, 55].includes(code)) return "Drizzle";
      if ([56, 57].includes(code)) return "Freezing drizzle";
      if ([61, 63, 65].includes(code)) return "Rain";
      if ([66, 67].includes(code)) return "Freezing rain";
      if ([71, 73, 75].includes(code)) return "Snow fall";
      if (code === 77) return "Snow grains";
      if ([80, 81, 82].includes(code)) return "Rain showers";
      if ([85, 86].includes(code)) return "Snow showers";
      if (code === 95) return "Thunderstorm";
      if ([96, 99].includes(code)) return "Thunderstorm with hail";
      return "Unknown";
    },
    async fetchTripWeather() {
      const cachedTripWeather = localStorage.getItem("cachedTripWeather");
      if (cachedTripWeather) {
        this.tripWeatherData = JSON.parse(cachedTripWeather);
        this.tripLoading = false;
        return;
      }
      
      this.tripLoading = true;
      this.tripWeatherData = [];
      console.log("Fetching trip weather for events:", this.tripEvents);
      for (const event of this.tripEvents) {
        if (!event.city || !event.country) continue;
        console.log("Processing event:", event);
        try {
          const response = await api.get("/itineraries/weather/", {
            params: { city: `${event.city}, ${event.country}` }
          });
          const weatherData = response.data;
          const eventStart = new Date(event.start);
          const eventEnd = new Date(event.end);
          const bufferMinutes = 15;
          const eventStartBuffer = new Date(eventStart.getTime() - bufferMinutes * 60000);
          const eventEndBuffer = new Date(eventEnd.getTime() + bufferMinutes * 60000);
  
          let hourlyTemps = [];
          if (weatherData && weatherData.hourly && weatherData.hourly.time) {
            for (let i = 0; i < weatherData.hourly.time.length; i++) {
              const forecastTime = this.adjustDate(weatherData.hourly.time[i]);
              if (forecastTime >= eventStartBuffer && forecastTime <= eventEndBuffer) {
                hourlyTemps.push({
                  time: forecastTime,
                  temperature: weatherData.hourly.temperature_2m[i],
                  wind_speed: weatherData.hourly.windspeed_10m[i],
                  wind_direction: weatherData.hourly.winddirection_10m[i],
                  weathercode: weatherData.hourly.weathercode ? weatherData.hourly.weathercode[i] : 0
                });
              }
            }
          }
  
          if (hourlyTemps.length === 0 && weatherData && weatherData.hourly && weatherData.hourly.time) {
            let closestForecast = null;
            let minDiff = Infinity;
            for (let i = 0; i < weatherData.hourly.time.length; i++) {
              const forecastTime = this.adjustDate(weatherData.hourly.time[i]);
              const diff = Math.abs(forecastTime - eventStart);
              if (diff < minDiff) {
                minDiff = diff;
                closestForecast = {
                  time: forecastTime,
                  temperature: weatherData.hourly.temperature_2m[i],
                  wind_speed: weatherData.hourly.windspeed_10m[i],
                  wind_direction: weatherData.hourly.winddirection_10m[i],
                  weathercode: weatherData.hourly.weathercode ? weatherData.hourly.weathercode[i] : 0
                };
              }
            }
            if (closestForecast) {
              hourlyTemps.push(closestForecast);
            }
          }
  
          if (hourlyTemps.length > 0) {
            const temps = hourlyTemps.map(item => item.temperature);
            const minTemp = Math.min(...temps);
            const maxTemp = Math.max(...temps);
            let closestForecast = hourlyTemps[0];
            let minDiff = Math.abs(hourlyTemps[0].time - eventStart);
            for (let ft of hourlyTemps) {
              let diff = Math.abs(ft.time - eventStart);
              if (diff < minDiff) {
                minDiff = diff;
                closestForecast = ft;
              }
            }
            const condition = this.getWeatherDescription(closestForecast.weathercode);
            this.tripWeatherData.push({
              event,
              weather: {
                tempRange: { min: minTemp, max: maxTemp },
                wind_speed: closestForecast.wind_speed,
                wind_direction: closestForecast.wind_direction,
                condition: condition
              }
            });
          } else {
            this.tripWeatherData.push({
              event,
              weather: {
                tempRange: null,
                wind_speed: "N/A",
                wind_direction: "N/A",
                condition: "N/A"
              }
            });
          }
        } catch (err) {
          console.error("Error fetching weather for trip event:", err);
          this.tripWeatherData.push({
            event,
            weather: {
              tempRange: null,
              wind_speed: "N/A",
              wind_direction: "N/A",
              condition: "N/A"
            }
          });
        }
      }
      console.log("Final tripWeatherData:", this.tripWeatherData);
      localStorage.setItem("cachedTripWeather", JSON.stringify(this.tripWeatherData));
      this.currentTripDayIndex = 0;
      this.tripLoading = false;
    },
    prevDay() {
      if (this.currentTripDayIndex > 0) {
        this.currentTripDayIndex--;
        console.log("Moved to previous day. New index:", this.currentTripDayIndex, "Day:", this.currentTripDayKey);
      }
    },
    nextDay() {
      if (this.currentTripDayIndex < this.sortedTripDays.length - 1) {
        this.currentTripDayIndex++;
        console.log("Moved to next day. New index:", this.currentTripDayIndex, "Day:", this.currentTripDayKey);
      }
    }
  }
};
</script>

<style scoped>
/* Your existing styles remain unchanged */
html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  font-family: sans-serif;
  color: black;
  overflow: hidden;
  touch-action: none;
}
.layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
html.review-active,
body.review-active {
  overflow: hidden !important;
}
.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  width: 60px;
  background-color: #141414;
  color: white;
  padding: 1rem 0;
  box-sizing: border-box;
}
.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-nav li {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.sidebar-nav li.active,
.sidebar-nav li:hover {
  background-color: #333;
}
.tooltip {
  position: absolute;
  left: 70px;
  white-space: nowrap;
  background-color: #333;
  color: #fff;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
  z-index: 101;
}
.sidebar-nav li:hover .tooltip {
  opacity: 1;
}
.exit-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
.exit-door-button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.5rem;
}
.main {
  flex: 1;
  background-color: #1c1c1c;
  display: flex;
  justify-content: center;
  padding: 2rem;
  box-sizing: border-box;
  overflow: hidden;
}
.weather-container {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  width: 100%;
  text-align: center;
  color: black;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.search-container {
  background-color: #f9f9f9;
  padding: 1rem;
  border-bottom: 1px solid #ccc;
}
.weather-search {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}
.weather-search input {
  width: 1000px;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: black;
}
.search-btn {
  width: 300px;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
}
.search-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.spinner {
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 5px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.error-message {
  color: red;
  margin-top: 0.5rem;
  font-size: 1rem;
}
.current-weather {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1rem;
}
.weather-container, .output-container {
  overflow: visible;
  flex-direction: column;
}
.left-column, .right-column {
  flex: 1;
}
.left-column {
  text-align: left;
}
.left-column .location {
  font-size: 1.75rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}
.left-column .date {
  font-size: 1.25rem;
  color: black;
  margin-bottom: 0.5rem;
}
.temp-display {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}
.temp-number {
  font-size: 3rem;
  font-weight: bold;
  margin-right: 0.5rem;
}
.temp-icon {
  font-size: 2.5rem;
}
.condition {
  font-size: 1.25rem;
  margin: 0;
}
.right-column {
  text-align: right;
  font-size: 1rem;
  border-left: 1px solid #ccc;
  padding-left: 1rem;
  align-items: flex-end;
  margin-left: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: 40px;
}
.right-column p {
  margin: 0.25rem 0;
}
.add-button {
  background: none;
  font-weight: bold;
  font-size: 1.2rem;
  border: none;
  cursor: pointer;
  color: inherit;
  margin-bottom: 0.5rem;
  position: relative;
  top: -30px;
}
.sun-icon {
  width: 24px;
  height: 24px;
  vertical-align: middle;
  margin-right: 0.25rem;
}
.sunrise-icon {
  margin-top: -7px;
}
.forecast-container {
  display: flex;
  flex-direction: column;
  text-align: left;
}
.hourly-section, .daily-section {
  margin-top: 0.5rem;
}
.hourly-header, .daily-header {
  margin-bottom: 0.5rem;
  background: white;
}
.hourly-row, .daily-row {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  border-bottom: 1px solid #ccc;
}
.hourly-forecast, .daily-forecast {
  border: 1px solid #ccc;
  padding: 0.5rem;
  border-radius: 4px;
  text-align: center;
}
.hourly-forecast {
  min-width: 80px;
}
.daily-forecast {
  min-width: 140px;
}
.time, .day {
  font-weight: bold;
  margin: 0;
}
.temp {
  margin: 0;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}
.icon {
  font-size: 1.2rem;
  margin: 0.25rem 0;
}
.favorites-search-bar {
  margin-bottom: 0.5rem;
}
.favorites-search-bar input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}
.fav-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}
.fav-left {
  text-align: left;
}
.fav-right {
  text-align: right;
  position: relative;
  margin-top: 30px;
}
.trash-icon {
  position: absolute;
  top: -33px;
  right: 0;
  cursor: pointer;
  font-size: 1.2rem;
}
.fav-city {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
}
.fav-time,
.fav-condition,
.fav-temp,
.fav-high-low {
  margin: 0.25rem 0;
}
.trip-output {
  text-align: left;
}
.trip-weather-header-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
}
.trip-weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
}
.trip-weather-content {
  box-sizing: border-box;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding-top: 0.5rem;
}
.no-events {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}
.nav-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.day-info {
  flex: 1;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
}
.trip-weather-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  padding: 0.75rem;
  border-radius: 4px;
  margin: 0.5rem 0;
}
.trip-event-left, .trip-event-right {
  flex: 1;
}
.trip-event-left {
  text-align: left;
}
.trip-event-left .event-title {
  font-weight: bold;
}
.trip-event-right {
  text-align: right;
  margin-top: 25px;
}
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  padding: 1rem;
}
</style>
