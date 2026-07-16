<template>
  <div class="contract-detail">
    <!-- Header -->
    <div class="detail-header">
      <button class="back-btn" @click="$router.back()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        返回列表
      </button>
      <h2 class="detail-title">合同详情</h2>
      <div class="detail-actions">
        <router-link :to="`/contracts/${id}/edit`" class="btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          编辑合同
        </router-link>
      </div>
    </div>

    <!-- Content -->
    <div v-loading="loading" class="detail-content">
      <div class="detail-grid">
        <!-- Left: Contract Info -->
        <div class="info-section">
          <!-- Status Card -->
          <div class="status-card">
            <div class="status-header">
              <h3 class="contract-name">{{ contract?.title || '加载中...' }}</h3>
              <span :class="['status-badge', getStatusClass(contract?.status)]">
                {{ contract?.status || '-' }}
              </span>
            </div>
            <div class="status-meta">
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                {{ contract?.contract_no || '-' }}
              </span>
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                {{ contract?.contract_type || '-' }}
              </span>
            </div>
          </div>

          <!-- Basic Info -->
          <div class="info-card">
            <h4 class="card-title">基本信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">甲方（我方）</span>
                <span class="info-value">{{ contract?.party_a || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">乙方（对方）</span>
                <span class="info-value">{{ contract?.party_b || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">合同金额</span>
                <span class="info-value font-medium">{{ formatAmount(contract?.amount) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">签订日期</span>
                <span class="info-value">{{ contract?.sign_date || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Date Info -->
          <div class="info-card">
            <h4 class="card-title">日期信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">开始日期</span>
                <span class="info-value">{{ contract?.start_date || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">到期日期</span>
                <span class="info-value">{{ contract?.end_date || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">剩余天数</span>
                <span :class="['info-value', { 'text-danger': contract?.days_left <= 30 }]">
                  {{ contract?.days_left > 0 ? contract.days_left + ' 天' : '已过期' }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">提前提醒</span>
                <span class="info-value">{{ contract?.remind_days || 30 }} 天</span>
              </div>
            </div>
          </div>

          <!-- Remarks -->
          <div class="info-card">
            <h4 class="card-title">备注信息</h4>
            <p class="remark-text">{{ contract?.remark || '暂无备注' }}</p>
          </div>

          <!-- Attachment -->
          <div v-if="contract?.file_path" class="info-card">
            <h4 class="card-title">合同附件</h4>
            <div class="attachment-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <div class="attachment-info">
                <span class="attachment-name">{{ contract.file_path }}</span>
                <span class="attachment-size">PDF 文档</span>
              </div>
              <button class="download-btn" @click="download">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                下载
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Preview -->
        <div v-if="contract?.file_path" class="preview-section">
          <div class="preview-card">
            <h4 class="card-title">合同预览</h4>
            <div class="preview-content">
              <div v-if="pdfPreviewUrl && isPdf" class="pdf-viewer">
                <iframe :src="pdfPreviewUrl" frameborder="0"></iframe>
              </div>
              <div v-else-if="wordPreviewUrl && isWord" class="word-viewer">
                <iframe :src="wordPreviewUrl" frameborder="0"></iframe>
              </div>
              <div v-else class="preview-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--brand-muted-foreground)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                <p class="preview-hint">该格式暂不支持在线预览，请下载后查看</p>
                <button class="btn-outline" @click="download">下载文件</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../api/index'

const route = useRoute()
const id = route.params.id
const contract = ref(null)
const loading = ref(true)

const token = localStorage.getItem('token')

const isPdf = computed(() => contract.value?.file_path?.endsWith('.pdf'))
const isWord = computed(() => {
  const fp = contract.value?.file_path || ''
  return fp.endsWith('.doc') || fp.endsWith('.docx')
})
const pdfPreviewUrl = computed(() => {
  if (!contract.value?.file_path) return ''
  return `/api/files/preview/${contract.value.file_path}?token=${token}`
})
const wordPreviewUrl = computed(() => {
  if (!contract.value?.file_path) return ''
  const publicUrl = window.location.origin + `/api/files/preview/${contract.value.file_path}?token=${token}`
  return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(publicUrl)}`
})

function formatAmount(amount) {
  if (!amount) return '¥ 0.00'
  return '¥ ' + Number(amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
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

function download() {
  const token = localStorage.getItem('token')
  window.open(`/api/files/download/${contract.value.file_path}?token=${token}`)
}

onMounted(async () => {
  try {
    const res = await api.get(`/api/contracts/${id}`)
    contract.value = res.data
  } catch (error) {
    console.error('Failed to load contract:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.contract-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: none;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  cursor: pointer;
  transition: background 0.2s ease;
}

.back-btn:hover {
  background: var(--brand-muted);
}

.detail-title {
  flex: 1;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.detail-actions {
  display: flex;
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

.btn-outline {
  padding: 8px 16px;
  background: white;
  color: var(--brand-primary);
  border: 1px solid var(--brand-primary);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-outline:hover {
  background: rgba(45, 125, 112, 0.05);
}

/* Content */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Status Card */
.status-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.contract-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--brand-foreground);
  line-height: 1.4;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
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

.status-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

/* Info Card */
.info-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brand-foreground);
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.info-value {
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.font-medium {
  font-weight: 500;
}

.text-danger {
  color: #dc2626;
}

.remark-text {
  font-size: 0.875rem;
  color: var(--brand-foreground);
  line-height: 1.6;
}

/* Attachment */
.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--brand-muted);
  border-radius: var(--radius-lg);
}

.attachment-info {
  flex: 1;
  min-width: 0;
}

.attachment-name {
  display: block;
  font-size: 0.875rem;
  color: var(--brand-foreground);
  margin-bottom: 2px;
}

.attachment-size {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.download-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  color: var(--brand-primary);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.download-btn:hover {
  background: var(--brand-muted);
}

/* Preview */
.preview-section {
  position: sticky;
  top: 24px;
  height: fit-content;
}

.preview-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.preview-card .card-title {
  padding: 16px 20px;
  margin-bottom: 0;
  border-bottom: 1px solid var(--brand-border);
}

.preview-content {
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pdf-viewer {
  width: 100%;
  height: 100%;
}

.pdf-viewer iframe {
  width: 100%;
  height: 100%;
}

.word-viewer {
  width: 100%;
  height: 100%;
}

.word-viewer iframe {
  width: 100%;
  height: 100%;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  text-align: center;
  padding: 40px;
}

.preview-hint {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}
</style>