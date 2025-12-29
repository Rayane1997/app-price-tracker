/**
 * Utility functions for formatting prices, dates, and percentages
 */

/**
 * Format price with currency symbol
 * @param {number|null} price - Price value
 * @param {string} currency - Currency code (default: 'USD')
 * @returns {string} Formatted price string
 */
export function formatPrice(price, currency = 'USD') {
  if (price === null || price === undefined) {
    return 'N/A'
  }

  const currencyMap = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'CA$',
    'AUD': 'A$'
  }

  const symbol = currencyMap[currency] || currency
  const formattedPrice = price.toFixed(2)

  // For EUR, format as "42,99 €"
  if (currency === 'EUR') {
    return `${formattedPrice.replace('.', ',')} ${symbol}`
  }

  // For others, format as "$42.99"
  return `${symbol}${formattedPrice}`
}

/**
 * Format ISO date string to readable format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date (e.g., "Dec 29, 2025")
 */
export function formatDate(dateString) {
  if (!dateString) {
    return 'N/A'
  }

  const date = new Date(dateString)
  if (isNaN(date.getTime())) {
    return 'Invalid Date'
  }

  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }

  return new Intl.DateTimeFormat('en-US', options).format(date)
}

/**
 * Format ISO date string with time
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date with time (e.g., "Dec 29, 2025 3:45 PM")
 */
export function formatDateTime(dateString) {
  if (!dateString) {
    return 'N/A'
  }

  const date = new Date(dateString)
  if (isNaN(date.getTime())) {
    return 'Invalid Date'
  }

  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }

  return new Intl.DateTimeFormat('en-US', options).format(date)
}

/**
 * Format date as relative time
 * @param {string} dateString - ISO date string
 * @returns {string} Relative time (e.g., "2 hours ago", "3 days ago")
 */
export function formatRelativeTime(dateString) {
  if (!dateString) {
    return 'N/A'
  }

  const date = new Date(dateString)
  if (isNaN(date.getTime())) {
    return 'Invalid Date'
  }

  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  const diffWeek = Math.floor(diffDay / 7)
  const diffMonth = Math.floor(diffDay / 30)
  const diffYear = Math.floor(diffDay / 365)

  if (diffSec < 60) {
    return 'just now'
  } else if (diffMin < 60) {
    return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`
  } else if (diffHour < 24) {
    return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`
  } else if (diffDay < 7) {
    return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`
  } else if (diffWeek < 4) {
    return `${diffWeek} ${diffWeek === 1 ? 'week' : 'weeks'} ago`
  } else if (diffMonth < 12) {
    return `${diffMonth} ${diffMonth === 1 ? 'month' : 'months'} ago`
  } else {
    return `${diffYear} ${diffYear === 1 ? 'year' : 'years'} ago`
  }
}

/**
 * Format percentage with sign
 * @param {number|null} value - Percentage value
 * @returns {string} Formatted percentage (e.g., "-15.5%", "+5.2%")
 */
export function formatPercentage(value) {
  if (value === null || value === undefined) {
    return 'N/A'
  }

  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

/**
 * Format currency with proper symbols and formatting
 * Alias for formatPrice for consistency
 * @param {number|null} price - Price value
 * @param {string} currency - Currency code (default: 'USD')
 * @returns {string} Formatted price string
 */
export function formatCurrency(price, currency = 'USD') {
  return formatPrice(price, currency)
}
