import api from './api'

/**
 * Alerts API Service
 * Handles all alert-related API calls
 */

/**
 * Get list of alerts with pagination and filters
 * @param {number} page - Current page number (1-indexed)
 * @param {number} pageSize - Number of items per page
 * @param {string} status - Filter by status (unread, read, dismissed, or null for all)
 * @param {string} type - Filter by type (price_drop, target_reached, promo_detected, or null for all)
 * @returns {Promise} Response with alerts array and pagination info
 */
export const getAlerts = async (page = 1, pageSize = 20, status = null, type = null) => {
  try {
    const params = {
      page,
      page_size: pageSize
    }

    if (status) {
      params.status = status
    }

    if (type) {
      params.type = type
    }

    const response = await api.get('/alerts', { params })
    return response.data
  } catch (error) {
    console.error('Error fetching alerts:', error)
    throw error
  }
}

/**
 * Get single alert by ID
 * @param {number} id - Alert ID
 * @returns {Promise} Alert object with product information
 */
export const getAlert = async (id) => {
  try {
    const response = await api.get(`/alerts/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching alert ${id}:`, error)
    throw error
  }
}

/**
 * Mark alert as read
 * @param {number} id - Alert ID
 * @returns {Promise} Updated alert object
 */
export const markAlertAsRead = async (id) => {
  try {
    const response = await api.put(`/alerts/${id}/mark-read`)
    return response.data
  } catch (error) {
    console.error(`Error marking alert ${id} as read:`, error)
    throw error
  }
}

/**
 * Dismiss alert
 * @param {number} id - Alert ID
 * @returns {Promise} Updated alert object
 */
export const dismissAlert = async (id) => {
  try {
    const response = await api.put(`/alerts/${id}/dismiss`)
    return response.data
  } catch (error) {
    console.error(`Error dismissing alert ${id}:`, error)
    throw error
  }
}

/**
 * Delete alert permanently
 * @param {number} id - Alert ID
 * @returns {Promise} Success response
 */
export const deleteAlert = async (id) => {
  try {
    const response = await api.delete(`/alerts/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error deleting alert ${id}:`, error)
    throw error
  }
}

/**
 * Get unread alerts count
 * @returns {Promise} Number of unread alerts
 */
export const getUnreadCount = async () => {
  try {
    const response = await api.get('/alerts', {
      params: {
        status: 'unread',
        page: 1,
        page_size: 1 // We only need the count, not the data
      }
    })
    return response.data.total || 0
  } catch (error) {
    console.error('Error fetching unread count:', error)
    return 0
  }
}
