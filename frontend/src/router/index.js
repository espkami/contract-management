import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/contracts', component: () => import('../views/contracts/List.vue') },
    { path: '/contracts/add', component: () => import('../views/contracts/Add.vue'), meta: { manager: true } },
    { path: '/contracts/:id', component: () => import('../views/contracts/Detail.vue') },
    { path: '/contracts/:id/edit', component: () => import('../views/contracts/Add.vue'), meta: { manager: true } },
    { path: '/expiry-alert', component: () => import('../views/ExpiryAlert.vue') },
    { path: '/admin/users', component: () => import('../views/admin/Users.vue'), meta: { admin: true } },
    { path: '/admin/notifications', component: () => import('../views/admin/Notifications.vue'), meta: { admin: true } },
    { path: '/admin/settings', component: () => import('../views/admin/Settings.vue'), meta: { admin: true } },
    { path: '/admin/backup', component: () => import('../views/admin/Backup.vue'), meta: { admin: true } },
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) return '/login'
  if (to.meta.admin && auth.user?.role !== 'admin') return '/dashboard'
  if (to.meta.manager && !auth.canManage) return '/dashboard'
})

export default router
