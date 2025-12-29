<template>
  <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
    <!-- Product Image -->
    <div class="relative h-48 bg-gray-100 overflow-hidden">
      <img
        v-if="product.image_url"
        :src="product.image_url"
        :alt="product.name"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-gray-400"
      >
        <svg class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>

      <!-- Promo Badge -->
      <div
        v-if="product.is_promo"
        class="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded"
      >
        PROMO
      </div>

      <!-- Status Badge -->
      <div
        class="absolute top-2 left-2 px-2 py-1 rounded text-xs font-semibold"
        :class="statusBadgeClass"
      >
        {{ statusText }}
      </div>
    </div>

    <!-- Product Info -->
    <div class="p-4">
      <!-- Product Name -->
      <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2" :title="product.name">
        {{ product.name || 'Unnamed Product' }}
      </h3>

      <!-- Domain -->
      <p class="text-sm text-gray-500 mb-3">
        {{ product.domain || 'Unknown domain' }}
      </p>

      <!-- Prices -->
      <div class="flex items-baseline gap-2 mb-4">
        <span class="text-2xl font-bold text-gray-900">
          {{ formatPrice(product.current_price) }}
        </span>
        <span v-if="product.target_price" class="text-sm text-gray-500">
          Target: {{ formatPrice(product.target_price) }}
        </span>
      </div>

      <!-- Last Check -->
      <p class="text-xs text-gray-400 mb-4">
        Last checked: {{ formatDate(product.last_check) }}
      </p>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <button
          class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          @click="handleViewHistory"
        >
          View History
        </button>
        <button
          class="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          @click="handleEdit"
          aria-label="Edit product"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
        <button
          class="px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
          @click="handleDelete"
          aria-label="Delete product"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatPrice as formatPriceUtil } from '@/utils/formatters'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])
const router = useRouter()

// Status badge styling
const statusBadgeClass = computed(() => {
  const classes = {
    active: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    paused: 'bg-yellow-500 text-white'
  }
  return classes[props.product.status] || 'bg-gray-500 text-white'
})

const statusText = computed(() => {
  return props.product.status ? props.product.status.toUpperCase() : 'UNKNOWN'
})

// Format price with currency symbol
const formatPrice = (price) => {
  if (price == null) return 'N/A'
  return formatPriceUtil(price, props.product.currency || 'EUR')
}

// Format date to readable string
const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Handle image load error
const handleImageError = (e) => {
  e.target.style.display = 'none'
}

// Event handlers
const handleViewHistory = () => {
  router.push(`/products/${props.product.id}/history`)
}

const handleEdit = () => {
  emit('edit', props.product)
}

const handleDelete = () => {
  emit('delete', props.product)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
