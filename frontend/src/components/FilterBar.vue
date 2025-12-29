<template>
  <div class="bg-white rounded-lg shadow-md p-4 mb-6">
    <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <!-- Filters -->
      <div class="flex flex-col sm:flex-row gap-3 flex-1">
        <!-- Status Filter -->
        <div class="flex-1 min-w-0">
          <label for="status-filter" class="block text-xs font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status-filter"
            v-model="localFilters.status"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="handleFilterChange"
          >
            <option :value="null">All Statuses</option>
            <option value="active">Active</option>
            <option value="error">Error</option>
            <option value="paused">Paused</option>
          </select>
        </div>

        <!-- Domain Filter -->
        <div class="flex-1 min-w-0">
          <label for="domain-filter" class="block text-xs font-medium text-gray-700 mb-1">
            Domain
          </label>
          <select
            id="domain-filter"
            v-model="localFilters.domain"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @change="handleFilterChange"
          >
            <option :value="null">All Domains</option>
            <option v-for="domain in domains" :key="domain" :value="domain">
              {{ domain }}
            </option>
          </select>
        </div>

        <!-- Reset Button -->
        <div class="flex items-end">
          <button
            type="button"
            class="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
            @click="handleReset"
          >
            Reset
          </button>
        </div>
      </div>

      <!-- Add Product Button -->
      <div class="flex items-end w-full sm:w-auto">
        <button
          type="button"
          class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors flex items-center justify-center gap-2"
          @click="handleAddProduct"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          Add Product
        </button>
      </div>
    </div>

    <!-- Active Filters Display -->
    <div v-if="hasActiveFilters" class="mt-3 flex items-center gap-2 flex-wrap">
      <span class="text-xs font-medium text-gray-600">Active filters:</span>
      <span
        v-if="localFilters.status"
        class="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full"
      >
        Status: {{ localFilters.status }}
        <button
          type="button"
          class="hover:text-blue-900"
          @click="clearFilter('status')"
          aria-label="Clear status filter"
        >
          <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </span>
      <span
        v-if="localFilters.domain"
        class="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full"
      >
        Domain: {{ localFilters.domain }}
        <button
          type="button"
          class="hover:text-green-900"
          @click="clearFilter('domain')"
          aria-label="Clear domain filter"
        >
          <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({ status: null, domain: null })
  },
  domains: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['filter-change', 'add-product'])

// Local filters state
const localFilters = ref({
  status: props.filters.status,
  domain: props.filters.domain
})

// Watch for external filter changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

// Computed
const hasActiveFilters = computed(() => {
  return localFilters.value.status !== null || localFilters.value.domain !== null
})

// Event handlers
const handleFilterChange = () => {
  emit('filter-change', { ...localFilters.value })
}

const handleReset = () => {
  localFilters.value = {
    status: null,
    domain: null
  }
  handleFilterChange()
}

const clearFilter = (filterName) => {
  localFilters.value[filterName] = null
  handleFilterChange()
}

const handleAddProduct = () => {
  emit('add-product')
}
</script>
