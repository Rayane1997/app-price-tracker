import { defineStore } from 'pinia'
import * as productsApi from '@/services/products'

/**
 * Products Pinia Store
 * Manages product state, loading, and API interactions
 */
export const useProductsStore = defineStore('products', {
  state: () => ({
    // Products data
    products: [],

    // Loading and error states
    loading: false,
    error: null,

    // Pagination
    totalProducts: 0,
    currentPage: 1,
    pageSize: 12,

    // Filters
    filters: {
      status: null,
      domain: null
    },

    // Available domains for filtering
    availableDomains: []
  }),

  getters: {
    /**
     * Calculate total number of pages
     */
    totalPages: (state) => {
      return Math.ceil(state.totalProducts / state.pageSize)
    },

    /**
     * Check if products exist
     */
    hasProducts: (state) => {
      return state.products.length > 0
    },

    /**
     * Get active products count
     */
    activeProductsCount: (state) => {
      return state.products.filter(p => p.status === 'active').length
    }
  },

  actions: {
    /**
     * Fetch products with current filters and pagination
     */
    async fetchProducts() {
      this.loading = true
      this.error = null

      try {
        const response = await productsApi.getProducts(
          this.currentPage,
          this.pageSize,
          this.filters.status,
          this.filters.domain
        )

        this.products = response.products || []
        this.totalProducts = response.total || 0
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch products'
        console.error('Error fetching products:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch single product by ID
     * @param {number} id - Product ID
     * @returns {Promise} Product object
     */
    async fetchProduct(id) {
      this.loading = true
      this.error = null

      try {
        const product = await productsApi.getProduct(id)
        return product
      } catch (error) {
        this.error = error.response?.data?.detail || `Failed to fetch product ${id}`
        console.error('Error fetching product:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Add new product
     * @param {Object} data - Product data
     * @returns {Promise} Created product
     */
    async addProduct(data) {
      this.loading = true
      this.error = null

      try {
        const product = await productsApi.createProduct(data)

        // Refresh products list
        await this.fetchProducts()

        return product
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create product'
        console.error('Error creating product:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Update existing product
     * @param {number} id - Product ID
     * @param {Object} data - Updated product data
     * @returns {Promise} Updated product
     */
    async updateProduct(id, data) {
      this.loading = true
      this.error = null

      try {
        const product = await productsApi.updateProduct(id, data)

        // Update product in local state
        const index = this.products.findIndex(p => p.id === id)
        if (index !== -1) {
          this.products[index] = product
        }

        return product
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update product'
        console.error('Error updating product:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Delete product
     * @param {number} id - Product ID
     */
    async removeProduct(id) {
      this.loading = true
      this.error = null

      try {
        await productsApi.deleteProduct(id)

        // Remove from local state
        this.products = this.products.filter(p => p.id !== id)
        this.totalProducts--

        // If current page is now empty and not the first page, go back one page
        if (this.products.length === 0 && this.currentPage > 1) {
          this.currentPage--
          await this.fetchProducts()
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete product'
        console.error('Error deleting product:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Set current page and fetch products
     * @param {number} page - Page number
     */
    async setPage(page) {
      if (page < 1 || page > this.totalPages) {
        return
      }

      this.currentPage = page
      await this.fetchProducts()
    },

    /**
     * Update filters and reset to first page
     * @param {Object} filters - Filter object {status, domain}
     */
    async setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.currentPage = 1
      await this.fetchProducts()
    },

    /**
     * Fetch available domains for filtering
     */
    async fetchDomains() {
      try {
        this.availableDomains = await productsApi.getDomains()
      } catch (error) {
        console.error('Error fetching domains:', error)
      }
    },

    /**
     * Reset filters to default
     */
    async resetFilters() {
      this.filters = {
        status: null,
        domain: null
      }
      this.currentPage = 1
      await this.fetchProducts()
    }
  }
})
