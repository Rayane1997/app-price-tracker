<template>
  <div class="time-range-selector">
    <div class="flex flex-wrap gap-2 sm:flex-nowrap">
      <button
        v-for="option in periodOptions"
        :key="option.value"
        :disabled="disabled"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          selectedPeriod === option.value
            ? 'bg-blue-600 text-white shadow-md'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
          disabled && 'opacity-50 cursor-not-allowed'
        ]"
        @click="handlePeriodChange(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

/**
 * TimeRangeSelector Component
 *
 * Displays buttons to select different time periods for price history
 * Emits period-change event when a button is clicked
 */

const props = defineProps({
  // Currently selected period
  selectedPeriod: {
    type: String,
    default: 'all',
    validator: (value) => ['7d', '30d', '90d', 'all'].includes(value)
  },
  // Disable all buttons (e.g., during loading)
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['period-change'])

// Available time period options
const periodOptions = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: 'all', label: 'All Time' }
]

/**
 * Handle period change
 * @param {string} period - Selected period value
 */
const handlePeriodChange = (period) => {
  if (!props.disabled && period !== props.selectedPeriod) {
    emit('period-change', period)
  }
}
</script>
