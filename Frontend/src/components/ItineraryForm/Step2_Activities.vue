<template>
  <div class="step2-container">
    <!-- Sidebar: Radius Finder & Added Activities -->
    <div class="radius-sidebar">
      <div class="radius-header" @click="isRadiusCollapsed = !isRadiusCollapsed">
        <span class="radius-title">Nearby Cities</span>
        <span class="collapse-icon">{{ isRadiusCollapsed ? '+' : '-' }}</span>
      </div>
      <div v-if="!isRadiusCollapsed">
        <div class="radius-filters">
          <div class="radius-control">
            <label for="radius">Radius (miles):</label>
            <span class="radius-value">{{ radius }}</span>
            <input
              type="range"
              id="radius"
              min="5"
              max="100"
              step="5"
              v-model="radius"
              @input="debouncedUpdateNearbyCities"
            />
          </div>
          <div class="radius-sort">
            <label for="sortRadius">Sort by distance:</label>
            <select id="sortRadius" v-model="sortRadius">
              <option value="asc">Low to High</option>
              <option value="desc">High to Low</option>
            </select>
          </div>
        </div>
        <hr class="radius-divider" />
        <ul class="radius-list" ref="radiusListRef">
          <li
            v-for="(city, index) in sortedNearbyCities"
            :key="city.osm_id || index"
            class="nearby-city-item"
          >
            {{ city.name }} ({{ city.computedDistance.toFixed(2) }} miles)
          </li>
        </ul>
      </div>
      <div
        class="added-attractions-header"
        @click="isAddedAttractionsCollapsed = !isAddedAttractionsCollapsed"
        :class="{ 'no-border': isRadiusCollapsed }"
      >
        <span class="added-title">Added Activities</span>
        <span class="collapse-icon">{{ isAddedAttractionsCollapsed ? '+' : '-' }}</span>
      </div>
      <ul
        v-if="!isAddedAttractionsCollapsed"
        :class="['added-attractions-list', { 'nearby-collapsed': isRadiusCollapsed }]"
      >
        <template v-for="(categories, location) in groupedAddedAttractions" :key="location">
          <li class="location-header">{{ location }}</li>
          <template v-for="(attractionsList, category) in categories" :key="category">
            <li class="category-header">{{ formatCategory(category) }}</li>
            <ul>
              <li
                v-for="(attraction, index) in attractionsList"
                :key="attraction.osm_id || index"
                class="added-attraction-item"
              >
                {{ attraction.name }}
                <button class="remove-btn" @click.stop="toggleAttraction(attraction)">
                  -
                </button>
              </li>
            </ul>
          </template>
        </template>
      </ul>
    </div>

    <!-- Main Area: Attraction Search & Results -->
    <div class="search-main">
      <div class="search-controls">
        <div class="search-row">
          <!-- City and Country fields -->
          <div class="form-group inline">
            <label for="citySearch">Search City</label>
            <input id="citySearch" v-model="searchCity" type="text" placeholder="Enter city (required)" />
          </div>
          <div class="form-group inline">
            <label for="countrySearch">Search Country</label>
            <input id="countrySearch" v-model="filters.country" type="text" placeholder="Enter country (required)" />
          </div>
          <!-- Updated Search Button with Loading State -->
          <button type="button" class="search-button" @click="fetchAttractions" :disabled="isSearching">
            <span v-if="isSearching">Searching...</span>
            <span v-else>Search Activity</span>
          </button>
          <button type="button" class="toggle-advanced" @click="showAdvanced = !showAdvanced">
            {{ showAdvanced ? "Hide Advanced" : "Show Advanced" }}
          </button>
        </div>
        <!-- Advanced Filters -->
        <div class="advanced-filters" v-if="showAdvanced">
          <div class="form-group inline">
            <label for="stateFilter">State/Province/Region</label>
            <input id="stateFilter" v-model="filters.state" type="text" placeholder="State/Province/Region" />
          </div>
          <div class="form-group inline">
            <label for="keywordFilter">Keyword</label>
            <input id="keywordFilter" v-model="filters.keyword" type="text" placeholder="Local filter keyword" />
          </div>
          <div class="form-group inline">
            <label for="filter">Category</label>
            <select id="filter" v-model="filters.category">
              <option value="">All Categories</option>
              <option 
                v-for="category in filteredCategories" 
                :key="category" 
                :value="category.toLowerCase()">
                {{ formatCategory(category) }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <!-- Error Message -->
      <div v-if="attractionsError" class="error-message">
        {{ attractionsError }}
      </div>
      <!-- Results Wrapper -->
      <div class="attractions-table-header">
          <span class="attraction-activity">Activity</span>
          <span class="attraction-location">Location</span>
          <span class="attraction-category">Category</span>
          <span class="attraction-add">Add/Remove</span>
        </div>
        <div class="results-wrapper" :class="{ 'scroll-enabled': attractionsError }">
        <div class="results-container" :class="{ 'advanced-active': showAdvanced }">
          <div class="results" ref="resultsContainer">
            <ul>
              <li
                v-for="(attraction, index) in paginatedAttractions"
                :key="attraction.osm_id || index"
                class="attraction-item"
              >
                <span class="attraction-activity">
                  {{ attraction.name }}
                </span>
                <span class="attraction-location">
                  {{
                    [attraction.city, attraction.state, attraction.country]
                      .filter(Boolean)
                      .join(", ") || "N/A"
                  }}
                </span>
                <span class="attraction-category">
                  {{ attraction.tourism ? formatCategory(attraction.tourism) : 'Unknown' }}
                </span>
                <span class="attraction-add">
                  <button
                    :class="isAttractionAdded(attraction) ? 'remove-btn' : 'add-btn'"
                    @click="toggleAttraction(attraction)"
                  >
                    {{ isAttractionAdded(attraction) ? '-' : '+' }}
                  </button>
                </span>
              </li>
            </ul>
          </div>
        </div>
        <!-- Pagination Controls -->
        <div class="pagination-controls">
          <button v-if="currentPage > 1" @click="currentPage = currentPage - 1">&lt;</button>
          <button
            v-for="page in visiblePages"
            :key="page"
            :class="{ active: currentPage === page }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
          <button v-if="currentPage < totalPages" @click="currentPage = currentPage + 1">
            &gt;
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";
import debounce from "lodash/debounce";

// Ensure tokens are loaded on component mount.
const authStore = useAuthStore();
onMounted(() => {
  authStore.loadTokens();
});

// Shared state and functions (assumed to include authentication in your API client)
const form = inject("form");
const addedAttractions = inject("addedAttractions");
const toggleAttraction = inject("toggleAttraction");

// --- LOCAL STATE FOR SEARCH ---
const searchCity = ref("");
const attractions = ref([]);
const attractionsError = ref("");
const filters = ref({
  keyword: "",
  category: "",
  sortBy: "",
  state: "",
  country: ""
});
const showAdvanced = ref(false);

// Reactive variable to indicate a search is in progress
const isSearching = ref(false);

// --- Advanced Filters: Categories ---
const allCategories = [
  "Attraction",
  "Restaurant",
  "Museum",
  "Gallery",
  "Zoo",
  "Theme_Park",
  "Viewpoint",
  "Aquarium",
  "Information",
  "Artwork",
  "Camp_Site",
  "Caravan_Site",
  "Guest_House",
  "Hostel",
  "Motel",
  "Picnic_Site",
  "Hotel"
];

const categorySearch = ref("");
const filteredCategories = computed(() => {
  if (!categorySearch.value.trim()) {
    return allCategories;
  }
  return allCategories.filter(category =>
    category.toLowerCase().includes(categorySearch.value.trim().toLowerCase())
  );
});

// --- PAGINATION STATE ---
const currentPage = ref(1);
const pageSize = ref(11);
const filteredAttractions = computed(() => {
  let result = attractions.value;
  if (filters.value.keyword.trim()) {
    result = result.filter(a =>
      a.name.toLowerCase().includes(filters.value.keyword.toLowerCase())
    );
  }
  if (filters.value.category) {
    if (filters.value.category.toLowerCase() === "other") {
      result = result.filter(a => !a.tourism);
    } else {
      result = result.filter(
        a =>
          a.tourism &&
          a.tourism.toLowerCase() === filters.value.category.toLowerCase()
      );
    }
  }
  return result;
});
const paginatedAttractions = computed(() => {
  const startIdx = (currentPage.value - 1) * pageSize.value;
  return filteredAttractions.value.slice(startIdx, startIdx + pageSize.value);
});
const totalPages = computed(() =>
  Math.ceil(filteredAttractions.value.length / pageSize.value)
);
const visiblePages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const maxVisible = 5;
  let start = Math.max(1, current - Math.floor(maxVisible / 2));
  let end = start + maxVisible - 1;
  if (end > total) {
    end = total;
    start = Math.max(1, end - maxVisible + 1);
  }
  const pages = [];
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
});

// Reset pagination when filters change
watch(
  () => filters.value.keyword,
  () => {
    currentPage.value = 1;
  }
);
watch(
  () => filters.value.category,
  () => {
    currentPage.value = 1;
  }
);

// --- NEARBY CITIES STATE ---
const radius = ref(15);
const nearbyCities = ref([]);
const inputCityCoords = ref({ lat: null, lon: null });
const isRadiusCollapsed = ref(false);
const isAddedAttractionsCollapsed = ref(false);
const sortRadius = ref("asc");

const sortedNearbyCities = computed(() => {
  return nearbyCities.value
    .filter(city => city.computedDistance > 0)
    .sort((a, b) =>
      sortRadius.value === "asc"
        ? a.computedDistance - b.computedDistance
        : b.computedDistance - a.computedDistance
    );
});

// --- HELPER FUNCTION TO FORMAT CATEGORY ---
function formatCategory(category) {
  if (!category) return "";
  return category
    .replace(/_/g, " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}

// --- FUNCTIONS ---
function getDistance(lat1, lon1, lat2, lon2) {
  const toRad = (value) => (value * Math.PI) / 180;
  const R = 3958.8; // Radius of Earth in miles
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

const fetchCityCoordinates = async () => {
  if (!form.value.city.trim()) return;
  try {
    const url = "https://nominatim.openstreetmap.org/search";
    const params = { q: form.value.city, format: "json", limit: 1 };
    const response = await fetch(`${url}?${new URLSearchParams(params)}`);
    const data = await response.json();
    if (data && data.length > 0) {
      inputCityCoords.value = {
        lat: parseFloat(data[0].lat),
        lon: parseFloat(data[0].lon)
      };
    }
  } catch (error) {
    console.error("Error fetching city coordinates:", error);
  }
};

const fetchAttractions = async () => {
  // Require both city and country before searching
  if (!searchCity.value.trim() || !filters.value.country.trim()) {
    attractionsError.value = "Please enter both city and country to search.";
    return;
  }
  
  attractionsError.value = "";
  attractions.value = [];
  currentPage.value = 1;
  isSearching.value = true; // Start the search animation
  try {
    let params = {};
    params.city = searchCity.value.trim();
    params.state = filters.value.state;
    params.country = filters.value.country;
    params.category = filters.value.category;
    params.sortBy = filters.value.sortBy;
    const response = await api.get("itineraries/attractions/", { params });
    attractions.value = response.data;
  } catch (error) {
    attractionsError.value =
      error.response?.data?.error || "Failed to fetch attractions.";
  } finally {
    isSearching.value = false; // End the search animation
  }
};

const fetchNearbyCities = async () => {
  try {
    const params = { city: form.value.city, radius: radius.value };
    const response = await api.get("itineraries/nearby-cities/", { params });
    nearbyCities.value = response.data;
    if (inputCityCoords.value.lat && inputCityCoords.value.lon) {
      nearbyCities.value = nearbyCities.value.map(city => {
        const dist = getDistance(
          inputCityCoords.value.lat,
          inputCityCoords.value.lon,
          parseFloat(city.lat),
          parseFloat(city.lon)
        );
        return { ...city, computedDistance: dist };
      });
    } else {
      nearbyCities.value = nearbyCities.value.map(city => ({
        ...city,
        computedDistance: radius.value
      }));
    }
  } catch (error) {
    nearbyCities.value = [];
  }
};

const updateNearbyCities = async () => {
  await fetchCityCoordinates();
  await fetchNearbyCities();
};

const debouncedUpdateNearbyCities = debounce(() => {
  updateNearbyCities();
}, 300);

watch(() => form.value.city, (newCity) => {
  if (newCity.trim() !== "") {
    fetchCityCoordinates();
    fetchNearbyCities();
  }
});

// --- ATTRACTION ADD/REMOVE ---
function isAttractionAdded(attraction) {
  return addedAttractions.value.some(
    a => a.osm_id === attraction.osm_id || a.name === attraction.name
  );
}

// --- GROUP ADDED ATTRACTIONS BY LOCATION AND CATEGORY ---
const groupedAddedAttractions = computed(() => {
  const groups = {};
  addedAttractions.value.forEach(attraction => {
    const location =
      attraction.city && attraction.state
        ? `${attraction.city}, ${attraction.state}`
        : (attraction.city || "Unknown Location");
    const category = attraction.tourism || "Other";
    if (!groups[location]) {
      groups[location] = {};
    }
    if (!groups[location][category]) {
      groups[location][category] = [];
    }
    groups[location][category].push(attraction);
  });
  return groups;
});
</script>

<style scoped>
.step2-container {
  display: flex;
  gap: 1rem;
  height: calc(100vh - 250px);
  flex-wrap: nowrap;
}

/* Sidebar */
.radius-sidebar {
  flex: 0 0 300px;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}
.radius-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #000;
  font-size: 0.9rem;
  border-bottom: 1px solid #ccc;
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  cursor: pointer;
}
.radius-header .radius-title {
  font-weight: bold;
}
.radius-header .collapse-icon {
  font-size: 0.95rem;
}
.radius-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}
.radius-control,
.radius-sort {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.radius-control label,
.radius-sort label,
.radius-control .radius-value,
.radius-sort select {
  color: #000;
  font-size: 0.9rem;
}
.radius-divider {
  border: none;
  border-top: 1px solid #ccc;
  margin: 0.25rem 0;
}
.radius-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  max-height: 200px;
}
.nearby-city-item {
  color: #000;
  padding: 0.25rem 0;
}

/* Added Activities Section */
.added-attractions-header {
  font-weight: bold;
  margin-top: 0;
  border-top: 1px solid #ccc;
  padding: 0.125rem 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: #000;
}
.added-attractions-header.no-border {
  border-top: none;
  transform: translateY(-8px);
}
.added-attractions-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 0;
  transition: margin-top 0.3s ease;
  border-top: 1px solid #ccc;
  padding-top: 0.0625rem;
}
.added-attractions-list.nearby-collapsed {
  padding-top: 0.03125rem;
  margin-top: -8px;
}
.location-header {
  margin-top: 0;
  padding: 0.125rem 0;
  text-decoration: underline;
  color: #000;
}
.category-header {
  margin-left: 1rem;
  margin-top: 0;
  font-style: italic;
  color: #333;
}
.category-header + ul {
  margin-left: 1rem;
  padding-left: 1rem;
}
.added-attraction-item {
  padding: 0.0625rem 0;
}

/* Main Search Area */
.search-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  padding-right: 1rem;
}
.search-controls {
  padding: 0.5rem;
  flex: none;
}
.search-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.form-group.inline {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 0 !important;
}
.form-group.inline label {
  margin-bottom: 0.25rem;
  color: #000;
}
.required {
  color: red;
}
.toggle-advanced,
.search-button {
  padding: 0.5rem 1rem;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease;
  width: 150px;
}
.toggle-advanced:hover,
.search-button:hover {
  background-color: #34495e;
}
.advanced-filters {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
  overflow-y: auto;
  max-height: 150px;
  padding-bottom: 0.5rem;
  flex: none;
}

.results-wrapper.scroll-enabled {
  max-height: 315px; /* adjust this value as needed */
  overflow-y: auto;
}

/* Results Wrapper */
.results-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.error-message[data-v-abfe909a] ~ .results-wrapper .results-container.advanced-active[data-v-abfe909a] {
  height: 233px; /* Adjust this value as needed */
  overflow: hidden;
}

.attractions-table-header {
  display: flex;
  font-weight: bold;
  padding: 0.7rem 0 0.2rem 0;
  border-bottom: 1px solid #ccc;
  color: #000;
  background: #fff;
  flex: none;
}
.attraction-activity {
  flex: 2;
  overflow-x: auto;
  white-space: nowrap;
  margin-right: 10px;
}
.attraction-location {
  flex: 2;
  overflow-x: auto;
  white-space: nowrap;
  padding-left: 10px;
}
.attraction-category {
  flex: 1;
}
.attraction-add {
  flex: 1;
  text-align: center;
}
.results-container {
  position: relative;
}
.results-container.advanced-active {
  height: 275px;
}
.results {
  overflow-y: auto;
  height: 100%;
}

/* Pagination Controls */
.pagination-controls {
  flex: none;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.5rem 0;
}
.pagination-controls button {
  padding: 0.5rem 0.75rem;
  border: 1px solid #2c3e50;
  background: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease;
  color: #000;
}
.pagination-controls button.active,
.pagination-controls button:hover {
  background: #2c3e50;
  color: #fff;
}

.error-message {
  color: red;
  margin: 0.5rem 0;
}

/* Disabled button style */
.search-button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>