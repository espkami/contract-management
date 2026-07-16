<template>
  <div class="notification-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">通知管理</h2>
        <span class="contract-count">共 {{ contracts.length }} 个待提醒合同</span>
      </div>
      <button class="btn-primary" @click="sendNotification" :disabled="selectedContracts.length === 0 || sending">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
        发送通知
      </button>
    </div>

    <div class="main-content">
      <div class="contract-section">
        <h3 class="section-title">待提醒合同列表</h3>
        <div class="contract-list">
          <div
            v-for="contract in contracts"
            :key="contract.id"
            :class="['contract-item', { selected: selectedContracts.includes(contract.id) }]"
            @click="toggleSelect(contract.id)"
          >
            <div class="contract-checkbox">
              <div :class="['checkbox', { checked: selectedContracts.includes(contract.id) }]">
                <svg v-if="selectedContracts.includes(contract.id)" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>
            <div class="contract-info">
              <p class="contract-title">{{ contract.title }}</p>
              <p class="contract-meta">{{ contract.contract_no }} · {{ contract.contract_type }}</p>
            </div>
            <div class="contract-date">
              <span class="date-value">{{ contract.end_date }}</span>
              <span :class="['days-badge', { expired: contract.days_left <= 0, warning: contract.days_left > 0 && contract.days_left <= 30 }]">
                {{ contract.days_left <= 0 ? '已过期' : `剩${contract.days_left}天` }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="send-section">
        <h3 class="section-title">发送设置</h3>
        <div class="send-form">
          <div class="form-group">
            <label class="form-label">接收邮箱</label>
            <textarea
              v-model="sendForm.toEmails"
              class="form-textarea"
              placeholder="请输入接收邮箱，多个邮箱用逗号或换行分隔（可选）"
              rows="2"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">企业微信通知</label>
            <div class="checkbox-row">
              <div :class="['checkbox', { checked: sendForm.sendWechat }]" @click="sendForm.sendWechat = !sendForm.sendWechat">
                <svg v-if="sendForm.sendWechat" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <span class="checkbox-label">发送到企业微信群（需先在通知配置中设置 Webhook）</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Server酱（推送到个人微信）</label>
            <div class="checkbox-row">
              <div :class="['checkbox', { checked: sendForm.sendServerchan }]" @click="sendForm.sendServerchan = !sendForm.sendServerchan">
                <svg v-if="sendForm.sendServerchan" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <span class="checkbox-label">推送到已配置的微信用户（需先在通知配置中设置 SendKey）</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">自定义消息</label>
            <textarea
              v-model="sendForm.message"
              class="form-textarea"
              placeholder="可选：添加自定义提醒消息"
              rows="3"
            ></textarea>
          </div>
          <div class="preview-section">
            <h4 class="preview-title">邮件预览</h4>
            <div class="email-preview">
              <div class="preview-header">
                <span class="preview-label">主题：</span>
                <span class="preview-value">【合同到期提醒】</span>
              </div>
              <div class="preview-body">
                <p>{{ sendForm.message || '以下合同即将到期，请及时处理：' }}</p>
                <table class="preview-table">
                  <thead>
                    <tr>
                      <th>合同名称</th>
                      <th>到期日期</th>
                      <th>状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="cid in selectedContracts.slice(0, 3)" :key="cid">
                      <td>{{ getContract(cid)?.title || '-' }}</td>
                      <td>{{ getContract(cid)?.end_date || '-' }}</td>
                      <td>{{ getContract(cid)?.days_left <= 0 ? '已过期' : `剩${getContract(cid)?.days_left}天` }}</td>
                    </tr>
                    <tr v-if="selectedContracts.length > 3">
                      <td colspan="3" class="text-center">... 还有 {{ selectedContracts.length - 3 }} 个合同</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="sendResult" class="result-overlay" @click.self="sendResult = null">
      <div class="result-dialog">
        <div class="result-header">
          <div :class="['result-icon', sendResult.success > 0 ? 'success' : 'error']">
            <svg v-if="sendResult.success > 0" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          <h3 class="result-title">{{ sendResult.success > 0 ? '发送成功' : '发送失败' }}</h3>
        </div>
        <div class="result-body">
          <p v-if="sendResult.success > 0">邮件成功发送：{{ sendResult.success }} 封</p>
          <p v-if="sendResult.failed > 0">邮件发送失败：{{ sendResult.failed }} 封</p>
          <p v-if="sendResult.wechat_success">企业微信：发送成功</p>
          <p v-if="sendResult.wechat_error && !sendResult.wechat_success" class="error-text">企业微信：{{ sendResult.wechat_error }}</p>
          <p v-if="sendResult.serverchan_success > 0">Server酱：成功推送 {{ sendResult.serverchan_success }} 条</p>
          <p v-if="sendResult.serverchan_errors && sendResult.serverchan_errors.length > 0" class="error-text">Server酱失败：{{ sendResult.serverchan_errors[0] }}</p>
          <div v-if="sendResult.failed_emails && sendResult.failed_emails.length > 0" class="failed-list">
            <h4>失败详情：</h4>
            <ul>
              <li v-for="(item, index) in sendResult.failed_emails" :key="index">
                {{ item.email }}：{{ item.error }}
              </li>
            </ul>
          </div>
        </div>
        <div class="result-footer">
          <button class="btn-close" @click="sendResult = null">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const contracts = ref([])
const selectedContracts = ref([])
const sending = ref(false)
const sendResult = ref(null)

const sendForm = reactive({
  toEmails: '',
  message: '',
  sendWechat: false,
  sendServerchan: false
})

function getContract(id) {
  return contracts.value.find(c => c.id === id)
}

function toggleSelect(id) {
  const index = selectedContracts.value.indexOf(id)
  if (index > -1) {
    selectedContracts.value.splice(index, 1)
  } else {
    selectedContracts.value.push(id)
  }
}

function selectAll() {
  if (selectedContracts.value.length === contracts.value.length) {
    selectedContracts.value = []
  } else {
    selectedContracts.value = contracts.value.map(c => c.id)
  }
}

async function loadContracts() {
  try {
    const res = await api.get('/api/notifications/pending-contracts')
    contracts.value = res.data || []
  } catch (error) {
    console.error('Failed to load contracts:', error)
  }
}

async function sendNotification() {
  // 至少需要选择一种发送方式
  const hasEmail = sendForm.toEmails.trim() && sendForm.toEmails.split(/[,\n]/).filter(e => e.trim()).length > 0
  if (!hasEmail && !sendForm.sendWechat && !sendForm.sendServerchan) {
    ElMessage.warning('请选择至少一种通知方式：填写接收邮箱 或 勾选企业微信 / Server酱')
    return
  }

  if (hasEmail && !sendForm.sendWechat) {
    // 仅邮件发送时需要验证邮箱格式
    const emails = sendForm.toEmails.split(/[,\n]/).map(e => e.trim()).filter(e => e)
    if (emails.some(e => !e.includes('@'))) {
      ElMessage.warning('请输入有效的邮箱地址')
      return
    }
  }

  sending.value = true
  try {
    const res = await api.post('/api/notifications/send', {
      contract_ids: selectedContracts.value,
      to_emails: hasEmail ? sendForm.toEmails.split(/[,\n]/).map(e => e.trim()).filter(e => e) : [],
      message: sendForm.message || undefined,
      send_wechat: sendForm.sendWechat,
      send_serverchan: sendForm.sendServerchan
    })
    sendResult.value = res.data
  } catch (error) {
    const msg = error.response?.data?.detail || '发送失败'
    ElMessage.error(msg)
  } finally {
    sending.value = false
  }
}

onMounted(loadContracts)
</script>

<style scoped>
.notification-management {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.contract-count {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
  padding: 4px 12px;
  background: var(--brand-muted);
  border-radius: var(--radius-full);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

.contract-section,
.send-section {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brand-foreground);
  margin-bottom: 16px;
}

.contract-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 500px;
  overflow-y: auto;
}

.contract-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}

.contract-item:hover {
  background: var(--brand-muted);
}

.contract-item.selected {
  border-color: var(--brand-primary);
  background: rgba(45, 125, 112, 0.05);
}

.contract-checkbox {
  flex-shrink: 0;
}

.checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid var(--brand-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.checkbox.checked {
  background: var(--brand-primary);
  border-color: var(--brand-primary);
}

.contract-info {
  flex: 1;
  min-width: 0;
}

.contract-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
  margin-bottom: 2px;
}

.contract-meta {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.contract-date {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.date-value {
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.days-badge {
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: 500;
  background: #dbeafe;
  color: #1e40af;
}

.days-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.days-badge.expired {
  background: #fee2e2;
  color: #991b1b;
}

.send-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
}

.form-label.required::after {
  content: '*';
  color: #dc2626;
  margin-left: 4px;
}

.form-textarea {
  padding: 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: white;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--brand-ring);
}

.form-textarea::placeholder {
  color: var(--brand-muted-foreground);
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--brand-muted);
  border-radius: var(--radius-lg);
}

.checkbox-label {
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.error-text {
  color: #dc2626 !important;
}

.preview-section {
  margin-top: 8px;
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--brand-muted-foreground);
  margin-bottom: 12px;
}

.email-preview {
  background: white;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 16px;
  font-size: 0.875rem;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--brand-border);
}

.preview-label {
  color: var(--brand-muted-foreground);
}

.preview-value {
  font-weight: 600;
  color: var(--brand-foreground);
}

.preview-body p {
  color: var(--brand-foreground);
  line-height: 1.6;
  margin-bottom: 12px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.preview-table th {
  text-align: left;
  padding: 8px;
  background: var(--brand-muted);
  color: var(--brand-muted-foreground);
  font-weight: 500;
}

.preview-table td {
  padding: 8px;
  border-bottom: 1px solid var(--brand-border);
  color: var(--brand-foreground);
}

.text-center {
  text-align: center;
  color: var(--brand-muted-foreground);
}

.result-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.result-dialog {
  background: var(--brand-card);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 420px;
  overflow: hidden;
}

.result-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--brand-border);
}

.result-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.result-icon.success {
  background: #dcfce7;
  color: #16a34a;
}

.result-icon.error {
  background: #fee2e2;
  color: #dc2626;
}

.result-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.result-body {
  padding: 20px;
}

.result-body p {
  font-size: 0.875rem;
  color: var(--brand-foreground);
  margin-bottom: 8px;
}

.failed-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--brand-border);
}

.failed-list h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brand-foreground);
  margin-bottom: 8px;
}

.failed-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.failed-list li {
  font-size: 0.8rem;
  color: #dc2626;
  padding: 4px 0;
  border-bottom: 1px solid var(--brand-border);
}

.result-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--brand-border);
  display: flex;
  justify-content: flex-end;
}

.btn-close {
  padding: 10px 24px;
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.btn-close:hover {
  opacity: 0.9;
}
</style>