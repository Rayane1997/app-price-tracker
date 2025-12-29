import api from './api'

/**
 * Price History API Service
 * Handles all API calls related to price history data
 */

/**
 * Get price history for a product with optional time period filtering
 * @param {number} productId - Product ID
 * @param {string} period - Time period: '7d', '30d', '90d', or 'all'
 * @returns {Promise<Array>} Array of price history entries
 */
export async function getPriceHistory(productId, period = 'all') {
  try {
    const response = await api.get(`/products/${productId}/price-history`, {
      params: { period }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching price history:', error)
    throw error
  }
}

/**
 * Get comprehensive price statistics for a product
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} Price statistics object
 */
export async function getPriceStats(productId) {
  try {
    const response = await api.get(`/products/${productId}/price-history/stats`)
    return response.data
  } catch (error) {
    console.error('Error fetching price stats:', error)
    throw error
  }
}

/**
 * Get Chart.js-ready price history data
 * @param {number} productId - Product ID
 * @param {string} period - Time period: '7d', '30d', '90d', or 'all'
 * @returns {Promise<Object>} Chart data object with labels, prices, and promos arrays
 */
export async function getChartData(productId, period = 'all') {
  try {
    const response = await api.get(`/products/${productId}/price-history/chart`, {
      params: { period }
    })
    return response.data
  } catch (error) {
    console.error('Error fetching chart data:', error)
    throw error
  }
}
