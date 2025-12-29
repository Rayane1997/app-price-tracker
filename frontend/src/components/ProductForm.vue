<template>
  <!-- Modal backdrop -->
  <Transition name="fade">
    <div
      v-if="show"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="handleClose"
    >
      <!-- Modal dialog -->
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 overflow-hidden">
        <!-- Header -->
        <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ isEditMode ? 'Edit Product' : 'Add New Product' }}
          </h3>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <!-- URL Field -->
          <div>
            <label for="url" class="block text-sm font-medium text-gray-700 mb-1">
              Product URL <span class="text-red-500">*</span>
            </label>
            <input
              id="url"
              v-model="formData.url"
              type="url"
              required
              :disabled="isEditMode"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder="https://example.com/product"
            />
            <p class="mt-1 text-xs text-gray-500">
              {{ isEditMode ? 'URL cannot be changed after creation' : 'Enter the full URL of the product page' }}
            </p>
          </div>

          <!-- Name Field -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
              Product Name
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Optional - will be auto-fetched if not provided"
            />
            <p class="mt-1 text-xs text-gray-500">
              Leave empty to automatically fetch from the product page
            </p>
          </div>

          <!-- Target Price Field -->
          <div>
            <label for="target_price" class="block text-sm font-medium text-gray-700 mb-1">
              Target Price ($)
            </label>
            <input
              id="target_price"
              v-model.number="formData.target_price"
              type="number"
              step="0.01"
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="0.00"
            />
            <p class="mt-1 text-xs text-gray-500">
              You'll be notified when the price drops to or below this amount
            </p>
          </div>

          <!-- Check Frequency Field -->
          <div>
            <label for="check_frequency" class="block text-sm font-medium text-gray-700 mb-1">
              Check Frequency (hours)
            </label>
            <input
              id="check_frequency"
              v-model.number="formData.check_frequency_hours"
              type="number"
              min="1"
              max="168"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="24"
            />
            <p class="mt-1 text-xs text-gray-500">
              How often to check for price changes (1-168 hours)
            </p>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-700">{{ errorMessage }}</p>
              </div>
            </div>
          </div>

          <!-- Footer Buttons -->
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              @click="handleClose"
              :disabled="loading"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="loading || !isFormValid"
            >
              <span v-if="loading" class="flex items-center gap-2">
                <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Saving...
              </span>
              <span v-else>
                {{ isEditMode ? 'Update Product' : 'Add Product' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'close'])

// Form data
const formData = ref({
  url: '',
  name: '',
  target_price: null,
  check_frequency_hours: 24
})

const loading = ref(false)
const errorMessage = ref('')

// Computed properties
const isEditMode = computed(() => props.product !== null)

const isFormValid = computed(() => {
  if (!formData.value.url) return false

  // Validate URL format
  try {
    new URL(formData.value.url)
  } catch {
    return false
  }

  // Validate target price if provided
  if (formData.value.target_price !== null && formData.value.target_price !== '') {
    if (formData.value.target_price < 0) return false
  }

  // Validate check frequency
  if (formData.value.check_frequency_hours < 1 || formData.value.check_frequency_hours > 168) {
    return false
  }

  return true
})

// Watch for product prop changes to populate form in edit mode
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    formData.value = {
      url: newProduct.url || '',
      name: newProduct.name || '',
      target_price: newProduct.target_price,
      check_frequency_hours: newProduct.check_frequency_hours || 24
    }
  } else {
    // Reset form for add mode
    formData.value = {
      url: '',
      name: '',
      target_price: null,
      check_frequency_hours: 24
    }
  }
  errorMessage.value = ''
}, { immediate: true })

// Watch show prop to reset error when modal opens
watch(() => props.show, (newShow) => {
  if (newShow) {
    errorMessage.value = ''
  }
})

// Event handlers
const handleSubmit = async () => {
  if (!isFormValid.value) {
    errorMessage.value = 'Please fix the validation errors'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    // Extract domain from URL
    const domain = new URL(formData.value.url).hostname

    // Prepare data for submission
    const dataToSave = {
      url: formData.value.url,
      domain: domain,
      check_frequency_hours: formData.value.check_frequency_hours
    }

    // Only include optional fields if they have values
    if (formData.value.name && formData.value.name.trim()) {
      dataToSave.name = formData.value.name
    }

    if (formData.value.target_price !== null && formData.value.target_price !== '') {
      dataToSave.target_price = formData.value.target_price
    }

    emit('save', dataToSave)
  } catch (error) {
    errorMessage.value = error.message || 'Failed to save product'
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  if (!loading.value) {
    emit('close')
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
