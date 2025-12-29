<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <Navbar />

    <!-- Main Content -->
    <router-view />
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
</script>
