<template>
  <div class="flex justify-center items-center" :class="containerClasses">
    <div
      class="animate-spin rounded-full border-b-2 border-blue-600"
      :class="spinnerClasses"
      role="status"
      aria-label="Loading"
    >
      <span class="sr-only">Loading...</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const spinnerClasses = computed(() => {
  const sizes = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  }
  return sizes[props.size]
})

const containerClasses = computed(() => {
  const padding = {
    sm: 'p-2',
    md: 'p-4',
    lg: 'p-6'
  }
  return padding[props.size]
})
</script>
