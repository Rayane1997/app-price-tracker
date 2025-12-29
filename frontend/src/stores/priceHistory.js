import { defineStore } from 'pinia'
import * as priceHistoryApi from '@/services/priceHistory'

/**
 * Price History Pinia Store
 * Manages price history state, statistics, and API interactions
 */
export const usePriceHistoryStore = defineStore('priceHistory', {
  state: () => ({
    // Price history data
    history: [],

    // Price statistics
    stats: null,

    // Product basic info
    product: null,

    // Current selected time period
    currentPeriod: 'all',

    // Loading and error states
    loading: false,
    error: null
  }),

  getters: {
    /**
     * Check if history data exists
     */
    hasHistory: (state) => {
      return state.history && state.history.length > 0
    },

    /**
     * Get lowest price from stats
     */
    lowestPrice: (state) => {
      return state.stats?.lowest_price || null
    },

    /**
     * Get highest price from stats
     */
    highestPrice: (state) => {
      return state.stats?.highest_price || null
    },

    /**
     * Get current price from stats
     */
    currentPrice: (state) => {
      return state.stats?.current_price || null
    },

    /**
     * Get average price from stats
     */
    averagePrice: (state) => {
      return state.stats?.average_price || null
    },

    /**
     * Get price change percentage from stats
     */
    priceChangePercentage: (state) => {
      return state.stats?.price_change_percentage || null
    }
  },

  actions: {
    /**
     * Fetch price history for a product
     * @param {number} productId - Product ID
     * @param {string} period - Time period ('7d', '30d', '90d', 'all')
     */
    async fetchHistory(productId, period = 'all') {
      this.loading = true
      this.error = null

      try {
        this.history = await priceHistoryApi.getPriceHistory(productId, period)
        this.currentPeriod = period
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch price history'
        console.error('Error fetching price history:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Fetch price statistics for a product
     * @param {number} productId - Product ID
     */
    async fetchStats(productId) {
      this.loading = true
      this.error = null

      try {
        this.stats = await priceHistoryApi.getPriceStats(productId)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch price statistics'
        console.error('Error fetching price stats:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    /**
     * Set the current time period
     * @param {string} period - Time period ('7d', '30d', '90d', 'all')
     */
    setPeriod(period) {
      this.currentPeriod = period
    },

    /**
     * Set product basic info
     * @param {Object} product - Product object
     */
    setProduct(product) {
      this.product = product
    },

    /**
     * Reset the store to initial state
     */
    reset() {
      this.history = []
      this.stats = null
      this.product = null
      this.currentPeriod = 'all'
      this.loading = false
      this.error = null
    }
  }
})
