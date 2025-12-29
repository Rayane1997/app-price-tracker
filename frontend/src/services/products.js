import api from './api'

/**
 * Product API Service
 * Handles all product-related API calls
 */

/**
 * Get list of products with pagination and filters
 * @param {number} page - Current page number (1-indexed)
 * @param {number} pageSize - Number of items per page
 * @param {string} status - Filter by status (active, error, paused, or null for all)
 * @param {string} domain - Filter by domain (or null for all)
 * @returns {Promise} Response with products array and pagination info
 */
export const getProducts = async (page = 1, pageSize = 12, status = null, domain = null) => {
  try {
    const params = {
      skip: (page - 1) * pageSize,
      limit: pageSize
    }

    if (status) {
      params.status = status
    }

    if (domain) {
      params.domain = domain
    }

    const response = await api.get('/products', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching products:', error)
    throw error
  }
}

/**
 * Get single product by ID
 * @param {number} id - Product ID
 * @returns {Promise} Product object
 */
export const getProduct = async (id) => {
  try {
    const response = await api.get(`/products/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching product ${id}:`, error)
    throw error
  }
}

/**
 * Create new product
 * @param {Object} data - Product data (url required, name, target_price, check_frequency_hours optional)
 * @returns {Promise} Created product object
 */
export const createProduct = async (data) => {
  try {
    const response = await api.post('/products', data)
    return response.data
  } catch (error) {
    console.error('Error creating product:', error)
    throw error
  }
}

/**
 * Update existing product
 * @param {number} id - Product ID
 * @param {Object} data - Updated product data
 * @returns {Promise} Updated product object
 */
export const updateProduct = async (id, data) => {
  try {
    const response = await api.put(`/products/${id}`, data)
    return response.data
  } catch (error) {
    console.error(`Error updating product ${id}:`, error)
    throw error
  }
}

/**
 * Delete product
 * @param {number} id - Product ID
 * @returns {Promise} Success response
 */
export const deleteProduct = async (id) => {
  try {
    const response = await api.delete(`/products/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error deleting product ${id}:`, error)
    throw error
  }
}

/**
 * Get list of unique domains from all products
 * @returns {Promise} Array of domain strings
 */
export const getDomains = async () => {
  try {
    const response = await api.get('/products/domains')
    return response.data
  } catch (error) {
    console.error('Error fetching domains:', error)
    throw error
  }
}
