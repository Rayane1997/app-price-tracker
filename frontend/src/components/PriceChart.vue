<template>
  <div class="price-chart bg-white rounded-lg shadow-md p-6">
    <div class="chart-header mb-4">
      <h3 class="text-xl font-semibold text-gray-800">Price History Chart</h3>
      <p class="text-sm text-gray-600">{{ periodLabel }}</p>
    </div>

    <!-- Chart Container -->
    <div class="chart-container relative" style="height: 400px;">
      <Line
        v-if="hasData"
        :data="chartDataFormatted"
        :options="chartOptions"
      />
      <div
        v-else
        class="flex items-center justify-center h-full text-gray-500"
      >
        No price history data available
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { formatPrice, formatDate } from '@/utils/formatters'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

/**
 * PriceChart Component
 *
 * Renders a line chart using Chart.js to visualize price history
 * Highlights promotional periods with background colors
 */

const props = defineProps({
  // Chart data object with labels, prices, and promos arrays
  chartData: {
    type: Object,
    required: true,
    default: () => ({
      labels: [],
      prices: [],
      promos: []
    })
  },
  // Current time period
  period: {
    type: String,
    default: 'all'
  }
})

/**
 * Check if chart has data
 */
const hasData = computed(() => {
  return props.chartData.labels && props.chartData.labels.length > 0
})

/**
 * Get period label for display
 */
const periodLabel = computed(() => {
  const labels = {
    '7d': 'Last 7 Days',
    '30d': 'Last 30 Days',
    '90d': 'Last 90 Days',
    'all': 'All Time'
  }
  return labels[props.period] || 'All Time'
})

/**
 * Format chart data for Chart.js
 */
const chartDataFormatted = computed(() => {
  if (!hasData.value) {
    return {
      labels: [],
      datasets: []
    }
  }

  // Format labels (dates)
  const formattedLabels = props.chartData.labels.map(label => formatDate(label))

  // Create background color array based on promo status
  const pointColors = props.chartData.promos.map(isPromo =>
    isPromo ? 'rgba(34, 197, 94, 0.8)' : 'rgba(59, 130, 246, 0.8)'
  )

  const pointHoverColors = props.chartData.promos.map(isPromo =>
    isPromo ? 'rgba(34, 197, 94, 1)' : 'rgba(59, 130, 246, 1)'
  )

  return {
    labels: formattedLabels,
    datasets: [
      {
        label: 'Price',
        data: props.chartData.prices,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: pointColors,
        pointBackgroundColor: pointColors,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: pointHoverColors,
        pointHoverBorderColor: '#fff',
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: false,
        spanGaps: true // Connect points even if there are null values
      }
    ]
  }
})

/**
 * Chart.js configuration options
 */
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 15,
        font: {
          size: 12,
          family: "'Inter', sans-serif"
        }
      }
    },
    tooltip: {
      enabled: true,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      padding: 12,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        title: (context) => {
          // Show original date on hover
          const index = context[0].dataIndex
          const originalDate = props.chartData.labels[index]
          return formatDate(originalDate)
        },
        label: (context) => {
          const price = context.parsed.y
          const index = context.dataIndex
          const isPromo = props.chartData.promos[index]

          if (price === null || price === undefined) {
            return 'Price: N/A (Failed check)'
          }

          const priceLabel = `Price: ${formatPrice(price)}`
          const promoLabel = isPromo ? ' (PROMO)' : ''

          return priceLabel + promoLabel
        }
      }
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Date',
        font: {
          size: 14,
          weight: 'bold',
          family: "'Inter', sans-serif"
        }
      },
      grid: {
        display: false
      },
      ticks: {
        maxRotation: 45,
        minRotation: 45,
        autoSkip: true,
        maxTicksLimit: 10,
        font: {
          size: 11
        }
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Price ($)',
        font: {
          size: 14,
          weight: 'bold',
          family: "'Inter', sans-serif"
        }
      },
      grid: {
        display: true,
        color: 'rgba(0, 0, 0, 0.05)',
        drawBorder: false
      },
      ticks: {
        callback: (value) => formatPrice(value),
        font: {
          size: 11
        }
      },
      beginAtZero: false
    }
  }
}))
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}
</style>
