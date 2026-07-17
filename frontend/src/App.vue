<template>
  <el-config-provider :locale="zhCn">
    <router-view v-if="$route.meta.public" />
    <div v-else class="app-layout">
      <!-- Sidebar -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <!-- Logo -->
        <div class="sidebar-header">
          <svg class="sidebar-logo" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <path d="M9 15l2 2 4-4"/>
          </svg>
          <span v-show="!sidebarCollapsed" class="sidebar-title">合同管理系统</span>
          <button class="sidebar-toggle" @click="sidebarCollapsed = !sidebarCollapsed">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="sidebar-nav">
          <!-- Main Navigation -->
          <div class="nav-section">
            <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
              </svg>
              <span v-show="!sidebarCollapsed">数据看板</span>
            </router-link>

            <router-link to="/contracts" class="nav-item" :class="{ active: $route.path === '/contracts' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <path d="M9 15l2 2 4-4"/>
              </svg>
              <span v-show="!sidebarCollapsed">合同管理</span>
            </router-link>

            <router-link to="/contracts/add" class="nav-item" :class="{ active: $route.path === '/contracts/add' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              <span v-show="!sidebarCollapsed">合同登记</span>
            </router-link>

            <router-link to="/expiry-alert" class="nav-item" :class="{ active: $route.path === '/expiry-alert' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span v-show="!sidebarCollapsed">到期预警</span>
              <span v-if="!sidebarCollapsed && alertCount > 0" class="nav-badge">{{ alertCount }}</span>
            </router-link>
          </div>

          <!-- System Management -->
          <div v-if="auth.isAdmin" class="nav-section">
            <p v-show="!sidebarCollapsed" class="nav-section-title">系统管理</p>
            <router-link to="/admin/users" class="nav-item" :class="{ active: $route.path === '/admin/users' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              <span v-show="!sidebarCollapsed">用户管理</span>
            </router-link>

            <router-link to="/admin/notifications" class="nav-item" :class="{ active: $route.path === '/admin/notifications' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              <span v-show="!sidebarCollapsed">通知管理</span>
            </router-link>

            <router-link to="/admin/settings" class="nav-item" :class="{ active: $route.path === '/admin/settings' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
              <span v-show="!sidebarCollapsed">通知配置</span>
            </router-link>

            <router-link to="/admin/backup" class="nav-item" :class="{ active: $route.path === '/admin/backup' }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <span v-show="!sidebarCollapsed">系统备份</span>
            </router-link>
          </div>
        </nav>

        <!-- User Info -->
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">{{ auth.user?.username?.charAt(0)?.toUpperCase() || '管' }}</div>
            <div v-show="!sidebarCollapsed" class="user-details">
              <p class="user-name truncate">{{ auth.user?.username || '管理员' }}</p>
              <p class="user-email truncate">{{ auth.user?.email || 'admin@company.com' }}</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="main-content">
        <!-- Top Header -->
        <header class="top-header">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <div class="header-actions">
            <!-- Notifications -->
            <button class="header-btn notification-btn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              </svg>
              <span v-if="alertCount > 0" class="notification-dot"></span>
            </button>

            <div class="header-divider"></div>

            <!-- Date -->
            <div class="header-date">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>{{ currentDate }}</span>
            </div>

            <div class="header-divider"></div>

            <!-- Logout -->
            <button class="logout-btn" @click="doLogout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              <span>退出</span>
            </button>
          </div>
        </header>

        <!-- Page Content -->
        <main class="page-content">
          <router-view />
        </main>
      </div>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useAuthStore } from './stores/auth'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const sidebarCollapsed = ref(false)
const alertCount = ref(0)
const currentDate = computed(() => dayjs().format('YYYY-MM-DD'))

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '数据看板',
    '/contracts': '合同管理',
    '/contracts/add': '合同登记',
    '/expiry-alert': '到期预警',
    '/admin/users': '用户管理'
  }
  return titles[route.path] || '合同管理系统'
})

async function doLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--brand-background);
  color: var(--brand-foreground);
  font-family: var(--font-sans);
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  height: 64px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  flex-shrink: 0;
}

.sidebar-title {
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  flex: 1;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--sidebar-text);
  padding: 4px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .sidebar-toggle {
    display: block;
  }
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 16px;
}

.nav-section-title {
  font-size: 0.6875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sidebar-text);
  opacity: 0.5;
  margin-bottom: 8px;
  padding-left: 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-lg);
  color: var(--sidebar-text);
  font-size: 0.875rem;
  transition: all 0.2s ease;
  margin-bottom: 4px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--sidebar-text-hover);
}

.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-active-text) !important;
  font-weight: 500;
}

.nav-item svg {
  flex-shrink: 0;
}

.nav-badge {
  margin-left: auto;
  background: var(--state-error);
  color: white;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--brand-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  color: white;
  font-size: 0.875rem;
  margin-bottom: 2px;
}

.user-email {
  color: var(--sidebar-text);
  font-size: 0.6875rem;
  opacity: 0.6;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: var(--brand-card);
  border-bottom: 1px solid var(--brand-border);
  flex-shrink: 0;
}

.page-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-btn {
  background: none;
  border: none;
  padding: 8px;
  border-radius: var(--radius-lg);
  color: var(--brand-muted-foreground);
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s ease;
}

.header-btn:hover {
  background: var(--brand-muted);
}

.notification-dot {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--state-error);
}

.header-divider {
  width: 1px;
  height: 24px;
  background: var(--brand-border);
}

.header-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: 1px solid var(--brand-border);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: var(--brand-muted);
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--brand-background);
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: var(--sidebar-width);
  }

  .page-content {
    padding: 16px;
  }

  .header-date {
    display: none;
  }

  .logout-btn span {
    display: none;
  }
}
</style>