<template>
  <div class="backup-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">系统备份</h2>
      </div>
    </div>

    <!-- 数据概览 -->
    <div class="info-grid">
      <div class="info-card">
        <div class="info-icon" style="background: rgba(45, 125, 112, 0.1);">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--brand-primary)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
          </svg>
        </div>
        <div class="info-content">
          <p class="info-value">{{ info.db_size_mb }} MB</p>
          <p class="info-label">数据库大小</p>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon" style="background: #dbeafe;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <div class="info-content">
          <p class="info-value">{{ info.uploads_count }}</p>
          <p class="info-label">附件数量 ({{ info.uploads_size_mb }} MB)</p>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon" style="background: #dcfce7;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-4"/>
            <polyline points="9 11 12 14 15 11"/>
            <line x1="12" y1="2" x2="12" y2="14"/>
          </svg>
        </div>
        <div class="info-content">
          <p class="info-value">{{ info.contract_count }}</p>
          <p class="info-label">合同数量</p>
        </div>
      </div>

      <div class="info-card">
        <div class="info-icon" style="background: #fef3c7;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          </svg>
        </div>
        <div class="info-content">
          <p class="info-value">{{ info.user_count }}</p>
          <p class="info-label">用户数量</p>
        </div>
      </div>
    </div>

    <!-- 操作区域 -->
    <div class="actions-grid">
      <!-- 导出备份 -->
      <div class="action-card">
        <div class="action-header">
          <div class="action-icon export-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          <h3 class="action-title">导出备份</h3>
        </div>
        <p class="action-desc">将所有合同数据（含数据库和附件）打包为 zip 文件下载到本地，可用于迁移或存档</p>
        <button class="btn-primary" :disabled="exporting" @click="exportBackup">
          <span v-if="exporting" class="loading-spinner"></span>
          <span v-else>立即导出</span>
        </button>
      </div>

      <!-- 导入备份 -->
      <div class="action-card">
        <div class="action-header">
          <div class="action-icon import-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <h3 class="action-title">导入备份</h3>
        </div>
        <p class="action-desc">从 zip 备份文件恢复数据，将覆盖当前所有合同和附件（用户账号和配置也会被覆盖）</p>
        <input ref="fileInput" type="file" accept=".zip" style="display: none;" @change="importBackup" />
        <button class="btn-warning" :disabled="importing" @click="$refs.fileInput.click()">
          <span v-if="importing" class="loading-spinner"></span>
          <span v-else>选择文件导入</span>
        </button>
      </div>

      <!-- 清空数据 -->
      <div class="action-card">
        <div class="action-header">
          <div class="action-icon danger-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              <line x1="10" y1="11" x2="10" y2="17"/>
              <line x1="14" y1="11" x2="14" y2="17"/>
            </svg>
          </div>
          <h3 class="action-title">清空数据</h3>
        </div>
        <p class="action-desc">删除所有合同记录和附件，但保留用户账号和系统配置。操作前建议先导出备份</p>
        <button class="btn-danger" :disabled="clearing" @click="confirmClear">
          <span v-if="clearing" class="loading-spinner"></span>
          <span v-else>清空所有数据</span>
        </button>
      </div>
    </div>

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click.self="showConfirmDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">确认清空数据</h3>
        </div>
        <div class="dialog-body">
          <p class="dialog-warning">此操作将永久删除以下数据：</p>
          <ul class="dialog-list">
            <li>所有合同记录（{{ info.contract_count }} 条）</li>
            <li>所有上传的附件文件（{{ info.uploads_count }} 个）</li>
            <li>所有通知发送记录</li>
          </ul>
          <p class="dialog-note">用户账号和系统配置将被保留。建议在清空前先导出备份。</p>
          <p class="dialog-confirm-text">请输入 <strong>清空数据</strong> 以确认：</p>
          <input v-model="confirmText" type="text" class="dialog-input" placeholder="清空数据" />
        </div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showConfirmDialog = false">取消</button>
          <button class="btn-danger" :disabled="confirmText !== '清空数据' || clearing" @click="clearData">
            <span v-if="clearing" class="loading-spinner"></span>
            <span v-else>确认清空</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 结果提示对话框 -->
    <div v-if="showResultDialog" class="dialog-overlay" @click.self="showResultDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">{{ resultTitle }}</h3>
        </div>
        <div class="dialog-body">
          <p class="dialog-result">{{ resultMessage }}</p>
        </div>
        <div class="dialog-actions">
          <button class="btn-primary" @click="handleResultClose">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const info = reactive({
  db_size: 0,
  db_size_mb: 0,
  uploads_count: 0,
  uploads_size: 0,
  uploads_size_mb: 0,
  contract_count: 0,
  user_count: 0
})

const exporting = ref(false)
const importing = ref(false)
const clearing = ref(false)
const fileInput = ref(null)

const showConfirmDialog = ref(false)
const confirmText = ref('')

const showResultDialog = ref(false)
const resultTitle = ref('')
const resultMessage = ref('')

async function loadInfo() {
  try {
    const res = await api.get('/api/backup/info')
    Object.assign(info, res.data)
  } catch (e) {
    console.error('加载备份信息失败:', e)
  }
}

async function exportBackup() {
  exporting.value = true
  try {
    const res = await api.get('/api/backup/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    const now = new Date()
    const pad = (n) => String(n).padStart(2, '0')
    link.download = `backup_${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('备份导出成功')
  } catch (e) {
    ElMessage.error('备份导出失败')
    console.error(e)
  } finally {
    exporting.value = false
  }
}

async function importBackup(event) {
  const file = event.target.files[0]
  if (!file) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/api/backup/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    resultTitle.value = '导入成功'
    resultMessage.value = res.data.message || '备份导入成功，请重新登录'
    showResultDialog.value = true
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '备份导入失败')
    console.error(e)
  } finally {
    importing.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

function confirmClear() {
  confirmText.value = ''
  showConfirmDialog.value = true
}

async function clearData() {
  clearing.value = true
  try {
    const res = await api.post('/api/backup/clear')
    ElMessage.success(res.data.message || '数据已清空')
    showConfirmDialog.value = false
    await loadInfo()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '清空数据失败')
    console.error(e)
  } finally {
    clearing.value = false
  }
}

function handleResultClose() {
  showResultDialog.value = false
  // 导入成功后重新加载页面
  window.location.reload()
}

onMounted(() => {
  loadInfo()
})
</script>

<style scoped>
.backup-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

/* 信息卡片 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}

.info-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--brand-foreground);
  line-height: 1.2;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--brand-muted-foreground);
  margin-top: 4px;
}

/* 操作卡片 */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 1024px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}

.action-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.export-icon {
  background: #dcfce7;
  color: #16a34a;
}

.import-icon {
  background: #dbeafe;
  color: #2563eb;
}

.danger-icon {
  background: #fee2e2;
  color: #dc2626;
}

.action-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.action-desc {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
  line-height: 1.5;
  flex: 1;
}

/* 按钮 */
.btn-primary,
.btn-warning,
.btn-danger,
.btn-cancel {
  padding: 10px 20px;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: var(--brand-primary);
  color: white;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-cancel {
  background: var(--brand-muted);
  color: var(--brand-foreground);
}

.btn-primary:hover:not(:disabled),
.btn-warning:hover:not(:disabled),
.btn-danger:hover:not(:disabled),
.btn-cancel:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled,
.btn-warning:disabled,
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--brand-card);
  border-radius: var(--radius-lg);
  max-width: 500px;
  width: 90%;
  max-height: 85vh;
  overflow-y: auto;
}

.dialog-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--brand-border);
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.dialog-body {
  padding: 20px 24px;
}

.dialog-warning {
  font-size: 0.9375rem;
  color: var(--brand-foreground);
  margin-bottom: 12px;
}

.dialog-list {
  margin: 0 0 16px 0;
  padding-left: 24px;
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.dialog-list li {
  margin-bottom: 6px;
}

.dialog-note {
  font-size: 0.8125rem;
  color: #d97706;
  background: #fef3c7;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
}

.dialog-confirm-text {
  font-size: 0.875rem;
  color: var(--brand-foreground);
  margin-bottom: 8px;
}

.dialog-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-md);
  font-size: 0.9375rem;
  color: var(--brand-foreground);
  background: var(--brand-card);
  box-sizing: border-box;
}

.dialog-input:focus {
  outline: none;
  border-color: var(--brand-ring);
}

.dialog-result {
  font-size: 0.9375rem;
  color: var(--brand-foreground);
  line-height: 1.6;
}

.dialog-actions {
  padding: 16px 24px;
  border-top: 1px solid var(--brand-border);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
