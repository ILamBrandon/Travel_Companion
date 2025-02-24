<template>
  <div class="form-section">
    <!-- Title -->
    <div class="form-group">
      <label for="title">Title</label>
      <input id="title" v-model="form.title" type="text" placeholder="Enter itinerary title" />
    </div>
    <!-- Location: City, State, Country -->
    <div class="location-row">
      <div class="form-group inline">
        <label for="city">City</label>
        <input id="city" v-model="form.city" type="text" placeholder="City (required)" />
      </div>
      <div class="form-group inline">
        <label for="state">State/Province/Region</label>
        <input id="state" v-model="form.state" type="text" placeholder="State (required)" />
      </div>
      <div class="form-group inline">
        <label for="country">Country</label>
        <input id="country" v-model="form.country" type="text" placeholder="Country (required)" />
      </div>
    </div>
    <!-- Dates -->
    <div class="form-group">
      <label for="start">Start Date</label>
      <input
        id="start"
        v-model="form.start"
        type="date"
        :min="minStart"
        @click="$event.target.showPicker()"
      />
    </div>
    <div class="form-group">
      <label for="end">End Date</label>
      <input
        id="end"
        v-model="form.end"
        type="date"
        :min="form.start || minStart"
        @click="$event.target.showPicker()"
      />
    </div>
    <!-- Reason for Travel -->
    <div class="form-group">
      <label for="reason">Reason for Travel</label>
      <select id="reason" v-model="form.reason">
        <option value="">Select reason...</option>
        <option value="Job">Job</option>
        <option value="Vacation">Vacation</option>
        <option value="Family">Family</option>
        <option value="other">Other</option>
      </select>
    </div>
    <div class="form-group" v-if="form.reason === 'other'">
      <label for="otherReason">Please specify</label>
      <input id="otherReason" v-model="form.otherReason" type="text" placeholder="Type your reason" />
    </div>
  </div>
</template>

<script setup>
import { inject } from "vue";

// Inject the form object
const form = inject("form");

// Create a variable for today's date in the "YYYY-MM-DD" format.
// This value is used as the minimum date for the start date input.
const today = new Date().toISOString().split("T")[0];
const minStart = today;
</script>

<style scoped>
/* (Optional component‑specific styles can go here) */
</style>
