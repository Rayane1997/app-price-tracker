<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Page Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <h1 class="text-3xl font-bold text-gray-900">My Wishlist</h1>
        <p class="mt-2 text-sm text-gray-600">
          Track and monitor prices for your favorite products
        </p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filter Bar -->
      <FilterBar
        :filters="productsStore.filters"
        :domains="productsStore.availableDomains"
        @filter-change="handleFilterChange"
        @add-product="handleAddProduct"
      />

      <!-- Product List -->
      <ProductList
        @edit="handleEditProduct"
        @delete="handleDeleteProduct"
      />
    </div>

    <!-- Product Form Modal -->
    <ProductForm
      :show="showForm"
      :product="editingProduct"
      @save="handleSaveProduct"
      @close="handleCloseForm"
    />

    <!-- Confirm Delete Dialog -->
    <ConfirmDialog
      :show="showDeleteDialog"
      title="Delete Product"
      :message="`Are you sure you want to delete '${deletingProduct?.name || 'this product'}'? This action cannot be undone.`"
      @confirm="handleConfirmDelete"
      @cancel="handleCancelDelete"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import FilterBar from '@/components/FilterBar.vue'
import ProductList from '@/components/ProductList.vue'
import ProductForm from '@/components/ProductForm.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

// Store
const productsStore = useProductsStore()

// State
const showForm = ref(false)
const editingProduct = ref(null)
const showDeleteDialog = ref(false)
const deletingProduct = ref(null)

// Lifecycle
onMounted(async () => {
  // Fetch initial data
  await Promise.all([
    productsStore.fetchProducts(),
    productsStore.fetchDomains()
  ])
})

// Product Form Handlers
const handleAddProduct = () => {
  editingProduct.value = null
  showForm.value = true
}

const handleEditProduct = (product) => {
  editingProduct.value = product
  showForm.value = true
}

const handleCloseForm = () => {
  showForm.value = false
  editingProduct.value = null
}

const handleSaveProduct = async (productData) => {
  try {
    if (editingProduct.value) {
      // Update existing product
      await productsStore.updateProduct(editingProduct.value.id, productData)
    } else {
      // Create new product
      await productsStore.addProduct(productData)
    }

    // Close form on success
    handleCloseForm()

    // Refresh domains in case a new domain was added
    await productsStore.fetchDomains()
  } catch (error) {
    // Error is already handled by the store
    console.error('Error saving product:', error)
  }
}

// Delete Handlers
const handleDeleteProduct = (product) => {
  deletingProduct.value = product
  showDeleteDialog.value = true
}

const handleConfirmDelete = async () => {
  if (deletingProduct.value) {
    try {
      await productsStore.removeProduct(deletingProduct.value.id)
      showDeleteDialog.value = false
      deletingProduct.value = null

      // Refresh domains in case the last product of a domain was deleted
      await productsStore.fetchDomains()
    } catch (error) {
      // Error is already handled by the store
      console.error('Error deleting product:', error)
      showDeleteDialog.value = false
      deletingProduct.value = null
    }
  }
}

const handleCancelDelete = () => {
  showDeleteDialog.value = false
  deletingProduct.value = null
}

// Filter Handlers
const handleFilterChange = (filters) => {
  productsStore.setFilters(filters)
}
</script>
