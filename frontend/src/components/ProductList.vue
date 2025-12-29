<template>
  <div>
    <!-- Loading State -->
    <div v-if="productsStore.loading" class="flex justify-center items-center py-12">
      <LoadingSpinner size="lg" />
    </div>

    <!-- Error State -->
    <div v-else-if="productsStore.error" class="rounded-md bg-red-50 p-4">
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
          <h3 class="text-sm font-medium text-red-800">Error loading products</h3>
          <p class="mt-2 text-sm text-red-700">{{ productsStore.error }}</p>
          <button
            class="mt-3 px-3 py-1.5 text-sm font-medium text-red-800 bg-red-100 rounded-md hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500"
            @click="handleRetry"
          >
            Try Again
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!productsStore.hasProducts"
      class="text-center py-12 bg-white rounded-lg shadow-md"
    >
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No products found</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by adding a new product to track.</p>
    </div>

    <!-- Products Grid -->
    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProductCard
          v-for="product in productsStore.products"
          :key="product.id"
          :product="product"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>

      <!-- Pagination -->
      <div
        v-if="productsStore.totalPages > 1"
        class="mt-8 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg shadow-md"
      >
        <!-- Mobile Pagination -->
        <div class="flex flex-1 justify-between sm:hidden">
          <button
            :disabled="productsStore.currentPage === 1"
            class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="handlePageChange(productsStore.currentPage - 1)"
          >
            Previous
          </button>
          <button
            :disabled="productsStore.currentPage === productsStore.totalPages"
            class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="handlePageChange(productsStore.currentPage + 1)"
          >
            Next
          </button>
        </div>

        <!-- Desktop Pagination -->
        <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ startIndex }}</span>
              to
              <span class="font-medium">{{ endIndex }}</span>
              of
              <span class="font-medium">{{ productsStore.totalProducts }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
              <!-- Previous Button -->
              <button
                :disabled="productsStore.currentPage === 1"
                class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="handlePageChange(productsStore.currentPage - 1)"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>

              <!-- Page Numbers -->
              <button
                v-for="page in visiblePages"
                :key="page"
                :class="[
                  page === productsStore.currentPage
                    ? 'z-10 bg-blue-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                    : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 text-sm font-semibold focus:z-20'
                ]"
                @click="handlePageChange(page)"
              >
                {{ page }}
              </button>

              <!-- Next Button -->
              <button
                :disabled="productsStore.currentPage === productsStore.totalPages"
                class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                @click="handlePageChange(productsStore.currentPage + 1)"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProductsStore } from '@/stores/products'
import ProductCard from './ProductCard.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const emit = defineEmits(['edit', 'delete'])

const productsStore = useProductsStore()

// Pagination calculations
const startIndex = computed(() => {
  return (productsStore.currentPage - 1) * productsStore.pageSize + 1
})

const endIndex = computed(() => {
  return Math.min(
    productsStore.currentPage * productsStore.pageSize,
    productsStore.totalProducts
  )
})

// Calculate visible page numbers (show max 7 pages)
const visiblePages = computed(() => {
  const total = productsStore.totalPages
  const current = productsStore.currentPage
  const maxVisible = 7

  if (total <= maxVisible) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages = []
  const leftOffset = Math.floor(maxVisible / 2)
  const rightOffset = maxVisible - leftOffset - 1

  let start = Math.max(1, current - leftOffset)
  let end = Math.min(total, current + rightOffset)

  // Adjust if we're near the beginning or end
  if (current <= leftOffset) {
    end = maxVisible
  } else if (current >= total - rightOffset) {
    start = total - maxVisible + 1
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// Event handlers
const handleEdit = (product) => {
  emit('edit', product)
}

const handleDelete = (product) => {
  emit('delete', product)
}

const handlePageChange = (page) => {
  productsStore.setPage(page)
}

const handleRetry = () => {
  productsStore.fetchProducts()
}
</script>
