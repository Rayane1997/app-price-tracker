import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Wishlist',
    component: () => import('../views/WishlistView.vue'),
    meta: { title: 'My Wishlist - Price Tracker' }
  },
  {
    path: '/products/:id/history',
    name: 'PriceHistory',
    component: () => import('../views/PriceHistoryView.vue'),
    meta: { title: 'Price History - Price Tracker' }
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('../views/AlertsView.vue'),
    meta: { title: 'My Alerts - Price Tracker' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Update document title on route change
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Price Tracker'
  next()
})

export default router
