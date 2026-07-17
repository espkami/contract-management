<template>
  <div class="contract-list">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <router-link to="/contracts/add" class="btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          新增合同
        </router-link>
        <div class="search-wrapper">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="filter.keyword"
            type="text"
            placeholder="搜索合同编号、名称、对方单位..."
            class="search-input"
            @keyup.enter="load"
          />
        </div>
      </div>
      <div class="toolbar-right">
        <select v-model="filter.status" class="filter-select" @change="load">
          <option value="">全部状态</option>
          <option value="生效中">生效中</option>
          <option value="即将到期">即将到期</option>
          <option value="已过期">已过期</option>
          <option value="已终止">已终止</option>
        </select>
        <select v-model="filter.contract_type" class="filter-select" @change="load">
          <option value="">全部类型</option>
          <option value="维修合同">维修合同</option>
          <option value="维保合同">维保合同</option>
          <option value="外修合同">外修合同</option>
          <option value="装修合同">装修合同</option>
          <option value="商业合同">商业合同</option>
        </select>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>合同编号</th>
            <th>合同名称</th>
            <th>对方单位</th>
            <th class="text-right">合同金额</th>
            <th>签订日期</th>
            <th>到期日期</th>
            <th class="text-center">状态</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody v-loading="loading">
          <tr v-for="contract in list" :key="contract.id">
            <td class="mono">{{ contract.contract_no }}</td>
            <td>{{ contract.title }}</td>
            <td class="muted">{{ contract.party_a }}</td>
            <td class="text-right font-medium">¥ {{ formatAmount(contract.amount) }}</td>
            <td>{{ contract.sign_date || '-' }}</td>
            <td>{{ contract.end_date || '-' }}</td>
            <td class="text-center">
              <span :class="['status-badge', getStatusClass(contract.status)]">
                {{ contract.status }}
              </span>
            </td>
            <td class="text-center">
              <router-link :to="`/contracts/${contract.id}`" class="action-link">查看</router-link>
              <router-link :to="`/contracts/${contract.id}/edit`" class="action-link">编辑</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <p class="pagination-info">共 {{ total }} 条记录</p>
      <div class="pagination-buttons">
        <button class="page-btn" :disabled="page <= 1" @click="page--; load()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <button
          v-for="p in visiblePages"
          :key="p"
          :class="['page-btn', { active: p === page }]"
          @click="page = p; load()"
        >
          {{ p }}
        </button>
        <button class="page-btn" :disabled="page >= totalPages" @click="page++; load()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const route = useRoute()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 20

const filter = reactive({
  keyword: '',
  status: '',
  contract_type: ''
})

watch(() => route.query.status, (newStatus) => {
  filter.status = newStatus || ''
  page.value = 1
  load()
})

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function formatAmount(amount) {
  if (!amount) return '0.00'
  return Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

function getStatusClass(status) {
  const statusMap = {
    '生效中': 'active',
    '执行中': 'active',
    '即将到期': 'expiring',
    '已过期': 'expired',
    '已到期': 'expired',
    '待审批': 'pending',
    '已终止': 'terminated'
  }
  return statusMap[status] || 'active'
}

async function load() {
  loading.value = true
  try {
    const params = {
      skip: (page.value - 1) * pageSize,
      limit: pageSize,
      ...filter
    }
    const res = await api.get('/api/contracts/', { params })
    list.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('Failed to load contracts:', error)
    ElMessage.error('加载合同列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.status) {
    filter.status = route.query.status
  }
  load()
})
</script>

<style scoped>
.contract-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--brand-primary);
  color: white;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  transition: opacity 0.2s ease;
}

.btn-primary:hover {
  opacity: 0.9;
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
  width: 280px;
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

.search-input::placeholder {
  color: var(--brand-muted-foreground);
}

.filter-select {
  padding: 8px 32px 8px 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: var(--brand-card);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.filter-select:focus {
  outline: none;
  border-color: var(--brand-ring);
}

/* Table */
.table-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table thead {
  background: var(--brand-muted);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 500;
  color: var(--brand-muted-foreground);
}

.data-table td {
  padding: 12px 16px;
  color: var(--brand-card-foreground);
  border-bottom: 1px solid var(--brand-border);
}

.data-table tbody tr:hover {
  background: var(--brand-muted);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.mono {
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.muted {
  color: var(--brand-muted-foreground);
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.font-medium {
  font-weight: 500;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.active {
  background: #dcfce7;
  color: #166534;
}

.status-badge.expiring {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.expired {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.pending {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.terminated {
  background: var(--brand-muted);
  color: var(--brand-muted-foreground);
}

/* Action Links */
.action-link {
  color: var(--brand-primary);
  font-size: 0.875rem;
  margin-right: 12px;
}

.action-link:hover {
  text-decoration: underline;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--brand-card-foreground);
  background: var(--brand-card);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--brand-muted);
}

.page-btn.active {
  background: var(--brand-primary);
  border-color: var(--brand-primary);
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .data-table {
    font-size: 0.75rem;
  }

  .data-table th,
  .data-table td {
    padding: 8px;
  }
}
</style>