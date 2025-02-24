<template>
  <div :class="['itinerary-form', { 'full-scroll': isReviewStep }]">
    <!-- Close Button: Clicking this returns to the calendar -->
    <button class="close-button" @click="goBackToCalendar">X</button>

    <FormWizard
      ref="wizardRef"
      :nextButtonText="'Next'"
      :backButtonText="'Back'"
      @on-change="handleTabChange"
      @on-complete="handleSubmit"
    >
      <!-- STEP 1 with before-change validation -->
      <TabContent title="Itinerary Info" :before-change="validateStep1">
        <Step1ItineraryInfo />
      </TabContent>

      <!-- STEP 2 with before-change validation -->
      <TabContent title="Attractions" :before-change="validateStep2">
        <Step2Attractions />
      </TabContent>

      <!-- STEP 3 with before-change validation -->
      <TabContent title="Plan Activities" :before-change="validateStep3">
        <Step3PlanActivities />
      </TabContent>

      <!-- STEP 4 -->
      <TabContent title="Review & Submit">
        <Step4Review />
      </TabContent>

      <!-- Navigation slot: Always fixed to the bottom left/right of the viewport -->
      <template #navigation>
        <div class="wizard-nav">
          <button
            v-if="wizardRef.value && wizardRef.value.currentStep > 0"
            type="button"
            @click="wizardRef.value.prevStep()"
          >
            Back
          </button>
          <button
            v-if="wizardRef.value && wizardRef.value.currentStep < 4"
            type="button"
            @click="wizardRef.value.nextStep()"
          >
            Next
          </button>
        </div>
      </template>
    </FormWizard>
  </div>
</template>

<script setup>
import { ref, computed, provide, watch, onMounted, nextTick } from "vue";
import { FormWizard, TabContent } from "vue3-form-wizard";
import "vue3-form-wizard/dist/style.css";
import Swal from "sweetalert2";
import { useRouter } from "vue-router";
import api from "@/services/api";

// Import the step components
import Step1ItineraryInfo from "./Step1_ItineraryInfo.vue";
import Step2Attractions from "./Step2_Activities.vue";
import Step3PlanActivities from "./Step3_PlanActivities.vue";
import Step4Review from "./Step4_Review.vue";

// --- ROUTER FOR THE CLOSE BUTTON ---
const router = useRouter();
const goBackToCalendar = () => {
  router.push("/calendar");
};

// --- SHARED STATE ---
/**
 * Our main form data object.
 * If we detect an existing itinerary from localStorage (`editItinerary`),
 * we'll overwrite these default values on mount.
 */
const form = ref({
  title: "",
  city: "",
  state: "",
  country: "",
  start: "",
  end: "",
  reason: "",
  otherReason: ""
});

const addedAttractions = ref([]);
const planningDetails = ref({});
const plannedEvents = ref([]); // Shared state

// A helper function to generate a unique key for each attraction
const activityKey = (attraction) => attraction.osm_id || attraction.name;

// --- MOUNTED: Check for "editItinerary" to preload data ---
onMounted(() => {
  const editData = localStorage.getItem("editItinerary");
  if (editData) {
    try {
      const itinerary = JSON.parse(editData);
      // Pre-fill basic fields
      form.value.id = itinerary.id;
      form.value.title = itinerary.title || "";
      form.value.city = itinerary.city || "";
      form.value.state = itinerary.state || "";
      form.value.country = itinerary.country || "";
      form.value.start = itinerary.start_date || "";
      form.value.end = itinerary.end_date || "";

      // If simpler, direct assignment is fine:
      form.value.reason = itinerary.reason || "";
      // (If the itinerary used "otherReason" originally, set it too if needed)
      if (itinerary.reason === "other" && itinerary.otherReason) {
        form.value.otherReason = itinerary.otherReason;
      }

      // Populate existing attractions
      if (itinerary.addedAttractions) {
        addedAttractions.value = itinerary.addedAttractions;
      }

      // Populate planning details
      if (itinerary.planningDetails) {
        planningDetails.value = itinerary.planningDetails;
      }
      
      // Rehydrate plannedEvents if saved in itinerary payload
      if (itinerary.plannedEvents) {
        plannedEvents.value = itinerary.plannedEvents;
      }

      // Clean up
      localStorage.removeItem("editItinerary");
    } catch (err) {
      console.error("Error parsing editItinerary:", err);
    }
  }
});

// --- VALIDATION FOR STEP 1 ---
const isSection1Valid = computed(() => {
  return (
    form.value.title.trim() !== "" &&
    form.value.city.trim() !== "" &&
    form.value.state.trim() !== "" &&
    form.value.country.trim() !== "" &&
    form.value.start.trim() !== "" &&
    form.value.end.trim() !== "" &&
    form.value.reason.trim() !== "" &&
    (form.value.reason !== "other" || form.value.otherReason.trim() !== "")
  );
});

const validateStep1 = () => {
  if (!isSection1Valid.value) {
    Swal.fire({
      icon: "warning",
      title: "Incomplete Information",
      text: "Please fill out all required fields in Section 1 before proceeding."
    });
    return false;
  }
  return true;
};

// --- BEFORE-CHANGE HOOK FOR STEP 2 ---
const validateStep2 = () => {
  if (addedAttractions.value.length === 0) {
    Swal.fire({
      icon: "warning",
      title: "No Activities Added",
      text: "Please add at least one attraction before proceeding to the next step."
    });
    return false;
  }
  return true;
};

// --- CHECKING FOR SCHEDULING CONFLICTS ---
const conflictMessages = computed(() => {
  let conflicts = {};
  const activities = addedAttractions.value;
  for (let i = 0; i < activities.length; i++) {
    const keyA = activityKey(activities[i]);
    const detailA = planningDetails.value[keyA];
    if (
      !detailA ||
      !detailA.date ||
      !detailA.time ||
      !detailA.durationHours ||
      !detailA.durationMinutes
    )
      continue;

    const startA = new Date(detailA.date + "T" + detailA.time);
    const durationA =
      (parseFloat(detailA.durationHours) * 3600 +
        parseFloat(detailA.durationMinutes) * 60) *
      1000;
    const endA = new Date(startA.getTime() + durationA);

    for (let j = i + 1; j < activities.length; j++) {
      const keyB = activityKey(activities[j]);
      const detailB = planningDetails.value[keyB];
      if (
        !detailB ||
        !detailB.date ||
        !detailB.time ||
        !detailB.durationHours ||
        !detailB.durationMinutes
      )
        continue;

      if (detailA.date === detailB.date) {
        const startB = new Date(detailB.date + "T" + detailB.time);
        const durationB =
          (parseFloat(detailB.durationHours) * 3600 +
            parseFloat(detailB.durationMinutes) * 60) *
          1000;
        const endB = new Date(startB.getTime() + durationB);

        if (startA < endB && startB < endA) {
          conflicts[keyA] =
            "This activity conflicts with another scheduled activity. Please adjust its time or duration.";
          conflicts[keyB] =
            "This activity conflicts with another scheduled activity. Please adjust its time or duration.";
        }
      }
    }
  }
  return conflicts;
});

// --- BEFORE-CHANGE HOOK FOR STEP 3 ---
const validateStep3 = () => {
  // Only validate events that have been dropped into a day column.
  const plannedKeys = Object.keys(planningDetails.value).filter((key) =>
    key.startsWith("planned_")
  );

  // If there are no planned events, then there’s nothing to validate
  if (plannedKeys.length === 0) {
    return true;
  }

  const eventsByDate = {};
  const incompleteEventsByDate = {};

  // Group events by date & check for incomplete fields
  plannedKeys.forEach((key) => {
    const details = planningDetails.value[key];
    const eventDate = details.date || "Unscheduled";
    if (!eventsByDate[eventDate]) {
      eventsByDate[eventDate] = [];
    }
    eventsByDate[eventDate].push({ key, details });

    if (!details.time || details.durationHours === "" || details.durationMinutes === "") {
      const friendlyName = details.attractionName || key;
      if (!incompleteEventsByDate[eventDate]) {
        incompleteEventsByDate[eventDate] = [];
      }
      incompleteEventsByDate[eventDate].push(friendlyName);
    }
  });

  const errorMessages = [];

  // Build error messages for incomplete events
  Object.keys(incompleteEventsByDate).forEach((date) => {
    const eventsList = incompleteEventsByDate[date]
      .map((name) => `<strong>${name}</strong>`)
      .join(", ");
    errorMessages.push(
      `On ${date}, the following events have incomplete details: ${eventsList}.`
    );
  });

  // Check for overlaps and >24h durations
  const overlappingPairsByDate = {};

  Object.keys(eventsByDate).forEach((date) => {
    const completeEvents = eventsByDate[date].filter(
      (e) =>
        e.details.time &&
        e.details.durationHours !== "" &&
        e.details.durationMinutes !== ""
    );

    // Compute each event’s start/end in minutes from midnight
    const computedEvents = completeEvents.map((e) => {
      const [startHour, startMinute] = e.details.time.split(":").map(Number);
      const start = startHour * 60 + startMinute;
      const duration =
        parseInt(e.details.durationHours, 10) * 60 +
        parseInt(e.details.durationMinutes, 10);
      const end = start + duration;
      return { key: e.key, start, end };
    });

    // Detect overlapping events pairwise
    for (let i = 0; i < computedEvents.length; i++) {
      for (let j = i + 1; j < computedEvents.length; j++) {
        const e1 = computedEvents[i];
        const e2 = computedEvents[j];
        if (e1.start < e2.end && e2.start < e1.end) {
          if (!overlappingPairsByDate[date]) {
            overlappingPairsByDate[date] = [];
          }
          const name1 = planningDetails.value[e1.key].attractionName || e1.key;
          const name2 = planningDetails.value[e2.key].attractionName || e2.key;
          const pair = [name1, name2].sort();
          if (
            !overlappingPairsByDate[date].some(
              (existingPair) => existingPair[0] === pair[0] && existingPair[1] === pair[1]
            )
          ) {
            overlappingPairsByDate[date].push(pair);
          }
        }
      }
    }
  });

  // Build error messages for overlapping events
  Object.keys(overlappingPairsByDate).forEach((date) => {
    overlappingPairsByDate[date].forEach((pair) => {
      errorMessages.push(
        `On ${date}, <strong>${pair[0]}</strong> and <strong>${pair[1]}</strong> overlap.`
      );
    });
  });

  if (errorMessages.length > 0) {
    Swal.fire({
      icon: "warning",
      title: "Incomplete or Overlapping Event Details",
      html: errorMessages.join("<br/>"),
      customClass: {
        popup: "step3-swal"
      }
    });
    return false;
  }

  return true;
};

// --- HANDLING ADD/REMOVE ATTRACTIONS ---
const addAttraction = (attraction) => {
  if (
    !addedAttractions.value.find(
      (a) => a.osm_id === attraction.osm_id || a.name === attraction.name
    )
  ) {
    addedAttractions.value.push(attraction);
    const key = activityKey(attraction);
    if (!planningDetails.value[key]) {
      planningDetails.value[key] = {
        date: form.value.start || "",
        time: "",
        durationHours: "",
        durationMinutes: ""
      };
    }
  }
};

const removeAttraction = (attraction) => {
  addedAttractions.value = addedAttractions.value.filter(
    (a) => a.osm_id !== attraction.osm_id && a.name !== attraction.name
  );
  const key = activityKey(attraction);
  delete planningDetails.value[key];
};

const isAttractionAdded = (attraction) => {
  return addedAttractions.value.some(
    (a) => a.osm_id === attraction.osm_id || a.name === attraction.name
  );
};

const toggleAttraction = (attraction) => {
  if (isAttractionAdded(attraction)) {
    removeAttraction(attraction);
  } else {
    addAttraction(attraction);
  }
};

// --- PROVIDE SHARED STATE AND FUNCTIONS TO CHILD COMPONENTS ---
provide("form", form);
provide("addedAttractions", addedAttractions);
provide("planningDetails", planningDetails);
provide("conflictMessages", conflictMessages);
provide("isSection1Valid", isSection1Valid);
provide("toggleAttraction", toggleAttraction);
provide("activityKey", activityKey);
provide("plannedEvents", plannedEvents);

// --- WIZARD HANDLING ---
const currentStep = ref(0);
const wizardRef = ref(null);

const handleTabChange = (prevIndex, newTabIndex) => {
  currentStep.value = newTabIndex;
};

const isReviewStep = computed(() => currentStep.value === 3);

watch(isReviewStep, (newVal) => {
  if (newVal) {
    document.body.classList.add("review-active");
    document.documentElement.classList.add("review-active");
  } else {
    document.body.classList.remove("review-active");
    document.documentElement.classList.remove("review-active");
  }
});

// --- FORM SUBMISSION ---
const handleSubmit = async () => {
  try {
    // Remove any planning detail entries whose keys don't start with "planned_"
    for (const key in planningDetails.value) {
      if (!String(key).startsWith("planned_")) {
        delete planningDetails.value[key];
      }
    }

    const payload = {
      id: form.value.id,
      title: form.value.title,
      city: form.value.city,
      state: form.value.state,
      country: form.value.country,
      start_date: form.value.start,
      end_date: form.value.end,
      reason: form.value.reason === "other" ? form.value.otherReason : form.value.reason,
      addedAttractions: addedAttractions.value,
      planningDetails: planningDetails.value, // only "planned_" keys remain
      plannedEvents: plannedEvents.value
    };

    // Save to localStorage so CalendarView can pick it up
    localStorage.setItem("submittedItinerary", JSON.stringify(payload));

    if (form.value.id) {
      // Edit mode: update the existing itinerary
      await api.put(`itineraries/${form.value.id}/`, payload);
    } else {
      // Create mode: post a new itinerary so that the server assigns an ID
      const response = await api.post("itineraries/", payload);
      // If your API returns an id, use it; otherwise, generate one:
      form.value.id = response.data.id || Date.now();
      payload.id = form.value.id;
      // Save the updated payload with a unique id to localStorage
      localStorage.setItem("submittedItinerary", JSON.stringify(payload));
    }

    Swal.fire({
      icon: "success",
      title: "Success",
      text: "Itinerary submitted successfully!"
    });

    // Navigate back to the calendar
    router.push("/calendar");

    // Reset form data after submission
    nextTick(() => {
      form.value = {
        id: null,
        title: "",
        city: "",
        state: "",
        country: "",
        start: "",
        end: "",
        reason: "",
        otherReason: ""
      };
      addedAttractions.value = [];
      planningDetails.value = {};
    });
  } catch (error) {
    Swal.fire({
      icon: "error",
      title: "Submission Failed",
      text: "Failed to submit itinerary."
    });
  }
};
</script>

<!-- Remove "scoped" so that styles apply to all child components as well -->
<style>
/* Overall container */
.itinerary-form {
  width: 100vw;
  height: 100vh;
  padding: 2rem;
  background: #fff;
  touch-action: pan-y;
  position: relative;
}

/* Override for review step */
.itinerary-form.full-scroll {
  height: auto;
  overflow-y: auto; 
  min-height: 100vh;
}

html.review-active,
body.review-active {
  overflow-y: auto !important;
}

/* Close Button */
.close-button {
  position: absolute;
  top: 1rem;
  left: 1.7rem;
  z-index: 1100;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #2c3e50;
}

/* Global Form Styles */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}
.form-group label {
  margin-bottom: 0.25rem;
  font-weight: 600;
  color: #000;
}
.form-group input,
.form-group select {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
}
.location-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.location-row .form-group {
  flex: 1;
}

/* STEP 2: Attractions & Nearby Cities */
.step2-container {
  display: flex;
  gap: 1rem;
  height: calc(100vh - 250px);
  flex-wrap: nowrap;
}
.radius-sidebar {
  flex: 0 0 300px;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow-y: auto;
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
.added-attractions-header {
  font-weight: bold !important;
  margin-top: 0.5rem;
  border-top: 1px solid #ccc;
  padding-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: #000;
}
.added-attractions-header .added-title {
  font-weight: bold;
}
.added-attractions-header.no-border {
  border-top: none;
  transform: translateY(-17px);
}
.added-attractions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  transition: max-height 0.3s ease;
}
.added-attraction-item {
  color: #000;
  padding: 0.25rem 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.remove-btn,
.add-btn {
  border: none;
  border-radius: 3px;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  font-size: 1rem;
}
.add-btn {
  background: #27ae60;
  color: #fff;
}
.remove-btn {
  background: #e74c3c;
  color: #fff;
}

/* Main Area: Search and Results (STEP 2) */
.search-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  overflow: hidden;
}
.search-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
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
.toggle-advanced,
.search-button {
  padding: 0.5rem 1rem;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease;
}
.toggle-advanced:hover,
.search-button:hover {
  background-color: #34495e;
}
.advanced-filters {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.attractions-table-header {
  display: flex;
  font-weight: bold;
  padding-top: 0.7rem;
  padding-bottom: 0.2rem;
  border-bottom: 1px solid #ccc;
  color: #000;
}
.attraction-activity {
  flex: 2;
}
.attraction-category {
  flex: 1;
}
.attraction-add {
  flex: 1;
  text-align: center;
}
.attraction-item {
  display: flex;
  align-items: center;
  padding: 0.25rem 0;
  color: #000;
}
.results ul {
  padding: 0;
}
.pagination-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
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

/* STEP 3: Plan Activities */
.step3-container {
  display: flex;
  gap: 1rem;
  height: calc(100vh - 250px);
}
.planning-sidebar {
  flex: 0 0 250px;
  background: #f1f1f1;
  padding: 1rem;
  border-radius: 6px;
  overflow-y: auto;
}
.planning-sidebar h4 {
  margin: 0 0 0.5rem;
  color: #000;
}
.sidebar-filters {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.sidebar-search,
.sidebar-select {
  padding: 0.4rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-item {
  padding: 0.4rem;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
  color: #000;
}
.sidebar-item:hover {
  background: #e0e0e0;
}
.planning-main {
  flex: 1;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  overflow-y: auto;
}
.static-header {
  padding: 0.5rem 0 0.25rem 0;
}
.plan-header {
  color: #000;
  margin-bottom: 0.25rem;
  font-size: 1.25rem;
}
.plan-instructions {
  color: #000;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}
.activities-scroll {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 1rem;
}
.activity-planner {
  background: #fff;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border-radius: 6px;
  color: #000;
  border: 1px solid #ccc;
}
.activity-planner h5 {
  margin: 0;
  font-size: 1.1rem;
}
.planner-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.25rem 0;
}
.planner-row label {
  width: 100px;
  font-weight: 600;
  color: #000;
}
.duration-row {
  align-items: center;
}
.duration-inputs {
  display: flex;
  align-items: center;
}
.duration-inputs input {
  width: 50px;
  padding: 0.25rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
}
.duration-separator {
  margin: 0 0.25rem;
}
.error-message {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
.global-conflict-message {
  background: #ffe0e0;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border: 1px solid #e74c3c;
  color: #e74c3c;
  border-radius: 4px;
  text-align: center;
}
.day-group {
  margin-bottom: 1rem;
  border-top: 1px solid #ccc;
  padding-top: 0.5rem;
}
.day-header {
  font-size: 1.2rem;
  font-weight: bold;
  color: #000;
  margin-bottom: 0.25rem;
}

.step3-swal .swal2-html-container strong {
  font-weight: bold !important;
}

/* STEP 4: Review */
.review {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  color: #000;
  margin-bottom: 1rem;
}
.review p {
  margin: 0.5rem 0;
}
.review-added-attractions,
.review-attractions {
  margin-top: 1rem;
}
.review-added-attractions ul,
.review-attractions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Wizard Navigation */
.wizard-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  pointer-events: auto;
  z-index: 10000;
  display: flex;
  justify-content: space-between;
}
.vue-form-wizard .wizard-tab-content {
  padding: 10px 20px 10px !important;
}
.wizard-progress-with-circle {
  top: 54px !important;
}
.wizard-nav button {
  padding: 0.5rem 1rem;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.wizard-nav button:hover {
  background-color: #34495e;
}
</style>