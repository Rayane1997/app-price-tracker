<template>
  <nav class="bg-gray-900 text-white sticky top-0 z-40 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Title -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <svg
              class="h-8 w-8 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
              />
            </svg>
            <span class="text-xl font-bold">Price Tracker</span>
          </router-link>
        </div>

        <!-- Navigation Links -->
        <div class="flex items-center gap-6">
          <router-link
            to="/"
            class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="isActive('/') ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'"
          >
            Wishlist
          </router-link>

          <router-link
            to="/alerts"
            class="relative px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="isActive('/alerts') ? 'bg-gray-800 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'"
          >
            Alerts
            <!-- Badge for alert count (placeholder) -->
            <span
              v-if="alertsCount > 0"
              class="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full"
            >
              {{ alertsCount }}
            </span>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAlertsStore } from '@/stores/alerts'

const route = useRoute()
const alertsStore = useAlertsStore()

// Get unread alerts count from store
const alertsCount = computed(() => alertsStore.unreadCount)

const isActive = (path) => {
  return route.path === path
}

// Refresh unread count on mount and periodically
onMounted(async () => {
  await alertsStore.refreshUnreadCount()

  // Refresh count every 60 seconds
  setInterval(() => {
    alertsStore.refreshUnreadCount()
  }, 60000)
})
</script>
