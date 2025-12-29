<template>
  <div class="bg-white rounded-lg shadow-md p-4 mb-6">
    <div class="flex flex-col md:flex-row items-start md:items-center gap-4">
      <!-- Status Filter -->
      <div class="flex-1 w-full md:w-auto">
        <label for="status-filter" class="block text-sm font-medium text-gray-700 mb-1">
          Status
        </label>
        <select
          id="status-filter"
          v-model="localFilters.status"
          @change="emitFilterChange"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All Statuses</option>
          <option value="unread">Unread</option>
          <option value="read">Read</option>
          <option value="dismissed">Dismissed</option>
        </select>
      </div>

      <!-- Type Filter -->
      <div class="flex-1 w-full md:w-auto">
        <label for="type-filter" class="block text-sm font-medium text-gray-700 mb-1">
          Type
        </label>
        <select
          id="type-filter"
          v-model="localFilters.type"
          @change="emitFilterChange"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="null">All Types</option>
          <option value="price_drop">Price Drop</option>
          <option value="target_reached">Target Reached</option>
          <option value="promo_detected">Promo Detected</option>
        </select>
      </div>

      <!-- Mark All Read Button -->
      <div class="w-full md:w-auto md:mt-6">
        <button
          @click="$emit('mark-all-read')"
          :disabled="!hasUnreadAlerts"
          class="w-full md:w-auto px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded hover:bg-blue-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Mark All Read
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({
      status: null,
      type: null
    })
  },
  hasUnreadAlerts: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['filter-change', 'mark-all-read'])

// Local filters state
const localFilters = ref({
  status: props.filters.status,
  type: props.filters.type
})

// Watch for external filter changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = {
    status: newFilters.status,
    type: newFilters.type
  }
}, { deep: true })

// Emit filter change event
const emitFilterChange = () => {
  emit('filter-change', { ...localFilters.value })
}
</script>
