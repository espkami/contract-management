<template>
  <div class="dashboard">
    <!-- Stat Cards Row -->
    <div class="stat-cards">
      <div class="stat-card" @click="goToContracts('all')">
        <div class="stat-header">
          <div>
            <p class="stat-value">{{ stats.total }}</p>
            <p class="stat-label">合同总数</p>
          </div>
          <div class="stat-icon" style="background: rgba(45, 125, 112, 0.1);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
        </div>
        <div class="stat-trend" :class="getTrendClass(stats.total_change)">
          <svg v-if="stats.total_change > 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
          <svg v-else-if="stats.total_change < 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="trend-value">{{ formatChange(stats.total_change) }}</span>
          <span class="trend-label">较上月</span>
        </div>
      </div>

      <div class="stat-card" @click="goToContracts('active')">
        <div class="stat-header">
          <div>
            <p class="stat-value">{{ stats.active }}</p>
            <p class="stat-label">生效中</p>
          </div>
          <div class="stat-icon" style="background: #dcfce7;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
        </div>
        <div class="stat-trend" :class="getTrendClass(stats.active_change)">
          <svg v-if="stats.active_change > 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
          <svg v-else-if="stats.active_change < 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="trend-value">{{ formatChange(stats.active_change) }}</span>
          <span class="trend-label">较上月</span>
        </div>
      </div>

      <div class="stat-card" @click="goToContracts('expiring')">
        <div class="stat-header">
          <div>
            <p class="stat-value">{{ stats.expiring }}</p>
            <p class="stat-label">即将到期</p>
          </div>
          <div class="stat-icon" style="background: #fef3c7;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
        </div>
        <div class="stat-trend" :class="getTrendClass(stats.expiring_change)">
          <svg v-if="stats.expiring_change > 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
          <svg v-else-if="stats.expiring_change < 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="trend-value">{{ formatChange(stats.expiring_change) }}</span>
          <span class="trend-label">较上月</span>
        </div>
      </div>

      <div class="stat-card" @click="goToContracts('expired')">
        <div class="stat-header">
          <div>
            <p class="stat-value">{{ stats.expired }}</p>
            <p class="stat-label">已过期</p>
          </div>
          <div class="stat-icon" style="background: #fee2e2;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
        </div>
        <div class="stat-trend" :class="getTrendClass(stats.expired_change)">
          <svg v-if="stats.expired_change > 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
          </svg>
          <svg v-else-if="stats.expired_change < 0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
            <polyline points="17 18 23 18 23 12"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="trend-value">{{ formatChange(stats.expired_change) }}</span>
          <span class="trend-label">较上月</span>
        </div>
      </div>
    </div>

    <!-- Middle Row -->
    <div class="dashboard-row">
      <!-- Status Distribution -->
      <div class="distribution-card">
        <h3 class="card-title">合同状态分布</h3>
        <div class="distribution-content">
          <!-- Donut Chart -->
          <div class="donut-chart">
            <div class="donut-ring" :style="{ background: donutGradient }"></div>
            <div class="donut-center">
              <span class="donut-value">{{ stats.total }}</span>
              <span class="donut-label">总计</span>
            </div>
          </div>
          <!-- Legend -->
          <div class="distribution-legend">
            <div class="legend-item" @click="goToContracts('active')">
              <div class="legend-color" style="background: #16a34a;"></div>
              <span class="legend-label">生效中</span>
              <div class="legend-values">
                <span class="legend-value">{{ stats.active }}</span>
                <span class="legend-percent">{{ activePercent }}%</span>
              </div>
            </div>
            <div class="legend-item" @click="goToContracts('expiring')">
              <div class="legend-color" style="background: #d97706;"></div>
              <span class="legend-label">即将到期</span>
              <div class="legend-values">
                <span class="legend-value">{{ stats.expiring }}</span>
                <span class="legend-percent">{{ expiringPercent }}%</span>
              </div>
            </div>
            <div class="legend-item" @click="goToContracts('expired')">
              <div class="legend-color" style="background: #dc2626;"></div>
              <span class="legend-label">已过期</span>
              <div class="legend-values">
                <span class="legend-value">{{ stats.expired }}</span>
                <span class="legend-percent">{{ expiredPercent }}%</span>
              </div>
            </div>
            <div class="legend-item" @click="goToContracts('completed')">
              <div class="legend-color" style="background: #94a3b8;"></div>
              <span class="legend-label">已完成</span>
              <div class="legend-values">
                <span class="legend-value">{{ stats.completed }}</span>
                <span class="legend-percent">{{ completedPercent }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Expiring Contracts -->
      <div class="expiring-card">
        <h3 class="card-title">即将到期合同</h3>
        <div class="expiring-list">
          <div
            v-for="contract in expiringContracts"
            :key="contract.id"
            class="expiring-item"
            :class="{ striped: expiringContracts.indexOf(contract) % 2 === 0 }"
            @click="goToContractDetail(contract.id)"
          >
            <div class="expiring-info">
              <p class="expiring-name truncate">{{ contract.title }}</p>
              <p class="expiring-code">{{ contract.contract_no }}</p>
            </div>
            <div class="expiring-meta">
              <span class="expiring-date">{{ contract.end_date }}</span>
              <span class="expiring-badge" :class="{ expired: contract.days_left <= 0 }">{{ contract.days_left <= 0 ? '已过期' : '即将到期' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Trend -->
    <div class="trend-card">
      <h3 class="card-title">月度合同趋势</h3>
      <div class="trend-chart">
        <div v-for="(month, index) in monthlyData" :key="index" class="trend-bar">
          <span class="trend-count">{{ month.value }}</span>
          <div class="trend-fill" :style="{ height: month.percent + '%', opacity: 0.75 + (month.percent / 200) }"></div>
          <span class="trend-label">{{ month.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const stats = ref({
  total: 0,
  active: 0,
  expiring: 0,
  expired: 0,
  completed: 0,
  total_change: 0,
  active_change: 0,
  expiring_change: 0,
  expired_change: 0,
  monthly_change: 0
})

const expiringContracts = ref([])

const monthlyData = ref([])

const activePercent = computed(() => {
  if (stats.value.total === 0) return '0'
  return ((stats.value.active / stats.value.total) * 100).toFixed(1)
})
const expiringPercent = computed(() => {
  if (stats.value.total === 0) return '0'
  return ((stats.value.expiring / stats.value.total) * 100).toFixed(1)
})
const expiredPercent = computed(() => {
  if (stats.value.total === 0) return '0'
  return ((stats.value.expired / stats.value.total) * 100).toFixed(1)
})
const completedPercent = computed(() => {
  if (stats.value.total === 0) return '0'
  return ((stats.value.completed / stats.value.total) * 100).toFixed(1)
})

const donutGradient = computed(() => {
  const total = stats.value.total || 1
  const activeDeg = (stats.value.active / total) * 360
  const expiringDeg = (stats.value.expiring / total) * 360
  const expiredDeg = (stats.value.expired / total) * 360
  
  return `conic-gradient(
    #16a34a 0deg ${activeDeg}deg,
    #d97706 ${activeDeg}deg ${activeDeg + expiringDeg}deg,
    #dc2626 ${activeDeg + expiringDeg}deg ${activeDeg + expiringDeg + expiredDeg}deg,
    #94a3b8 ${activeDeg + expiringDeg + expiredDeg}deg 360deg
  )`
})

const getTrendClass = (change) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'warning'
}

const formatChange = (change) => {
  if (change > 0) return `+${change}%`
  return `${change}%`
}

const goToContracts = (status) => {
  const statusMap = {
    'all': '',
    'active': '生效中',
    'expiring': '即将到期',
    'expired': '已过期',
    'completed': '已终止'
  }
  router.push({ path: '/contracts', query: status ? { status: statusMap[status] } : {} })
}

const goToContractDetail = (id) => {
  router.push(`/contracts/${id}`)
}

onMounted(async () => {
  try {
    const [statsRes, contractsRes, trendRes] = await Promise.all([
      api.get('/api/contracts/stats'),
      api.get('/api/contracts/expiring'),
      api.get('/api/contracts/monthly-trend')
    ])
    if (statsRes.data) stats.value = statsRes.data
    if (contractsRes.data) expiringContracts.value = contractsRes.data.filter(c => c.days_left > 0).slice(0, 5)
    if (trendRes.data) {
      monthlyData.value = trendRes.data
      const maxValue = Math.max(...monthlyData.value.map(m => m.value)) || 1
      monthlyData.value.forEach(m => {
        m.percent = (m.value / maxValue) * 100
      })
    }
  } catch (error) {
    console.log('Dashboard data fetch error:', error)
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Stat Cards */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: var(--brand-primary);
  box-shadow: 0 4px 12px rgba(45, 125, 112, 0.1);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--brand-foreground);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
  margin-top: 4px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
}

.stat-trend.positive {
  color: var(--brand-primary);
}

.stat-trend.warning {
  color: #d97706;
}

.stat-trend.negative {
  color: #dc2626;
}

.trend-value {
  font-weight: 600;
}

.trend-label {
  color: var(--brand-muted-foreground);
}

/* Dashboard Row */
.dashboard-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

@media (max-width: 1024px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }
}

/* Distribution Card */
.distribution-card,
.expiring-card,
.trend-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--brand-foreground);
  margin-bottom: 16px;
}

.distribution-content {
  display: flex;
  align-items: center;
  gap: 32px;
}

@media (max-width: 640px) {
  .distribution-content {
    flex-direction: column;
  }
}

.donut-chart {
  position: relative;
  width: 160px;
  height: 160px;
  flex-shrink: 0;
}

.donut-ring {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  margin: 32px;
}

.donut-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--brand-foreground);
}

.donut-label {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.distribution-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background 0.2s ease;
}

.legend-item:hover {
  background: var(--brand-background);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 12px;
}

.legend-label {
  flex: 1;
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.legend-values {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.legend-percent {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

/* Expiring Card */
.expiring-list {
  display: flex;
  flex-direction: column;
}

.expiring-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 8px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background 0.2s ease;
}

.expiring-item:hover {
  background: var(--brand-background);
}

.expiring-item.striped {
  background: var(--brand-background);
}

.expiring-info {
  flex: 1;
  min-width: 0;
}

.expiring-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
  margin-bottom: 2px;
}

.expiring-code {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.expiring-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
}

.expiring-date {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.expiring-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  background: #fef3c7;
  color: #92400e;
}

.expiring-badge.expired {
  background: #fee2e2;
  color: #991b1b;
}

/* Trend Chart */
.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 200px;
}

.trend-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.trend-count {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.trend-fill {
  width: 100%;
  background: var(--brand-primary);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: height 0.3s ease;
}

.trend-label {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}
</style>