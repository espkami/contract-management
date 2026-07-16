<template>
  <div class="user-management">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">用户管理</h2>
        <span class="user-count">共 {{ total }} 位用户</span>
      </div>
      <button class="btn-primary" @click="openDialog()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新建用户
      </button>
    </div>

    <!-- User Table -->
    <div class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>用户信息</th>
            <th>邮箱</th>
            <th class="text-center">角色</th>
            <th class="text-center">状态</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody v-loading="loading">
          <tr v-for="user in list" :key="user.id">
            <td>
              <div class="user-info">
                <div class="user-avatar">{{ user.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
                <div class="user-details">
                  <span class="user-name">{{ user.username }}</span>
                  <span class="user-id">ID: {{ user.id }}</span>
                </div>
              </div>
            </td>
            <td class="muted">{{ user.email }}</td>
            <td class="text-center">
              <span :class="['role-badge', user.role]">
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td class="text-center">
              <button
                :class="['status-toggle', { active: user.is_active }]"
                @click="toggleActive(user)"
              >
                <span class="status-dot"></span>
                <span class="status-label">{{ user.is_active ? '启用' : '禁用' }}</span>
              </button>
            </td>
            <td class="text-center">
              <button class="action-btn" @click="openDialog(user)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                编辑
              </button>
              <button class="action-btn danger" @click="del(user)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dialog -->
    <div v-if="dlgVisible" class="dialog-overlay" @click.self="dlgVisible = false">
      <div class="dialog">
        <div class="dialog-header">
          <h3 class="dialog-title">{{ editRow ? '编辑用户' : '新建用户' }}</h3>
          <button class="dialog-close" @click="dlgVisible = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <form class="dialog-body" @submit.prevent="saveUser">
          <div class="form-group">
            <label class="form-label required">用户名</label>
            <input
              v-model="dlgForm.username"
              type="text"
              class="form-input"
              placeholder="请输入用户名"
              :disabled="!!editRow"
            />
          </div>
          <div class="form-group">
            <label class="form-label required">邮箱</label>
            <input
              v-model="dlgForm.email"
              type="email"
              class="form-input"
              placeholder="请输入邮箱地址"
            />
          </div>
          <div class="form-group">
            <label class="form-label">角色</label>
            <select v-model="dlgForm.role" class="form-select">
              <option value="admin">管理员</option>
              <option value="manager">管理者</option>
              <option value="viewer">查看者</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" :class="{ required: !editRow }">密码</label>
            <input
              v-model="dlgForm.password"
              type="password"
              class="form-input"
              :placeholder="editRow ? '留空则不修改密码' : '请输入密码'"
            />
          </div>
        </form>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="dlgVisible = false">取消</button>
          <button class="btn-submit" :disabled="saving" @click="saveUser">
            <span v-if="saving" class="loading-spinner"></span>
            <span v-else>确定</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import api from '../../api/index'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dlgVisible = ref(false)
const editRow = ref(null)

const dlgForm = reactive({
  username: '',
  email: '',
  role: 'viewer',
  password: ''
})

function getRoleName(role) {
  const roles = { admin: '管理员', manager: '管理者', viewer: '查看者' }
  return roles[role] || '查看者'
}

async function load() {
  loading.value = true
  try {
    const res = await api.get('/api/users/')
    list.value = res.data.items || []
    total.value = res.data.total || list.value.length
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

function openDialog(row = null) {
  editRow.value = row
  if (row) {
    Object.assign(dlgForm, { ...row, password: '' })
  } else {
    Object.assign(dlgForm, { username: '', email: '', role: 'viewer', password: '' })
  }
  dlgVisible.value = true
}

async function saveUser() {
  if (!dlgForm.username || !dlgForm.email) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (!editRow.value && !dlgForm.password) {
    ElMessage.warning('请输入密码')
    return
  }

  saving.value = true
  try {
    if (editRow.value) {
      const body = { email: dlgForm.email, role: dlgForm.role }
      if (dlgForm.password) body.password = dlgForm.password
      await api.put(`/api/users/${editRow.value.id}`, body)
      ElMessage.success('修改成功')
    } else {
      await api.post('/api/users/', dlgForm)
      ElMessage.success('创建成功')
    }
    dlgVisible.value = false
    load()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function toggleActive(user) {
  try {
    await api.put(`/api/users/${user.id}`, { is_active: !user.is_active })
    user.is_active = !user.is_active
    ElMessage.success(user.is_active ? '已启用' : '已禁用')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function del(user) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${user.username}」？`, '警告', { type: 'warning' })
    await api.delete(`/api/users/${user.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(load)
</script>

<style scoped>
.user-management {
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

.user-count {
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

.btn-primary:hover {
  opacity: 0.9;
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

.muted {
  color: var(--brand-muted-foreground);
}

.text-center {
  text-align: center;
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--brand-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: var(--brand-foreground);
}

.user-id {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

/* Role Badge */
.role-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge.admin {
  background: #fee2e2;
  color: #991b1b;
}

.role-badge.manager {
  background: #fef3c7;
  color: #92400e;
}

.role-badge.viewer {
  background: #dbeafe;
  color: #1e40af;
}

/* Status Toggle */
.status-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--brand-muted);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-toggle.active {
  background: #dcfce7;
  border-color: #16a34a;
  color: #166534;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

/* Action Buttons */
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: none;
  border: none;
  color: var(--brand-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.action-btn:hover {
  opacity: 0.8;
}

.action-btn.danger {
  color: #dc2626;
}

/* Dialog */
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
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--brand-border);
}

.dialog-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.dialog-close {
  background: none;
  border: none;
  padding: 4px;
  color: var(--brand-muted-foreground);
  cursor: pointer;
}

.dialog-close:hover {
  color: var(--brand-foreground);
}

.dialog-body {
  padding: 20px;
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

.form-input,
.form-select {
  padding: 10px 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: white;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--brand-ring);
}

.form-input:disabled {
  background: var(--brand-muted);
  cursor: not-allowed;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--brand-border);
}

.btn-cancel {
  padding: 10px 24px;
  background: white;
  color: var(--brand-foreground);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-cancel:hover {
  background: var(--brand-muted);
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
  min-width: 80px;
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>