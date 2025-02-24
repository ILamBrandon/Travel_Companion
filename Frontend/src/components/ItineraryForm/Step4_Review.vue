<template>
  <div class="review-container">
    <!-- Big header at the top -->
    <h1 class="main-header">Itinerary Review</h1>

    <!-- Step 1: Itinerary Details -->
    <div class="step-box" id="step1" v-if="form">
      <h2>Step 1: Itinerary Info Details</h2>
      <hr class="separator" />
      <p><strong class="field-label">Title:</strong> {{ form.title }}</p>
      <p><strong class="field-label">City:</strong> {{ form.city }}</p>
      <p><strong class="field-label">State:</strong> {{ form.state }}</p>
      <p><strong class="field-label">Country:</strong> {{ form.country }}</p>
      <p><strong class="field-label">Start Date:</strong> {{ form.start }}</p>
      <p><strong class="field-label">End Date:</strong> {{ form.end }}</p>
      <p>
        <strong class="field-label">Reason:</strong>
        {{ form.reason === 'other' ? form.otherReason : form.reason }}
      </p>
    </div>

    <!-- Step 2: City Summary -->
    <div class="step-box" id="step2">
      <h2>Step 2: Attractions Summary</h2>
      <hr class="separator" />
      <div v-if="Object.keys(citySummary).length">
        <div
          v-for="(categories, city) in citySummary"
          :key="city"
          class="city-summary"
        >
          <p class="city-name">
            <strong class="field-label underline">City: </strong>
            <strong class="field-label underline">{{ city }}</strong>
          </p>
          <ul class="bullet-list">
            <li v-for="(count, category) in categories" :key="category">
              <strong class="field-label">{{ formatCategory(category) }}:</strong> {{ count }}
            </li>
          </ul>
        </div>
      </div>
      <p v-else>No attractions selected.</p>
    </div>

    <!-- Step 3: Planned Activities – Timeline view -->
    <div class="step-box" id="step3">
      <h2>Step 3: Planned Activities</h2>
      <hr class="separator" />

      <!-- Instruction for small event boxes -->
      <p class="instruction">
        If an event box is too small due to its short duration, you can click on it to view the full details. If not you can scroll to see the details.
      </p>

      <!-- Show timeline only if there is at least one planned event -->
      <div v-if="hasPlannedEvents">
        <!-- Timeline Header: Displays the day columns on top with navigation arrows -->
        <div class="timeline-header">
          <!-- Left navigation arrow -->
          <div class="nav-arrow left-arrow" @click="scrollLeft">&lt;</div>
          
          <!-- Time header (empty block for alignment) -->
          <div class="time-header"></div>
          
          <!-- Day headers (only the visible days in the current page) -->
          <div class="day-headers">
            <div
              v-for="day in visibleDays"
              :key="day"
              class="day-header-cell"
            >
              {{ formatDate(day) }}
            </div>
          </div>
          
          <!-- Right navigation arrow -->
          <div class="nav-arrow right-arrow" @click="scrollRight">&gt;</div>
        </div>

        <!-- Timeline Container: Left time scale and day columns -->
        <div class="timeline-container">
          <!-- Left-side time scale -->
          <div class="time-scale">
            <div
              v-for="time in timeSlots"
              :key="time"
              class="time-slot"
            >
              {{ time }}
            </div>
          </div>
          <!-- Day columns (one per visible day) -->
          <div class="day-columns">
            <div
              v-for="day in visibleDays"
              :key="day"
              class="day-column"
            >
              <!-- Container for events for each day -->
              <div class="events-container">
                <div
                  v-for="event in eventsByDay(day)"
                  :key="event.id"
                  class="planned-event"
                  :style="getEventStyle(event)"
                  @click="selectEvent(event)"
                >
                  <div class="event-name">
                    <strong>{{ event.attractionName || 'Unnamed Attraction' }}</strong>
                  </div>
                  <div class="event-time">
                    <strong>Start Time:</strong> {{ formatTime(event.time) }}
                  </div>
                  <div class="event-duration">
                    <strong>Duration:</strong> {{ event.durationHours }} hrs {{ event.durationMinutes }} mins
                  </div>
                  <div class="event-end">
                    <strong>End Time:</strong> {{ computeEndTime(event) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <p v-else>No planned activities.</p>
    </div>

    <!-- Modal for Event Details -->
    <div v-if="selectedEvent" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">&times;</button>
        <h3>{{ selectedEvent.attractionName || 'Unnamed Attraction' }}</h3>
        <p><strong>Start Time:</strong> {{ formatTime(selectedEvent.time) }}</p>
        <p><strong>Duration:</strong> {{ selectedEvent.durationHours }} hrs {{ selectedEvent.durationMinutes }} mins</p>
        <p><strong>End Time:</strong> {{ computeEndTime(selectedEvent) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed } from "vue";

// --- Injections and Data Setup ---
const form = inject("form");
const injectedAttractions = inject("addedAttractions") || [];
const planningDetails = inject("planningDetails") || {};
const activityKey = inject("activityKey") || ((activity) => activity.id);

const formatCategory = (category) => category.replace(/_/g, ' ');

const attractionsList = computed(() => {
  return injectedAttractions && injectedAttractions.value
    ? injectedAttractions.value
    : injectedAttractions;
});

// Compute City Summary for Step 2
const citySummary = computed(() => {
  const summary = {};
  const attractions = attractionsList.value;
  if (Array.isArray(attractions)) {
    attractions.forEach((activity) => {
      const city = activity.city || (form && form.city) || "Unknown";
      if (!summary[city]) {
        summary[city] = {};
      }
      const category = activity.category || activity.tourism || "Other";
      summary[city][category] = (summary[city][category] || 0) + 1;
    });
  }
  return summary;
});

// --- STEP 3: Timeline for Planned Activities ---
// We assume planned events in planningDetails have keys starting with "planned_"
const hasPlannedEvents = computed(() => {
  return Object.keys(planningDetails.value).some((key) => key.startsWith("planned_"));
});

// Helper: parse a YYYY-MM-DD string into a Date object
const parseLocalDate = (dateStr) => {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(year, month - 1, day);
};

// Utility: Get dates between two dates (inclusive)
const getDatesInRange = (start, end) => {
  const dates = [];
  let current = parseLocalDate(start);
  const endDate = parseLocalDate(end);
  while (current <= endDate) {
    const year = current.getFullYear();
    const month = String(current.getMonth() + 1).padStart(2, "0");
    const day = String(current.getDate()).padStart(2, "0");
    dates.push(`${year}-${month}-${day}`);
    current.setDate(current.getDate() + 1);
  }
  return dates;
};

// Format date string into a short header (e.g., "Mon, Aug 12")
const formatDate = (dateStr) => {
  const dateObj = parseLocalDate(dateStr);
  return dateObj.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
};

// Compute day columns from itinerary dates
const dayColumns = computed(() => {
  if (form && form.value.start && form.value.end) {
    return getDatesInRange(form.value.start, form.value.end);
  } else {
    return [];
  }
});

// --- Paging Setup ---
// Show 4 days per page
const currentPage = ref(0);
const pageSize = 4;
const totalPages = computed(() => Math.ceil(dayColumns.value.length / pageSize));
const visibleDays = computed(() =>
  dayColumns.value.slice(currentPage.value * pageSize, (currentPage.value + 1) * pageSize)
);

const scrollLeft = () => {
  if (currentPage.value > 0) currentPage.value--;
};
const scrollRight = () => {
  if (currentPage.value < totalPages.value - 1) currentPage.value++;
};

// --- Time Slots in 12‑hour Format ---
// Create an array of time labels (formatted in 12‑hour clock with am/pm)
const timeSlots = computed(() => {
  const slots = [];
  for (let h = 0; h < 24; h++) {
    const period = h < 12 ? "am" : "pm";
    let hour12 = h % 12;
    if (hour12 === 0) hour12 = 12;
    slots.push(`${hour12} ${period}`);
  }
  return slots;
});

// --- Format Time Helper ---
// Converts a 24‑hour time string (e.g., "04:18") to a 12‑hour format with am/pm.
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  let [hour, minute] = timeStr.split(":").map(Number);
  const period = hour < 12 ? "am" : "pm";
  let hour12 = hour % 12;
  if (hour12 === 0) hour12 = 12;
  return `${hour12}:${minute.toString().padStart(2, "0")} ${period}`;
};

// --- Compute End Time ---
// Calculates the end time by adding the duration to the start time.
const computeEndTime = (event) => {
  if (!event.time) return '';
  let [startHour, startMinute] = event.time.split(":").map(Number);
  const durationHours = parseInt(event.durationHours, 10) || 0;
  const durationMinutes = parseInt(event.durationMinutes, 10) || 0;
  let endHour = startHour + durationHours;
  let endMinute = startMinute + durationMinutes;
  if (endMinute >= 60) {
    endHour += Math.floor(endMinute / 60);
    endMinute = endMinute % 60;
  }
  // Wrap around if endHour exceeds 24
  endHour = endHour % 24;
  const period = endHour < 12 ? "am" : "pm";
  let hour12 = endHour % 12;
  if (hour12 === 0) hour12 = 12;
  return `${hour12}:${endMinute.toString().padStart(2, "0")} ${period}`;
};

// Return all planned events for a given day (from planningDetails keys starting with "planned_")
const eventsByDay = (day) => {
  const events = [];
  Object.keys(planningDetails.value).forEach((key) => {
    if (key.startsWith("planned_")) {
      const event = planningDetails.value[key];
      if (event.date === day) {
        events.push({ id: key, ...event });
      }
    }
  });
  return events;
};

// --- Get Event Style ---
// Position event based on its start time (in minutes from midnight) and duration
const getEventStyle = (event) => {
  if (!event.time) return {};
  const [startHour, startMinute] = event.time.split(":").map(Number);
  const startTotalMinutes = startHour * 60 + startMinute;
  const durationHours = parseInt(event.durationHours, 10) || 0;
  const durationMinutes = parseInt(event.durationMinutes, 10) || 0;
  const totalDuration = durationHours * 60 + durationMinutes;
  return {
    position: "absolute",
    top: `${startTotalMinutes}px`,
    height: `${totalDuration}px`,
    left: "0",
    right: "0",
    overflow: "hidden",
    background: "#d3d3d3",
    border: "1px solid #008000",
    borderRadius: "4px",
    padding: "4px",
    fontSize: "0.8rem",
    boxSizing: "border-box",
    wordWrap: "break-word",
    cursor: "pointer"
  };
};

// --- Modal Handling ---
const selectedEvent = ref(null);
const selectEvent = (event) => {
  selectedEvent.value = event;
};
const closeModal = () => {
  selectedEvent.value = null;
};
</script>

<style scoped>
/* Main header styling */
.main-header {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
}

/* Container styling */
.review-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #000;
  padding: 30px;
  background-color: #f0f2f5;
  min-height: 100vh;
}

/* Step box styling */
.step-box {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 25px;
  margin-bottom: 25px;
}
.step-box h2 {
  font-size: 1.75rem;
  margin-bottom: 8px;
}
.separator {
  border: none;
  border-bottom: 1px solid #000;
  margin: 5px 0;
}

/* Label styling */
.field-label {
  font-weight: bold;
}
.underline {
  text-decoration: underline;
}

/* Instruction text styling for Step 3 */
.instruction {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 10px;
}

/* ----------------------------- */
/* Timeline Header & Container   */
/* ----------------------------- */

/* Timeline header */
.timeline-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  position: relative;
}

/* Navigation arrow styling */
.nav-arrow {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  z-index: 10;
}
.left-arrow {
  left: 0;
}
.right-arrow {
  right: 0;
}

/* Time header (for alignment) */
.time-header {
  width: 60px;
}

/* Day headers container */
.day-headers {
  display: flex;
  flex: 1;
}
.day-header-cell {
  flex: 1;
  text-align: center;
  font-weight: bold;
  border-right: 1px solid #ccc;
  padding: 5px;
}
.day-header-cell:last-child {
  border-right: none;
}

/* Timeline container */
.timeline-container {
  display: flex;
  border: 1px solid #ddd;
  overflow: hidden;
}

/* Time scale column */
.time-scale {
  width: 60px;
  border-right: 1px solid #ccc;
  display: flex;
  flex-direction: column;
  height: 1440px;
}
.time-slot {
  height: 60px;
  border-bottom: 1px solid #eee;
  text-align: center;
  font-size: 0.8rem;
  line-height: 60px;
}

/* Day columns */
.day-columns {
  display: flex;
  flex: 1;
}
.day-column {
  flex: 1;
  border-right: 1px solid #ccc;
  position: relative;
  height: 1440px;
}
.day-column:last-child {
  border-right: none;
}

/* Events container */
.events-container {
  position: relative;
  height: 100%;
  overflow-y: auto;
  padding: 5px;
}

.planned-event {
  overflow: auto !important;
}

/* Additional text styling */
.event-name {
  font-weight: bold;
  margin-bottom: 4px;
}
.event-time,
.event-end,
.event-duration {
  font-size: 0.75rem;
  margin-bottom: 2px;
}

/* ----------------------------- */
/* Modal Styling                 */
/* ----------------------------- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 10px;
  right: 15px;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
</style>
