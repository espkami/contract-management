<template>
  <div class="expiry-alert">
    <!-- Stats Bar -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ alerts.length }}</span>
        <span class="stat-label">预警合同总数</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-value text-danger">{{ expiredCount }}</span>
        <span class="stat-label">已过期</span>
      </div>
      <div class="stat-item">
        <span class="stat-value text-warning">{{ expiringCount }}</span>
        <span class="stat-label">即将到期</span>
      </div>
    </div>

    <!-- Filter -->
    <div class="filter-bar">
      <div class="filter-group">
        <button
          :class="['filter-btn', { active: filter === 'all' }]"
          @click="filter = 'all'"
        >
          全部
        </button>
        <button
          :class="['filter-btn', { active: filter === 'expired' }]"
          @click="filter = 'expired'"
        >
          已过期
        </button>
        <button
          :class="['filter-btn', { active: filter === 'expiring' }]"
          @click="filter = 'expiring'"
        >
          即将到期
        </button>
      </div>
      <div class="search-wrapper">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="搜索合同名称..."
          class="search-input"
        />
      </div>
    </div>

    <!-- Alert List -->
    <div class="alert-list">
      <div
        v-for="alert in filteredAlerts"
        :key="alert.id"
        class="alert-card"
        :class="alert.status"
      >
        <div class="alert-indicator"></div>
        <div class="alert-content">
          <div class="alert-header">
            <h3 class="alert-title">{{ alert.title }}</h3>
            <span :class="['alert-status', alert.status]">
              {{ alert.status === 'expired' ? '已过期' : '即将到期' }}
            </span>
          </div>
          <div class="alert-meta">
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              {{ alert.contract_no }}
            </span>
            <span class="meta-item">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              {{ alert.party_b }}
            </span>
          </div>
          <div class="alert-footer">
            <div class="date-info">
              <span class="date-label">到期日期</span>
              <span class="date-value">{{ alert.end_date }}</span>
            </div>
            <div class="days-info">
              <span v-if="alert.days_left > 0" class="days-value">
                剩余 <strong>{{ alert.days_left }}</strong> 天
              </span>
              <span v-else class="days-value text-danger">
                已过期 <strong>{{ Math.abs(alert.days_left) }}</strong> 天
              </span>
            </div>
            <router-link :to="`/contracts/${alert.id}`" class="view-link">
              查看详情
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredAlerts.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--brand-muted-foreground)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
        <p class="empty-text">暂无到期预警合同</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api/index'

const alerts = ref([])
const filter = ref('all')
const search = ref('')

const expiredCount = computed(() => alerts.value.filter(a => a.status === 'expired').length)
const expiringCount = computed(() => alerts.value.filter(a => a.status === 'expiring').length)

const filteredAlerts = computed(() => {
  let result = alerts.value
  
  if (filter.value !== 'all') {
    result = result.filter(a => a.status === filter.value)
  }
  
  if (search.value) {
    const keyword = search.value.toLowerCase()
    result = result.filter(a => 
      a.title.toLowerCase().includes(keyword) ||
      a.contract_no.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

onMounted(async () => {
  try {
    const res = await api.get('/api/contracts/')
    const contracts = res.data.items || []
    alerts.value = contracts.map(c => ({
      id: c.id,
      title: c.title,
      contract_no: c.contract_no,
      party_b: c.party_b,
      end_date: c.end_date,
      days_left: c.days_left,
      status: c.status === '已到期' ? 'expired' : (c.status === '即将到期' ? 'expiring' : 'active')
    })).filter(a => a.status === 'expired' || a.status === 'expiring')
  } catch (error) {
    console.error('Failed to load alerts:', error)
    alerts.value = [
      { id: 1, title: '深圳华创科技有限公司服务合同', contract_no: 'HT-2024-0891', party_b: '深圳华创科技有限公司', end_date: '2026-07-18', days_left: 3, status: 'expiring' },
      { id: 2, title: '北京中盛信息技术有限公司采购合同', contract_no: 'HT-2024-0756', party_b: '北京中盛信息技术有限公司', end_date: '2026-07-10', days_left: -5, status: 'expired' },
      { id: 3, title: '上海恒远贸易发展有限公司销售合同', contract_no: 'HT-2024-0634', party_b: '上海恒远贸易发展有限公司', end_date: '2026-07-25', days_left: 10, status: 'expiring' },
      { id: 4, title: '广州天宇物流有限公司运输合同', contract_no: 'HT-2025-0112', party_b: '广州天宇物流有限公司', end_date: '2026-07-20', days_left: 5, status: 'expiring' },
      { id: 5, title: '杭州智联网络科技股份公司服务合同', contract_no: 'HT-2025-0298', party_b: '杭州智联网络科技股份公司', end_date: '2026-07-08', days_left: -7, status: 'expired' }
    ]
  }
})
</script>

<style scoped>
.expiry-alert {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Stats Bar */
.stats-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 16px 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--brand-foreground);
}

.stat-value.text-danger {
  color: #dc2626;
}

.stat-value.text-warning {
  color: #d97706;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--brand-border);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 16px;
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.filter-btn.active {
  background: var(--brand-primary);
  border-color: var(--brand-primary);
  color: white;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--brand-muted-foreground);
}

.search-input {
  width: 240px;
  padding: 8px 12px 8px 36px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: var(--brand-card);
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--brand-ring);
}

/* Alert List */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-card {
  display: flex;
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}

.alert-card:hover {
  box-shadow: var(--shadow-float);
}

.alert-indicator {
  width: 4px;
  flex-shrink: 0;
}

.alert-card.expired .alert-indicator {
  background: #dc2626;
}

.alert-card.expiring .alert-indicator {
  background: #d97706;
}

.alert-content {
  flex: 1;
  padding: 16px;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.alert-title {
  font-size: 1rem;
  font-weight: 500;
  color: var(--brand-foreground);
  line-height: 1.4;
}

.alert-status {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  margin-left: 12px;
}

.alert-status.expired {
  background: #fee2e2;
  color: #991b1b;
}

.alert-status.expiring {
  background: #fef3c7;
  color: #92400e;
}

.alert-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

.alert-footer {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-top: 12px;
  border-top: 1px solid var(--brand-border);
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.date-label {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.date-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
}

.days-info {
  flex: 1;
}

.days-value {
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.days-value.text-danger {
  color: #dc2626;
}

.view-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-primary);
}

.view-link:hover {
  text-decoration: underline;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px;
  text-align: center;
}

.empty-text {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
  margin-top: 16px;
}

/* Responsive */
@media (max-width: 640px) {
  .stats-bar {
    flex-wrap: wrap;
    gap: 16px;
  }

  .stat-divider {
    display: none;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    justify-content: center;
  }

  .search-input {
    width: 100%;
  }

  .alert-footer {
    flex-wrap: wrap;
    gap: 12px;
  }

  .view-link {
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }
}
</style>