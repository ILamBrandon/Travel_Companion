<template>
  <div class="step3-container">
    <!-- Sidebar for Planned Attractions -->
    <div class="planning-sidebar">
      <h4>My Attractions</h4>
      <div class="sidebar-filters">
        <input
          type="text"
          v-model="sidebarSearch"
          placeholder="Search attractions..."
          class="sidebar-search"
        />
        <!-- Category Filter -->
        <select v-model="sidebarFilter" class="sidebar-select">
          <option value="">All Categories</option>
          <option
            v-for="(cat, index) in sidebarCategories"
            :key="index"
            :value="cat"
          >
            {{ formatCategory(cat) }}
          </option>
        </select>
        <!-- Location Filter -->
        <select v-model="sidebarLocation" class="sidebar-select">
          <option value="">All Locations</option>
          <option
            v-for="(loc, index) in sidebarLocations"
            :key="index"
            :value="loc"
          >
            {{ loc }}
          </option>
        </select>
      </div>
      <!-- Scrollable container for the list only -->
      <div class="sidebar-list-container">
        <ul class="sidebar-list">
          <li
            v-for="attraction in sortedSidebarAttractions"
            :key="activityKey(attraction)"
            class="sidebar-item"
            :draggable="!isArchived(attraction)"
            @dragstart="onDragStart($event, attraction)"
          >
            <span
              class="attraction-name"
              :class="{ archived: isArchived(attraction) }"
            >
              {{ attraction.name }}
            </span>
            <button class="archive-icon" @click.stop="toggleArchived(attraction)">
              {{ isArchived(attraction) ? '✓' : 'X' }}
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Main Area: Activity Planning -->
    <div class="planning-main">
      <div class="static-header">
        <h3 class="plan-header"><strong>Plan each day of your trip</strong></h3>
        <p class="plan-instructions">
          For each event, drag an attraction into a date and fill out the information for it.
          The <em>End Time</em> will update automatically when you set the start time and duration.
        </p>
      </div>

      <!-- Day Columns -->
      <div class="day-columns-container">
        <div
          v-for="day in dayColumns"
          :key="day"
          class="day-box"
          @dragover.prevent
          @dragenter="onDragEnter(day, $event)"
          @dragleave="onDragLeave(day, $event)"
          @drop="onDrop(day, $event)"
        >
          <h4 class="day-header">
            <template v-if="day !== 'Unscheduled'">
              <div class="day-date">{{ formatDateLine(day).date }}</div>
              <div class="day-weekday">{{ formatDateLine(day).weekday }}</div>
            </template>
            <template v-else>
              Unscheduled
            </template>
          </h4>
          <!-- Drop Zone: Always show the separator; conditionally show the text message -->
          <div class="drop-zone">
            <hr class="separator" />
            <div
              v-if="plannedEventsForDay(day).length === 0 && !draggingColumns[day]"
              class="drop-message"
            >
              <p>Drag an attraction here to plan your day.</p>
            </div>
          </div>
          <!-- Planned Events for the Day -->
          <div
            v-for="plannedEvent in plannedEventsForDay(day)"
            :key="plannedEventKey(plannedEvent)"
            class="activity-planner"
            :ref="el => setActivityRef(plannedEventKey(plannedEvent), el)"
          >
            <button class="remove-event" @click="removePlannedEvent(plannedEvent)">
              🗑️
            </button>
            <h5>{{ plannedEvent.attraction.name }}</h5>
            <div class="planner-row">
              <label>Start Time:</label>
              <input
                type="time"
                v-model="planningDetails[plannedEventKey(plannedEvent)].time"
                @input="onFieldInput(plannedEvent)"
                @focus="openPicker($event)"
              />
            </div>
            <div class="planner-row duration-row">
              <label>Duration:</label>
              <div class="duration-inputs">
                <input
                  type="number"
                  min="0"
                  step="1"
                  v-model="planningDetails[plannedEventKey(plannedEvent)].durationHours"
                  placeholder="hrs"
                  @input="onFieldInput(plannedEvent)"
                />
                <span class="duration-separator">:</span>
                <input
                  type="number"
                  min="0"
                  max="59"
                  step="1"
                  v-model="planningDetails[plannedEventKey(plannedEvent)].durationMinutes"
                  placeholder="mins"
                  @input="onFieldInput(plannedEvent)"
                />
              </div>
            </div>
            <div
              class="planner-row"
              v-if="planningDetails[plannedEventKey(plannedEvent)].time"
            >
              <label>End Time:</label>
              <input
                type="time"
                :value="planningDetails[plannedEventKey(plannedEvent)].endTime || computeEndTime(plannedEvent)"
                @input="updateEndTime(plannedEvent, $event)"
                @focus="openPicker($event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, nextTick, watch } from "vue";
import Swal from "sweetalert2";

// Injected data and functions
const form = inject("form");
const addedAttractions = inject("addedAttractions");
const planningDetails = inject("planningDetails");
const activityKey = inject("activityKey");
const plannedEvents = inject("plannedEvents");

// Sidebar reactive variables
const sidebarSearch = ref("");
const sidebarFilter = ref("");
const sidebarLocation = ref("");

// Reactive list for archived attractions
const archivedAttractions = ref([]);

// Helper: Format category strings (e.g. guest_house → Guest House)
function formatCategory(category) {
  if (!category) return "";
  return category.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

// Compute unique categories and locations for sidebar filters
const sidebarCategories = computed(() => {
  const cats = addedAttractions.value.map(a => a.tourism || "Unknown");
  return Array.from(new Set(cats));
});
const computeLocation = (attraction) => {
  return attraction.city && attraction.state
    ? `${attraction.city}, ${attraction.state}`
    : attraction.city || "Unknown Location";
};
const sidebarLocations = computed(() => {
  const locs = addedAttractions.value.map(a => computeLocation(a));
  return Array.from(new Set(locs));
});

// Filter + sort sidebar attractions (archived ones at bottom)
const sortedSidebarAttractions = computed(() => {
  return addedAttractions.value
    .filter(attraction => {
      const location = computeLocation(attraction);
      const matchesSearch = attraction.name.toLowerCase().includes(sidebarSearch.value.toLowerCase());
      const matchesCategory = sidebarFilter.value
        ? attraction.tourism &&
          attraction.tourism.toLowerCase() === sidebarFilter.value.toLowerCase()
        : true;
      const matchesLocation = sidebarLocation.value
        ? location.toLowerCase() === sidebarLocation.value.toLowerCase()
        : true;
      return matchesSearch && matchesCategory && matchesLocation;
    })
    .sort((a, b) => {
      const aArchived = archivedAttractions.value.includes(activityKey(a));
      const bArchived = archivedAttractions.value.includes(activityKey(b));
      // archived => sort last
      return aArchived === bArchived ? 0 : aArchived ? 1 : -1;
    });
});

// Toggle archived status
const toggleArchived = (attraction) => {
  const key = activityKey(attraction);
  if (archivedAttractions.value.includes(key)) {
    archivedAttractions.value = archivedAttractions.value.filter(k => k !== key);
  } else {
    archivedAttractions.value.push(key);
  }
};
const isArchived = (attraction) => archivedAttractions.value.includes(activityKey(attraction));

// ------------------------------
// DRAG & DROP FOR PLANNED EVENTS
// ------------------------------
let plannedEventCounter = 0;
const plannedEventKey = (plannedEvent) => plannedEvent.id;

const onDragStart = (event, attraction) => {
  event.dataTransfer.setData("application/json", JSON.stringify(attraction));
};

const draggingColumns = ref({}); // Tracks which day columns are being dragged over

const onDragEnter = (day, event) => {
  draggingColumns.value[day] = true;
};
const onDragLeave = (day, event) => {
  draggingColumns.value[day] = false;
};
const onDrop = (day, event) => {
  draggingColumns.value[day] = false;
  dropEvent(day, event);
};

const dropEvent = (day, event) => {
  event.preventDefault();
  const attractionData = event.dataTransfer.getData("application/json");
  if (!attractionData) return;
  try {
    // Parse and deep clone the attraction data so it won't be shared
    const attraction = JSON.parse(attractionData);
    const clonedAttraction = JSON.parse(JSON.stringify(attraction));
    
    // Generate a unique id for the new planned event
    const newId = `planned_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create the new planned event
    const newEvent = { id: newId, attraction: clonedAttraction, date: day };
    plannedEvents.value.push(newEvent);
    
    // Initialize planning details for this event (deeply cloned already)
    planningDetails.value[newId] = {
      date: day,
      time: "",
      durationHours: "",
      durationMinutes: "",
      endTime: "",
      attractionName: attraction.name
    };
    
    // Set up a watcher for this event to update endTime automatically.
    watchEventDetails(newId);
  } catch (e) {
    console.error("Error parsing attraction data", e);
  }
};


const plannedEventsForDay = (day) => {
  return plannedEvents.value
    .filter(e => e.date === day)
    .sort((a, b) => {
      const timeA = planningDetails.value[a.id]?.time;
      const timeB = planningDetails.value[b.id]?.time;
      if (!timeA && !timeB) return 0;
      if (!timeA) return 1;
      if (!timeB) return -1;
      return timeA.localeCompare(timeB);
    });
};

const removePlannedEvent = (plannedEvent) => {
  // Remove from plannedEvents
  plannedEvents.value = plannedEvents.value.filter(e => e.id !== plannedEvent.id);
  // Delete its details from planningDetails
  delete planningDetails.value[plannedEvent.id];
};

// ------------------------------
// DRAG-SCROLL & INPUT HANDLERS
// ------------------------------
const activityRefs = ref({});
const setActivityRef = (key, el) => {
  if (el) activityRefs.value[key] = el;
};
const scrollToActivity = (key) => {
  if (activityRefs.value[key]) {
    activityRefs.value[key].scrollIntoView({ behavior: "smooth", block: "center" });
  }
};
const onFieldInput = (plannedEvent) => {
  // Update endTime automatically whenever time or duration fields change.
  updateEventDetails(plannedEvent);
  nextTick(() => {
    scrollToActivity(plannedEventKey(plannedEvent));
  });
};

// ------------------------------
// DATE RANGE & COLUMN GENERATION
// ------------------------------
const getDatesInRange = (start, end) => {
  const dates = [];
  let current = new Date(start);
  const endDate = new Date(end);
  while (current <= endDate) {
    dates.push(current.toISOString().split("T")[0]);
    current.setDate(current.getDate() + 1);
  }
  return dates;
};
const dayColumns = computed(() => {
  if (form.value.start && form.value.end) {
    return getDatesInRange(form.value.start, form.value.end);
  } else {
    // If no valid start/end, at least have an "Unscheduled" column:
    return ["Unscheduled"];
  }
});

// ------------------------------
// TIME HANDLERS & FORMATTERS
// ------------------------------
const formatDateLine = (dateStr) => {
  if (!dateStr) return { date: "", weekday: "" };
  const dateObj = new Date(dateStr);
  // Add one day for display purposes if desired (comment out if not needed):
  dateObj.setDate(dateObj.getDate() + 1);
  const optionsDate = { year: "numeric", month: "long", day: "numeric" };
  const optionsWeekday = { weekday: "long" };
  return {
    date: dateObj.toLocaleDateString("en-US", optionsDate),
    weekday: dateObj.toLocaleDateString("en-US", optionsWeekday)
  };
};
const openPicker = (event) => {
  if (event.target && event.target.showPicker) event.target.showPicker();
};

// Compute end time based on the event's time and duration
const computeEndTime = (plannedEvent) => {
  const key = plannedEventKey(plannedEvent);
  const details = planningDetails.value[key];
  if (
    !details ||
    !details.time ||
    details.durationHours === "" ||
    details.durationMinutes === ""
  ) {
    return "";
  }
  const [startHour, startMinute] = details.time.split(":").map(Number);
  const addHours = parseInt(details.durationHours, 10);
  const addMinutes = parseInt(details.durationMinutes, 10);
  let endHour = startHour + addHours;
  let endMinute = startMinute + addMinutes;
  if (endMinute >= 60) {
    endHour += Math.floor(endMinute / 60);
    endMinute = endMinute % 60;
  }
  const pad = n => n.toString().padStart(2, "0");
  return `${pad(endHour)}:${pad(endMinute)}`;
};

// Updates the endTime in planning details automatically based on current fields.
const updateEventDetails = (plannedEvent) => {
  const key = plannedEventKey(plannedEvent);
  const details = planningDetails.value[key];
  if (details) {
    details.endTime = computeEndTime(plannedEvent);
  }
};

// When user manually edits the end time
const updateEndTime = (plannedEvent, event) => {
  const key = plannedEventKey(plannedEvent);
  if (planningDetails.value[key]) {
    planningDetails.value[key].endTime = event.target.value;
  }
  onFieldInput(plannedEvent);
};

// ------------------------------
// WATCHERS TO AUTO-UPDATE END TIME
// ------------------------------
const watchEventDetails = (key) => {
  watch(
    () => [
      planningDetails.value[key]?.time,
      planningDetails.value[key]?.durationHours,
      planningDetails.value[key]?.durationMinutes
    ],
    () => {
      // If details was removed or doesn't exist, skip
      if (!planningDetails.value[key]) return;
      // Automatically update endTime
      planningDetails.value[key].endTime = computeEndTime({ id: key });
    }
  );
};

// ------------------------------
// HELPER FOR TIME CONVERSION & ALERTS
// ------------------------------
const convertTimeToMinutes = (timeStr) => {
  const [hours, minutes] = timeStr.split(":").map(Number);
  return hours * 60 + minutes;
};

// Sets to track already alerted overlaps, days, and cross-day events
const alertedOverlaps = ref(new Set());
const alertedDays = ref(new Set());
const alertedCrossDayEvents = ref(new Set());

watch(
  [plannedEvents, planningDetails],
  () => {
    // Overlap Detection
    const newOverlaps = new Set();

    dayColumns.value.forEach(day => {
      const events = plannedEventsForDay(day);

      for (let i = 0; i < events.length; i++) {
        const e1 = events[i];
        const details1 = planningDetails.value[e1.id];
        // If missing or incomplete, skip
        if (!details1 || !details1.time || details1.durationHours === "" || details1.durationMinutes === "") {
          continue;
        }
        const computedEnd1 = details1.endTime || computeEndTime(e1);
        if (!computedEnd1) continue;
        const start1 = convertTimeToMinutes(details1.time);
        const end1 = convertTimeToMinutes(computedEnd1);

        for (let j = i + 1; j < events.length; j++) {
          const e2 = events[j];
          const details2 = planningDetails.value[e2.id];
          if (!details2 || !details2.time || details2.durationHours === "" || details2.durationMinutes === "") {
            continue;
          }
          const computedEnd2 = details2.endTime || computeEndTime(e2);
          if (!computedEnd2) continue;

          const start2 = convertTimeToMinutes(details2.time);
          const end2 = convertTimeToMinutes(computedEnd2);

          // Overlap check
          if (start1 < end2 && start2 < end1) {
            const key = `${day}-${[e1.id, e2.id].sort().join("-")}`;
            newOverlaps.add(key);

            if (!alertedOverlaps.value.has(key)) {
              Swal.fire({
                title: "Overlap Detected!",
                html: `In ${formatDateLine(day).date}: "<span style='font-weight: bold;'>${e1.attraction.name}</span>" overlaps with "<span style='font-weight: bold;'>${e2.attraction.name}</span>".`,
                icon: "error",
                confirmButtonText: "OK"
              });
            }
          }
        }
      }
    });

    alertedOverlaps.value = newOverlaps;

    // Total Duration Detection
    dayColumns.value.forEach(day => {
      const events = plannedEventsForDay(day);
      let totalMinutes = 0;
      events.forEach(e => {
        const details = planningDetails.value[e.id];
        if (
          details &&
          details.time &&
          details.durationHours !== "" &&
          details.durationMinutes !== ""
        ) {
          totalMinutes += (parseInt(details.durationHours, 10) * 60 +
                           parseInt(details.durationMinutes, 10));
        }
      });
      if (totalMinutes >= 1440) {
        if (!alertedDays.value.has(day)) {
          Swal.fire({
            title: "Total Duration Exceeded",
            text: `The total scheduled event time for ${formatDateLine(day).date} is ${totalMinutes} minutes, exceeding 24 hours.`,
            icon: "error",
            confirmButtonText: "OK"
          });
          alertedDays.value.add(day);
        }
      } else {
        alertedDays.value.delete(day);
      }
    });

    // Cross-Day Event Detection
    dayColumns.value.forEach(day => {
      const events = plannedEventsForDay(day);
      events.forEach(e => {
        const details = planningDetails.value[e.id];
        if (
          details &&
          details.time &&
          details.durationHours !== "" &&
          details.durationMinutes !== ""
        ) {
          const startMin = convertTimeToMinutes(details.time);
          const durationMin = parseInt(details.durationHours, 10) * 60 + parseInt(details.durationMinutes, 10);
          if (startMin + durationMin >= 1440) {
            if (!alertedCrossDayEvents.value.has(e.id)) {
              Swal.fire({
                title: "Event Extends Beyond the Day",
                html: `The event "<span style='font-weight: bold;'>${e.attraction.name}</span>" scheduled on ${formatDateLine(day).date} extends into the next day.`,
                icon: "error",
                confirmButtonText: "OK"
              });
              alertedCrossDayEvents.value.add(e.id);
            }
          } else {
            alertedCrossDayEvents.value.delete(e.id);
          }
        }
      });
    });
  },
  { deep: true }
);
</script>

<style scoped>
/* Sidebar styling */
.planning-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.sidebar-filters {
  flex-shrink: 0;
}
.sidebar-list-container {
  overflow-y: auto;
  width: 100%;
  flex-grow: 1;
}
.sidebar-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}
.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: grab;
  padding: 4px 8px;
  border-bottom: 1px solid #ccc;
}
.attraction-name.archived {
  text-decoration: line-through;
  opacity: 0.6;
}
.archive-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1em;
  margin-left: 4px;
}

/* Input styling */
input[type="date"],
input[type="time"],
input[type="number"] {
  color: black;
  -webkit-text-fill-color: black;
  width: 128px;
}
.planner-row label {
  font-size: 0.97em;
}
.no-activities p,
.drop-message p {
  color: black;
  margin: 0;
  padding: 0;
}
.separator {
  border: none;
  border-top: 1px solid #000;
  margin: 0 0 8px 0;
}
.static-header .plan-header {
  margin-bottom: 4px;
}
.static-header .plan-instructions {
  margin-top: 4px;
  font-size: 15px;
}
input[type="date"]::-webkit-datetime-edit,
input[type="date"]::-webkit-datetime-edit-text,
input[type="date"]::-webkit-datetime-edit-month-field,
input[type="date"]::-webkit-datetime-edit-day-field,
input[type="date"]::-webkit-datetime-edit-year-field {
  color: black !important;
  -webkit-text-fill-color: black !important;
}

/* Main area layout */
.planning-main {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.day-columns-container {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow-x: auto;
}
.day-box {
  flex: 0 0 calc(100% / 4.8);
  border: 1px solid #ccc;
  padding: 8px;
  box-sizing: border-box;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}
.day-header {
  text-align: center;
  margin-bottom: 8px;
  color: black;
}
.day-date,
.day-weekday {
  color: black;
}
.drop-zone {
  margin-bottom: 8px;
}
.activity-planner {
  position: relative;
  border: 1px solid #ddd;
  padding: 4px;
  margin-bottom: 8px;
  background: #f9f9f9;
  width: 100%;
  box-sizing: border-box;
}
  
.remove-event {
  position: absolute;
  top: 2px;
  right: 2px;
  padding: 2px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2em;
}

.activity-planner h5 {
  margin-right: 18px; /* adjust as needed */
}

.duration-inputs {
  display: inline-flex;
  align-items: center;
}
.duration-inputs input {
  width: 50px;
  padding: 2px;
}
.duration-separator {
  margin: 0 4px;
}
</style>