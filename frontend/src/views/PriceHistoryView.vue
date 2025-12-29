<template>
  <div class="price-history-view min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center gap-4 mb-4">
          <!-- Back Button -->
          <button
            @click="goBack"
            class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            <span class="font-medium">Back to Wishlist</span>
          </button>
        </div>

        <!-- Product Title -->
        <h1 class="text-3xl font-bold text-gray-900">
          {{ productTitle }}
        </h1>
        <p class="text-gray-600 mt-2">
          Track price changes over time
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <LoadingSpinner size="lg" />
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="bg-red-50 border border-red-200 text-red-800 rounded-lg p-6 text-center"
      >
        <svg class="w-12 h-12 mx-auto mb-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-lg font-semibold mb-2">Error Loading Price History</h3>
        <p>{{ error }}</p>
        <button
          @click="loadData"
          class="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!hasChartData"
        class="bg-white rounded-lg shadow-md p-12 text-center"
      >
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="text-xl font-semibold text-gray-800 mb-2">No Price History Yet</h3>
        <p class="text-gray-600">
          Price tracking data will appear here once the first check is completed.
        </p>
      </div>

      <!-- Main Content -->
      <div v-else class="space-y-6">
        <!-- Time Range Selector -->
        <TimeRangeSelector
          :selected-period="priceHistoryStore.currentPeriod"
          :disabled="loading"
          @period-change="handlePeriodChange"
        />

        <!-- Price Statistics -->
        <PriceStats
          v-if="priceHistoryStore.stats"
          :stats="priceHistoryStore.stats"
        />

        <!-- Price Chart -->
        <PriceChart
          v-if="chartData"
          :chart-data="chartData"
          :period="priceHistoryStore.currentPeriod"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePriceHistoryStore } from '@/stores/priceHistory'
import { useProductsStore } from '@/stores/products'
import { getChartData } from '@/services/priceHistory'
import PriceChart from '@/components/PriceChart.vue'
import PriceStats from '@/components/PriceStats.vue'
import TimeRangeSelector from '@/components/TimeRangeSelector.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

/**
 * PriceHistoryView
 *
 * Main view for displaying price history with chart, statistics, and time range selector
 */

const route = useRoute()
const router = useRouter()
const priceHistoryStore = usePriceHistoryStore()
const productsStore = useProductsStore()

// Component state
const loading = ref(false)
const error = ref(null)
const chartData = ref(null)

/**
 * Get product ID from route params
 */
const productId = computed(() => {
  return parseInt(route.params.id, 10)
})

/**
 * Get product title for display
 */
const productTitle = computed(() => {
  if (priceHistoryStore.product) {
    return priceHistoryStore.product.name || 'Product Price History'
  }
  return 'Product Price History'
})

/**
 * Check if chart data exists
 */
const hasChartData = computed(() => {
  return chartData.value && chartData.value.labels && chartData.value.labels.length > 0
})

/**
 * Load all data (product info, stats, chart data)
 */
const loadData = async () => {
  if (isNaN(productId.value)) {
    error.value = 'Invalid product ID'
    return
  }

  loading.value = true
  error.value = null

  try {
    // Load product info
    const product = await productsStore.fetchProduct(productId.value)
    priceHistoryStore.setProduct(product)

    // Load price statistics
    await priceHistoryStore.fetchStats(productId.value)

    // Load chart data for current period
    await loadChartData(priceHistoryStore.currentPeriod)
  } catch (err) {
    console.error('Error loading price history:', err)
    error.value = err.response?.data?.detail || 'Failed to load price history data'
  } finally {
    loading.value = false
  }
}

/**
 * Load chart data for specific period
 * @param {string} period - Time period ('7d', '30d', '90d', 'all')
 */
const loadChartData = async (period) => {
  try {
    chartData.value = await getChartData(productId.value, period)
  } catch (err) {
    console.error('Error loading chart data:', err)
    throw err
  }
}

/**
 * Handle time period change
 * @param {string} period - Selected period
 */
const handlePeriodChange = async (period) => {
  if (loading.value || period === priceHistoryStore.currentPeriod) {
    return
  }

  loading.value = true
  error.value = null

  try {
    // Update store period
    priceHistoryStore.setPeriod(period)

    // Reload chart data with new period
    await loadChartData(period)
  } catch (err) {
    console.error('Error changing period:', err)
    error.value = 'Failed to load data for selected period'
  } finally {
    loading.value = false
  }
}

/**
 * Navigate back to wishlist
 */
const goBack = () => {
  router.push({ name: 'Wishlist' })
}

// Load data on component mount
onMounted(() => {
  // Reset store state from previous visits
  priceHistoryStore.reset()

  // Load all data
  loadData()
})
</script>
