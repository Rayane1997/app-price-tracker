import { defineStore } from 'pinia'
import * as alertsApi from '@/services/alerts'

/**
 * Alerts Pinia Store
 * Manages alert state, loading, and API interactions
 */
export const useAlertsStore = defineStore('alerts', {
  state: () => ({
    // Alerts data
    alerts: [],

    // Loading and error states
    loading: false,
    error: null,

    // Pagination
    totalAlerts: 0,
    currentPage: 1,
    pageSize: 20,
    totalPages: 1,

    // Filters
    filters: {
      status: null,
      type: null
    },

    // Unread count for badge
    unreadCount: 0
  }),

  getters: {
    /**
     * Check if alerts exist
     */
    hasAlerts: (state) => {
      return state.alerts.length > 0
    },

    /**
     * Get unread alerts from current list
     */
    unreadAlerts: (state) => {
      return state.alerts.filter(alert => alert.status === 'unread')
    }
  },

  actions: {
    /**
     * Fetch alerts with current filters and pagination
     */
    async fetchAlerts() {
      this.loading = true
      this.error = null

      try {
        const response = await alertsApi.getAlerts(
          this.currentPage,
          this.pageSize,
          this.filters.status,
          this.filters.type
        )

        this.alerts = response.alerts || []
        this.totalAlerts = response.total || 0
        this.totalPages = response.total_pages || 1
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch alerts'
        console.error('Error fetching alerts:', error)
      } finally {
        this.loading = false
      }
    },

    /**
     * Mark alert as read
     * @param {number} id - Alert ID
     */
    async markAsRead(id) {
      this.error = null

      try {
        const updatedAlert = await alertsApi.markAlertAsRead(id)

        // Update alert in local state
        const index = this.alerts.findIndex(a => a.id === id)
        if (index !== -1) {
          this.alerts[index] = updatedAlert
        }

        // Refresh unread count
        await this.refreshUnreadCount()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to mark alert as read'
        console.error('Error marking alert as read:', error)
        throw error
      }
    },

    /**
     * Dismiss alert
     * @param {number} id - Alert ID
     */
    async dismiss(id) {
      this.error = null

      try {
        const updatedAlert = await alertsApi.dismissAlert(id)

        // Update alert in local state
        const index = this.alerts.findIndex(a => a.id === id)
        if (index !== -1) {
          this.alerts[index] = updatedAlert
        }

        // Refresh unread count
        await this.refreshUnreadCount()

        // If we're filtering by a specific status, remove dismissed alerts from list
        if (this.filters.status && this.filters.status !== 'dismissed') {
          this.alerts = this.alerts.filter(a => a.id !== id)
          this.totalAlerts--
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to dismiss alert'
        console.error('Error dismissing alert:', error)
        throw error
      }
    },

    /**
     * Delete alert permanently
     * @param {number} id - Alert ID
     */
    async remove(id) {
      this.error = null

      try {
        await alertsApi.deleteAlert(id)

        // Remove from local state
        this.alerts = this.alerts.filter(a => a.id !== id)
        this.totalAlerts--

        // Refresh unread count
        await this.refreshUnreadCount()

        // If current page is now empty and not the first page, go back one page
        if (this.alerts.length === 0 && this.currentPage > 1) {
          this.currentPage--
          await this.fetchAlerts()
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete alert'
        console.error('Error deleting alert:', error)
        throw error
      }
    },

    /**
     * Set current page and fetch alerts
     * @param {number} page - Page number
     */
    async setPage(page) {
      if (page < 1 || page > this.totalPages) {
        return
      }

      this.currentPage = page
      await this.fetchAlerts()
    },

    /**
     * Update filters and reset to first page
     * @param {Object} filters - Filter object {status, type}
     */
    async setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.currentPage = 1
      await this.fetchAlerts()
    },

    /**
     * Refresh unread count for badge
     */
    async refreshUnreadCount() {
      try {
        this.unreadCount = await alertsApi.getUnreadCount()
      } catch (error) {
        console.error('Error refreshing unread count:', error)
      }
    },

    /**
     * Mark all unread alerts as read
     */
    async markAllAsRead() {
      this.error = null

      try {
        // Get all unread alerts from current list
        const unreadAlerts = this.alerts.filter(a => a.status === 'unread')

        // Mark each as read
        for (const alert of unreadAlerts) {
          await alertsApi.markAlertAsRead(alert.id)
        }

        // Refresh the list to get updated data
        await this.fetchAlerts()
        await this.refreshUnreadCount()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to mark all alerts as read'
        console.error('Error marking all as read:', error)
        throw error
      }
    },

    /**
     * Reset filters to default
     */
    async resetFilters() {
      this.filters = {
        status: null,
        type: null
      }
      this.currentPage = 1
      await this.fetchAlerts()
    }
  }
})
