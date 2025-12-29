<template>
  <div class="price-stats">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- Current Price Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6 col-span-2 md:col-span-1">
        <div class="text-sm text-gray-600 mb-2">Current Price</div>
        <div class="text-3xl font-bold text-gray-900">
          {{ formatPrice(stats.current_price) }}
        </div>
      </div>

      <!-- Lowest Price Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6">
        <div class="text-sm text-gray-600 mb-2">Lowest Price</div>
        <div class="flex items-center">
          <div class="text-2xl font-bold text-green-600">
            {{ formatPrice(stats.lowest_price) }}
          </div>
          <span class="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
            BEST
          </span>
        </div>
      </div>

      <!-- Highest Price Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6">
        <div class="text-sm text-gray-600 mb-2">Highest Price</div>
        <div class="flex items-center">
          <div class="text-2xl font-bold text-red-600">
            {{ formatPrice(stats.highest_price) }}
          </div>
          <span class="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
            PEAK
          </span>
        </div>
      </div>

      <!-- Average Price Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6">
        <div class="text-sm text-gray-600 mb-2">Average Price</div>
        <div class="text-2xl font-bold text-gray-700">
          {{ formatPrice(stats.average_price) }}
        </div>
      </div>

      <!-- Price Change Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6">
        <div class="text-sm text-gray-600 mb-2">Price Change</div>
        <div class="flex items-center">
          <div
            :class="[
              'text-2xl font-bold',
              priceChangeColor
            ]"
          >
            {{ formatPercentage(stats.price_change_percentage) }}
          </div>
          <!-- Up/Down Arrow Icon -->
          <svg
            v-if="stats.price_change_percentage !== null"
            :class="['ml-2 w-6 h-6', priceChangeColor]"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              v-if="stats.price_change_percentage >= 0"
              fill-rule="evenodd"
              d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"
              clip-rule="evenodd"
            />
            <path
              v-else
              fill-rule="evenodd"
              d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </div>
      </div>

      <!-- Total Checks Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6">
        <div class="text-sm text-gray-600 mb-2">Total Checks</div>
        <div class="text-2xl font-bold text-gray-700">
          {{ stats.total_checks || 0 }}
        </div>
      </div>

      <!-- Last Updated Card -->
      <div class="stat-card bg-white rounded-lg shadow-md p-6 col-span-2">
        <div class="text-sm text-gray-600 mb-2">Last Updated</div>
        <div class="text-lg font-semibold text-gray-700">
          {{ formatDateTime(stats.last_updated) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">
          {{ formatRelativeTime(stats.last_updated) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { formatPrice, formatDateTime, formatRelativeTime, formatPercentage } from '@/utils/formatters'

/**
 * PriceStats Component
 *
 * Displays comprehensive price statistics in a card grid layout
 * Shows current, lowest, highest, average prices, price change, total checks, and last update
 */

const props = defineProps({
  // Price statistics object
  stats: {
    type: Object,
    required: true,
    default: () => ({
      current_price: null,
      lowest_price: null,
      highest_price: null,
      average_price: null,
      price_change_percentage: null,
      total_checks: 0,
      last_updated: null
    })
  }
})

/**
 * Compute color class based on price change
 * Green for negative (price drop), Red for positive (price increase)
 */
const priceChangeColor = computed(() => {
  if (props.stats.price_change_percentage === null) {
    return 'text-gray-500'
  }
  return props.stats.price_change_percentage < 0 ? 'text-green-600' : 'text-red-600'
})
</script>
