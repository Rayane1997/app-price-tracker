<template>
  <div
    class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 md:p-6"
    :class="{ 'border-l-4 border-blue-500': alert.status === 'unread' }"
  >
    <!-- Header: Alert Type Badge and Date -->
    <div class="flex items-center justify-between mb-3">
      <span
        class="px-3 py-1 rounded-full text-xs font-semibold text-white"
        :class="alertTypeBadgeClass"
      >
        {{ alertTypeLabel }}
      </span>
      <span class="text-xs text-gray-500">{{ formattedDate }}</span>
    </div>

    <!-- Product Info -->
    <div class="mb-3">
      <router-link
        :to="`/products/${alert.product_id}/history`"
        class="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors"
      >
        {{ alert.product.name }}
      </router-link>
      <p class="text-sm text-gray-500 mt-1">{{ alert.product.domain }}</p>
    </div>

    <!-- Alert Message -->
    <p
      class="text-gray-700 mb-3"
      :class="{ 'font-semibold': alert.status === 'unread' }"
    >
      {{ alert.message }}
    </p>

    <!-- Price Information -->
    <div v-if="alert.old_price" class="flex items-center gap-4 mb-4">
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-500 line-through">
          {{ formatPrice(alert.old_price) }}
        </span>
        <span class="text-lg font-bold text-green-600">
          {{ formatPrice(alert.new_price) }}
        </span>
      </div>
      <span
        v-if="alert.price_drop_percentage"
        class="px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-semibold"
      >
        -{{ alert.price_drop_percentage.toFixed(1) }}%
      </span>
    </div>
    <div v-else class="mb-4">
      <span class="text-lg font-bold text-green-600">
        {{ formatPrice(alert.new_price) }}
      </span>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap gap-2">
      <button
        v-if="alert.status === 'unread'"
        @click="$emit('mark-read', alert)"
        class="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded hover:bg-blue-600 transition-colors"
      >
        Mark Read
      </button>
      <button
        v-if="alert.status !== 'dismissed'"
        @click="$emit('dismiss', alert)"
        class="px-4 py-2 bg-gray-500 text-white text-sm font-medium rounded hover:bg-gray-600 transition-colors"
      >
        Dismiss
      </button>
      <button
        @click="$emit('delete', alert)"
        class="px-4 py-2 bg-red-500 text-white text-sm font-medium rounded hover:bg-red-600 transition-colors"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatCurrency } from '@/utils/formatters'

const props = defineProps({
  alert: {
    type: Object,
    required: true
  }
})

defineEmits(['mark-read', 'dismiss', 'delete'])

// Alert type badge color classes
const alertTypeBadgeClass = computed(() => {
  const classes = {
    price_drop: 'bg-blue-500',
    target_reached: 'bg-green-500',
    promo_detected: 'bg-purple-500'
  }
  return classes[props.alert.type] || 'bg-gray-500'
})

// Alert type label
const alertTypeLabel = computed(() => {
  const labels = {
    price_drop: 'Price Drop',
    target_reached: 'Target Reached',
    promo_detected: 'Promo Detected'
  }
  return labels[props.alert.type] || props.alert.type
})

// Format date to relative time
const formattedDate = computed(() => {
  const date = new Date(props.alert.created_at)
  const now = new Date()
  const diffInSeconds = Math.floor((now - date) / 1000)

  if (diffInSeconds < 60) {
    return 'Just now'
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60)
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else if (diffInSeconds < 604800) {
    const days = Math.floor(diffInSeconds / 86400)
    return `${days} day${days > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString()
  }
})

// Format price with currency
const formatPrice = (price) => {
  return formatCurrency(price, props.alert.product.currency)
}
</script>
