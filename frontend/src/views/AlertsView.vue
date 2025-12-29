<template>
  <div class="alerts-view min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">My Alerts</h1>
        <p class="text-gray-600 mt-2">
          Stay updated on price drops and special deals for your tracked products.
        </p>
      </div>

      <!-- Filters -->
      <AlertFilters
        :filters="alertsStore.filters"
        :has-unread-alerts="hasUnreadAlerts"
        @filter-change="handleFilterChange"
        @mark-all-read="handleMarkAllRead"
      />

      <!-- Alerts List -->
      <AlertList
        @mark-read="handleMarkAsRead"
        @dismiss="handleDismiss"
        @delete="confirmDelete"
      />

      <!-- Delete Confirmation Dialog -->
      <ConfirmDialog
        :show="showDeleteDialog"
        title="Delete Alert"
        message="Are you sure you want to permanently delete this alert? This action cannot be undone."
        @confirm="handleDelete"
        @cancel="cancelDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAlertsStore } from '@/stores/alerts'
import AlertFilters from '@/components/AlertFilters.vue'
import AlertList from '@/components/AlertList.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const alertsStore = useAlertsStore()

// State for delete confirmation
const showDeleteDialog = ref(false)
const alertToDelete = ref(null)

// Check if there are unread alerts
const hasUnreadAlerts = computed(() => {
  return alertsStore.unreadAlerts.length > 0 || alertsStore.unreadCount > 0
})

/**
 * Mark alert as read
 */
const handleMarkAsRead = async (alert) => {
  try {
    await alertsStore.markAsRead(alert.id)
  } catch (error) {
    console.error('Failed to mark alert as read:', error)
  }
}

/**
 * Dismiss alert
 */
const handleDismiss = async (alert) => {
  try {
    await alertsStore.dismiss(alert.id)
  } catch (error) {
    console.error('Failed to dismiss alert:', error)
  }
}

/**
 * Show delete confirmation dialog
 */
const confirmDelete = (alert) => {
  alertToDelete.value = alert
  showDeleteDialog.value = true
}

/**
 * Delete alert after confirmation
 */
const handleDelete = async () => {
  if (alertToDelete.value) {
    try {
      await alertsStore.remove(alertToDelete.value.id)
    } catch (error) {
      console.error('Failed to delete alert:', error)
    }
  }
  showDeleteDialog.value = false
  alertToDelete.value = null
}

/**
 * Cancel delete operation
 */
const cancelDelete = () => {
  showDeleteDialog.value = false
  alertToDelete.value = null
}

/**
 * Mark all unread alerts as read
 */
const handleMarkAllRead = async () => {
  try {
    await alertsStore.markAllAsRead()
  } catch (error) {
    console.error('Failed to mark all alerts as read:', error)
  }
}

/**
 * Handle filter changes
 */
const handleFilterChange = async (filters) => {
  try {
    await alertsStore.setFilters(filters)
  } catch (error) {
    console.error('Failed to update filters:', error)
  }
}

// Load alerts on mount
onMounted(async () => {
  await alertsStore.fetchAlerts()
  await alertsStore.refreshUnreadCount()
})
</script>
