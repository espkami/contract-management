<template>
  <div class="contract-form">
    <!-- Header -->
    <div class="form-header">
      <button class="back-btn" @click="$router.back()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        返回列表
      </button>
      <h2 class="form-title">{{ isEdit ? '编辑合同' : '合同登记' }}</h2>
    </div>

    <!-- Form Card -->
    <div class="form-card">
      <form @submit.prevent="save">
        <!-- Section: Basic Info -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label required">合同编号</label>
              <input
                v-model="form.contract_no"
                type="text"
                class="form-input"
                placeholder="系统自动生成或手动输入"
              />
            </div>
            <div class="form-group">
              <label class="form-label required">合同名称</label>
              <input
                v-model="form.title"
                type="text"
                class="form-input"
                placeholder="请输入合同名称"
              />
            </div>
            <div class="form-group">
              <label class="form-label required">合同类型</label>
              <select v-model="form.contract_type" class="form-select">
                <option value="">请选择合同类型</option>
                <option value="维修合同">维修合同</option>
                <option value="维保合同">维保合同</option>
                <option value="外修合同">外修合同</option>
                <option value="装修合同">装修合同</option>
                <option value="商业合同">商业合同</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section: Parties -->
        <div class="form-section">
          <h3 class="section-title">签约双方</h3>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label required">甲方（我方）</label>
              <input
                v-model="form.party_a"
                type="text"
                class="form-input"
                placeholder="请输入甲方名称"
              />
            </div>
            <div class="form-group">
              <label class="form-label required">乙方（对方）</label>
              <input
                v-model="form.party_b"
                type="text"
                class="form-input"
                placeholder="请输入乙方名称"
              />
            </div>
          </div>
        </div>

        <!-- Section: Dates & Amount -->
        <div class="form-section">
          <h3 class="section-title">金额与日期</h3>
          <div class="form-grid-4">
            <div class="form-group">
              <label class="form-label">合同金额（元）</label>
              <input
                v-model.number="form.amount"
                type="number"
                step="0.01"
                min="0"
                class="form-input"
                placeholder="0.00"
              />
            </div>
            <div class="form-group">
              <label class="form-label">签订日期</label>
              <input
                v-model="form.sign_date"
                type="date"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label required">开始日期</label>
              <input
                v-model="form.start_date"
                type="date"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="form-label required">到期日期</label>
              <input
                v-model="form.end_date"
                type="date"
                class="form-input"
              />
            </div>
          </div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">提前提醒（天）</label>
              <input
                v-model.number="form.remind_days"
                type="number"
                min="1"
                max="365"
                class="form-input"
                placeholder="30"
              />
              <p class="form-hint">合同到期前多少天开始提醒</p>
            </div>
          </div>
        </div>

        <!-- Section: Attachment -->
        <div class="form-section">
          <h3 class="section-title">合同附件</h3>
          <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
            <input
              ref="fileInput"
              type="file"
              accept=".pdf,.doc,.docx,.jpg,.png"
              style="display: none"
              @change="handleFileChange"
            />
            <div v-if="!form.file_path" class="upload-content">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--brand-muted-foreground)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <p class="upload-text">拖拽文件到此处，或点击上传</p>
              <p class="upload-hint">支持 PDF、Word、图片格式，最大 50MB</p>
            </div>
            <div v-else class="upload-success">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <span class="upload-filename">{{ form.file_path }}</span>
            </div>
          </div>
          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ uploadProgress }}%</span>
          </div>
        </div>

        <!-- Section: Remarks -->
        <div class="form-section">
          <h3 class="section-title">备注信息</h3>
          <div class="form-group">
            <textarea
              v-model="form.remark"
              class="form-textarea"
              placeholder="请输入备注信息（选填）"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button type="submit" class="btn-submit" :disabled="saving">
            <span v-if="saving" class="loading-spinner"></span>
            <span v-else>{{ isEdit ? '保存修改' : '提交登记' }}</span>
          </button>
          <button type="button" class="btn-cancel" @click="$router.back()">取消</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/index'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const fileInput = ref()
const isEdit = computed(() => !!route.params.id && route.path.includes('edit'))
const saving = ref(false)
const uploadProgress = ref(0)

const form = reactive({
  contract_no: `HT-${dayjs().format('YYYYMMDD')}-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
  title: '',
  party_a: '',
  party_b: '',
  amount: null,
  contract_type: '',
  sign_date: dayjs().format('YYYY-MM-DD'),
  start_date: '',
  end_date: '',
  remind_days: 30,
  remark: '',
  file_path: ''
})

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (file) uploadFile(file)
}

function handleDrop(e) {
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

async function uploadFile(file) {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件不能超过50MB')
    return
  }

  uploadProgress.value = 0
  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await api.post('/api/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        uploadProgress.value = Math.round((e.loaded / e.total) * 100)
      }
    })
    form.file_path = res.data.file_path || file.name
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function save() {
  if (!form.title || !form.party_a || !form.party_b || !form.contract_type || !form.start_date || !form.end_date) {
    ElMessage.warning('请填写必填项')
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/api/contracts/${route.params.id}`, form)
      ElMessage.success('修改成功')
    } else {
      await api.post('/api/contracts/', form)
      ElMessage.success('登记成功')
    }
    router.push('/contracts')
  } catch (error) {
    const msg = error.response?.data?.detail || '操作失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res = await api.get(`/api/contracts/${route.params.id}`)
      Object.assign(form, res.data)
    } catch (error) {
      ElMessage.error('加载合同信息失败')
      router.back()
    }
  }
})
</script>

<style scoped>
.contract-form {
  max-width: 900px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
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

.form-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.form-card {
  background: var(--brand-card);
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-of-type {
  margin-bottom: 0;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--brand-foreground);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--brand-border);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

@media (max-width: 1024px) {
  .form-grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .form-grid,
  .form-grid-4 {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
  margin-bottom: 6px;
}

.form-label.required::after {
  content: '*';
  color: #dc2626;
  margin-left: 4px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: white;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--brand-ring);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--brand-muted-foreground);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 36px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
  margin-top: 4px;
}

/* Upload */
.upload-area {
  border: 2px dashed var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.upload-area:hover {
  border-color: var(--brand-primary);
  background: rgba(45, 125, 112, 0.02);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-text {
  font-size: 0.875rem;
  color: var(--brand-foreground);
}

.upload-hint {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

.upload-success {
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-filename {
  font-size: 0.875rem;
  color: var(--brand-primary);
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--brand-muted);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--brand-primary);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
}

/* Actions */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--brand-border);
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
  min-width: 120px;
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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