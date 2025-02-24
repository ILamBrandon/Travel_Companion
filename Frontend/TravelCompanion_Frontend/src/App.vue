<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-container">
    <!-- Render the routed component -->
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* Container that covers the full viewport with your background image */
.app-container {
  width: 100vw;
  min-height: 100vh;
}


/* Main content area */
main {
}
</style>
