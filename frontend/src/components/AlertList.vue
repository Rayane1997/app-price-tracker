<template>
  <div>
    <!-- Loading State -->
    <LoadingSpinner v-if="alertsStore.loading" size="lg" />

    <!-- Error State -->
    <div
      v-else-if="alertsStore.error"
      class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800"
    >
      <p class="font-semibold">Error loading alerts</p>
      <p class="text-sm">{{ alertsStore.error }}</p>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!alertsStore.hasAlerts"
      class="bg-gray-50 rounded-lg p-12 text-center"
    >
      <svg
        class="mx-auto h-16 w-16 text-gray-400 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <h3 class="text-xl font-semibold text-gray-700 mb-2">No alerts found</h3>
      <p class="text-gray-500">
        You'll receive alerts when product prices drop or reach your target price.
      </p>
    </div>

    <!-- Alerts List -->
    <div v-else>
      <div class="space-y-4">
        <AlertCard
          v-for="alert in alertsStore.alerts"
          :key="alert.id"
          :alert="alert"
          @mark-read="handleMarkRead"
          @dismiss="handleDismiss"
          @delete="handleDelete"
        />
      </div>

      <!-- Pagination -->
      <div
        v-if="alertsStore.totalPages > 1"
        class="flex justify-center items-center gap-2 mt-8"
      >
        <button
          @click="goToPage(alertsStore.currentPage - 1)"
          :disabled="alertsStore.currentPage === 1"
          class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          Previous
        </button>

        <div class="flex gap-2">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="goToPage(page)"
            :disabled="page === alertsStore.currentPage"
            class="px-4 py-2 border rounded-md text-sm font-medium transition-colors"
            :class="
              page === alertsStore.currentPage
                ? 'bg-blue-500 text-white border-blue-500'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            "
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="goToPage(alertsStore.currentPage + 1)"
          :disabled="alertsStore.currentPage === alertsStore.totalPages"
          class="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>

      <!-- Pagination Info -->
      <div class="text-center text-sm text-gray-600 mt-4">
        Showing {{ alertsStore.alerts.length }} of {{ alertsStore.totalAlerts }} alerts
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAlertsStore } from '@/stores/alerts'
import AlertCard from './AlertCard.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const alertsStore = useAlertsStore()

const emit = defineEmits(['mark-read', 'dismiss', 'delete'])

// Calculate visible page numbers for pagination
const visiblePages = computed(() => {
  const current = alertsStore.currentPage
  const total = alertsStore.totalPages
  const delta = 2 // Number of pages to show on each side of current page

  const pages = []
  const rangeStart = Math.max(1, current - delta)
  const rangeEnd = Math.min(total, current + delta)

  for (let i = rangeStart; i <= rangeEnd; i++) {
    pages.push(i)
  }

  return pages
})

// Go to specific page
const goToPage = (page) => {
  if (page >= 1 && page <= alertsStore.totalPages) {
    alertsStore.setPage(page)
  }
}

// Event handlers that pass through to parent
const handleMarkRead = (alert) => {
  emit('mark-read', alert)
}

const handleDismiss = (alert) => {
  emit('dismiss', alert)
}

const handleDelete = (alert) => {
  emit('delete', alert)
}
</script>
