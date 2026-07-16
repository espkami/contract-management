<template>
  <div class="settings-page">
    <div class="toolbar">
      <div class="toolbar-left">
        <h2 class="page-title">通知配置</h2>
      </div>
    </div>

    <!-- 自动提醒开关 -->
    <div class="settings-card highlight-card">
      <div class="card-header">
        <div class="card-header-row">
          <h3 class="card-title">自动提醒</h3>
          <span :class="['status-badge', { active: autoRemind.enabled }]">
            {{ autoRemind.enabled ? '已开启' : '未开启' }}
          </span>
        </div>
        <p class="card-desc">开启后，系统每天自动检查快到期合同，并通过下方配置的渠道发送提醒</p>
      </div>

      <div class="auto-remind-form">
        <div class="form-group">
          <label class="form-label">提前提醒天数</label>
          <input v-model.number="autoRemind.remind_days" type="number" min="1" max="365" class="form-input auto-days-input" />
          <span class="form-hint-inline">天内到期的合同将被提醒</span>
        </div>
        <div class="form-group">
          <label class="form-label">上次执行</label>
          <span class="last-run-text">{{ autoRemind.last_run || '尚未执行' }}</span>
        </div>
      </div>

      <div class="card-actions">
        <button class="btn-toggle" :class="{ on: autoRemind.enabled }" @click="toggleAutoRemind">
          {{ autoRemind.enabled ? '关闭自动提醒' : '开启自动提醒' }}
        </button>
        <button class="btn-save" :disabled="autoSaving" @click="saveAutoRemind">
          <span v-if="autoSaving" class="loading-spinner"></span>
          <span v-else>保存设置</span>
        </button>
        <button class="btn-test" :disabled="autoTriggering" @click="triggerRemind">
          <span v-if="autoTriggering" class="loading-spinner"></span>
          <span v-else>立即执行一次</span>
        </button>
      </div>
    </div>

    <!-- Server酱配置 -->
    <div class="settings-card">
      <div class="card-header">
        <div class="card-header-row">
          <h3 class="card-title">Server酱（推送到个人微信）</h3>
          <span :class="['status-badge', { active: serverchanConfig.configured }]">
            {{ serverchanConfig.configured ? `已配置 ${serverchanConfig.key_count} 个` : '未配置' }}
          </span>
        </div>
        <p class="card-desc">通过 Server酱 将合同到期提醒推送到个人微信，支持多个 SendKey（每行一个）</p>
      </div>

      <div class="form-group">
        <label class="form-label">SendKey</label>
        <textarea v-model="serverchanForm.serverchan_keys" class="form-textarea" rows="3" placeholder="每行输入一个 SendKey，例如：SCT1234567890abcdef"></textarea>
        <p class="form-hint">访问 sct.ftqq.com 注册并绑定微信，获取 SendKey。多个用户各一行。</p>
      </div>

      <div class="card-actions">
        <button class="btn-save" :disabled="serverchanSaving" @click="saveServerchan">
          <span v-if="serverchanSaving" class="loading-spinner"></span>
          <span v-else>保存配置</span>
        </button>
        <button class="btn-test" :disabled="serverchanTesting || !serverchanConfig.configured" @click="testServerchan">
          <span v-if="serverchanTesting" class="loading-spinner"></span>
          <span v-else>发送测试</span>
        </button>
      </div>
    </div>

    <!-- SMTP 邮件配置 -->
    <div class="settings-card">
      <div class="card-header">
        <div class="card-header-row">
          <h3 class="card-title">邮件通知</h3>
          <span :class="['status-badge', { active: smtpConfig.configured }]">
            {{ smtpConfig.configured ? '已配置' : '未配置' }}
          </span>
        </div>
        <p class="card-desc">配置邮件服务器后，系统可以通过邮件发送合同到期提醒通知</p>
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label class="form-label required">SMTP 服务器地址</label>
          <input v-model="smtpForm.smtp_host" type="text" class="form-input" placeholder="例如：smtp.qq.com" />
        </div>
        <div class="form-group">
          <label class="form-label required">SMTP 端口</label>
          <input v-model.number="smtpForm.smtp_port" type="number" class="form-input" placeholder="例如：465" />
        </div>
        <div class="form-group">
          <label class="form-label required">发件邮箱账号</label>
          <input v-model="smtpForm.smtp_user" type="email" class="form-input" placeholder="例如：your_email@qq.com" />
        </div>
        <div class="form-group">
          <label class="form-label">SMTP 授权码</label>
          <input v-model="smtpForm.smtp_password" type="password" class="form-input" placeholder="留空则不修改，输入则更新" />
          <p class="form-hint">授权码不是邮箱密码，需在邮箱设置中开启 SMTP 后获取</p>
        </div>
      </div>

      <div class="card-actions">
        <button class="btn-save" :disabled="smtpSaving" @click="saveSmtp">
          <span v-if="smtpSaving" class="loading-spinner"></span>
          <span v-else>保存配置</span>
        </button>
        <button class="btn-test" :disabled="emailTesting || !smtpConfig.configured" @click="testSmtp">
          <span v-if="emailTesting" class="loading-spinner"></span>
          <span v-else>发送测试</span>
        </button>
      </div>
    </div>

    <!-- 企业微信配置 -->
    <div class="settings-card">
      <div class="card-header">
        <div class="card-header-row">
          <h3 class="card-title">企业微信通知</h3>
          <span :class="['status-badge', { active: wechatConfig.configured }]">
            {{ wechatConfig.configured ? '已配置' : '未配置' }}
          </span>
        </div>
        <p class="card-desc">配置企业微信群机器人 Webhook，系统可以将合同到期提醒推送到企业微信群</p>
      </div>

      <div class="form-group wechat-url-group">
        <label class="form-label required">Webhook 地址</label>
        <input v-model="wechatForm.wechat_webhook_url" type="text" class="form-input" placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx" />
        <p class="form-hint">在企业微信群中添加机器人，获取 Webhook 地址</p>
      </div>

      <div class="card-actions">
        <button class="btn-save" :disabled="wechatSaving" @click="saveWechat">
          <span v-if="wechatSaving" class="loading-spinner"></span>
          <span v-else>保存配置</span>
        </button>
        <button class="btn-test" :disabled="wechatTesting || !wechatConfig.configured" @click="testWechat">
          <span v-if="wechatTesting" class="loading-spinner"></span>
          <span v-else>发送测试</span>
        </button>
      </div>
    </div>

    <!-- 配置参考 -->
    <div class="settings-card">
      <div class="card-header">
        <h3 class="card-title">配置参考</h3>
      </div>
      <div class="ref-tabs">
        <button :class="['ref-tab', { active: activeTab === 'sc' }]" @click="activeTab = 'sc'">Server酱</button>
        <button :class="['ref-tab', { active: activeTab === 'smtp' }]" @click="activeTab = 'smtp'">邮件 SMTP</button>
        <button :class="['ref-tab', { active: activeTab === 'wechat' }]" @click="activeTab = 'wechat'">企业微信</button>
      </div>
      <div class="ref-content">
        <div v-if="activeTab === 'sc'" class="wechat-reference">
          <div class="wechat-steps">
            <div class="step"><div class="step-num">1</div><div class="step-content"><h4>注册 Server酱</h4><p>访问 sct.ftqq.com 注册账号</p></div></div>
            <div class="step"><div class="step-num">2</div><div class="step-content"><h4>绑定微信</h4><p>登录后在「发送消息」页面绑定微信</p></div></div>
            <div class="step"><div class="step-num">3</div><div class="step-content"><h4>复制 SendKey</h4><p>复制 SendKey 粘贴到上方配置框</p></div></div>
            <div class="step"><div class="step-num">4</div><div class="step-content"><h4>多个用户</h4><p>每个用户一个 SendKey，每行一个</p></div></div>
          </div>
        </div>
        <div v-else-if="activeTab === 'smtp'" class="smtp-reference">
          <table class="ref-table">
            <thead><tr><th>邮箱服务</th><th>SMTP 服务器</th><th>端口</th><th>说明</th></tr></thead>
            <tbody>
              <tr><td>QQ 邮箱</td><td>smtp.qq.com</td><td>465</td><td>需开启 SMTP，获取授权码</td></tr>
              <tr><td>163 邮箱</td><td>smtp.163.com</td><td>465</td><td>需开启 SMTP，获取授权码</td></tr>
              <tr><td>企业微信邮箱</td><td>smtp.exmail.qq.com</td><td>465</td><td>使用邮箱密码</td></tr>
              <tr><td>Outlook</td><td>smtp.office365.com</td><td>587</td><td>需使用 TLS 连接</td></tr>
            </tbody>
          </table>
        </div>
        <div v-else class="wechat-reference">
          <div class="wechat-steps">
            <div class="step"><div class="step-num">1</div><div class="step-content"><h4>打开企业微信群</h4><p>在企业微信中打开需要接收通知的群</p></div></div>
            <div class="step"><div class="step-num">2</div><div class="step-content"><h4>添加群机器人</h4><p>点击群右上角 ··· → 群机器人 → 添加机器人</p></div></div>
            <div class="step"><div class="step-num">3</div><div class="step-content"><h4>复制 Webhook 地址</h4><p>添加完成后，复制 Webhook 地址粘贴到上方配置框</p></div></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

const activeTab = ref('sc')

// SMTP
const smtpForm = reactive({ smtp_host: '', smtp_port: 465, smtp_user: '', smtp_password: '' })
const smtpConfig = reactive({ configured: false })
const smtpSaving = ref(false)
const emailTesting = ref(false)
const testEmail = ref('')

// 企业微信
const wechatForm = reactive({ wechat_webhook_url: '' })
const wechatConfig = reactive({ configured: false })
const wechatSaving = ref(false)
const wechatTesting = ref(false)

// Server酱
const serverchanForm = reactive({ serverchan_keys: '' })
const serverchanConfig = reactive({ configured: false, key_count: 0 })
const serverchanSaving = ref(false)
const serverchanTesting = ref(false)

// 自动提醒
const autoRemind = reactive({ enabled: false, remind_days: 30, last_run: null })
const autoSaving = ref(false)
const autoTriggering = ref(false)

async function loadSmtpConfig() {
  try {
    const res = await api.get('/api/settings/smtp')
    smtpForm.smtp_host = res.data.smtp_host || ''
    smtpForm.smtp_port = res.data.smtp_port || 465
    smtpForm.smtp_user = res.data.smtp_user || ''
    smtpForm.smtp_password = res.data.smtp_password || ''
    smtpConfig.configured = res.data.configured
  } catch (e) { console.error(e) }
}

async function loadWechatConfig() {
  try {
    const res = await api.get('/api/settings/wechat')
    wechatForm.wechat_webhook_url = res.data.wechat_webhook_url || ''
    wechatConfig.configured = res.data.configured
  } catch (e) { console.error(e) }
}

async function loadServerchanConfig() {
  try {
    const res = await api.get('/api/settings/serverchan')
    serverchanForm.serverchan_keys = res.data.serverchan_keys || ''
    serverchanConfig.configured = res.data.configured
    serverchanConfig.key_count = res.data.key_count
  } catch (e) { console.error(e) }
}

async function loadAutoRemind() {
  try {
    const res = await api.get('/api/settings/auto-remind')
    autoRemind.enabled = res.data.enabled
    autoRemind.remind_days = res.data.remind_days
    autoRemind.last_run = res.data.last_run
  } catch (e) { console.error(e) }
}

async function saveSmtp() {
  if (!smtpForm.smtp_host || !smtpForm.smtp_user) { ElMessage.warning('请填写 SMTP 服务器地址和发件邮箱'); return }
  smtpSaving.value = true
  try {
    await api.put('/api/settings/smtp', smtpForm)
    ElMessage.success('邮件配置保存成功')
    loadSmtpConfig()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { smtpSaving.value = false }
}

async function saveWechat() {
  if (!wechatForm.wechat_webhook_url) { ElMessage.warning('请输入企业微信 Webhook 地址'); return }
  wechatSaving.value = true
  try {
    await api.put('/api/settings/wechat', wechatForm)
    ElMessage.success('企业微信配置保存成功')
    loadWechatConfig()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { wechatSaving.value = false }
}

async function saveServerchan() {
  serverchanSaving.value = true
  try {
    await api.put('/api/settings/serverchan', serverchanForm)
    ElMessage.success('Server酱配置保存成功')
    loadServerchanConfig()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { serverchanSaving.value = false }
}

async function saveAutoRemind() {
  autoSaving.value = true
  try {
    await api.put('/api/settings/auto-remind', { auto_remind_enabled: autoRemind.enabled, auto_remind_days: autoRemind.remind_days })
    ElMessage.success('自动提醒设置已保存')
  } catch (e) { ElMessage.error(e.response?.data?.detail || '保存失败') }
  finally { autoSaving.value = false }
}

function toggleAutoRemind() {
  autoRemind.enabled = !autoRemind.enabled
}

async function triggerRemind() {
  autoTriggering.value = true
  try {
    const res = await api.post('/api/notifications/auto-remind/trigger')
    const r = res.data.result
    let msg = '手动提醒已执行'
    if (r.email > 0) msg += `，邮件${r.email}封`
    if (r.wechat) msg += '，企业微信成功'
    if (r.serverchan > 0) msg += `，Server酱${r.serverchan}条`
    if (r.errors && r.errors.length > 0) {
      ElMessage.warning(msg)
      ElMessage.error(r.errors[0])
    } else if (r.message) {
      ElMessage.info(r.message)
    } else {
      ElMessage.success(msg)
    }
    loadAutoRemind()
  } catch (e) { ElMessage.error(e.response?.data?.detail || '执行失败') }
  finally { autoTriggering.value = false }
}

async function testSmtp() {
  if (!testEmail.value) { ElMessage.warning('请输入收件邮箱'); return }
  emailTesting.value = true
  try {
    const res = await api.post('/api/settings/smtp/test', { to_email: testEmail.value })
    ElMessage.success(res.data.message)
  } catch (e) { ElMessage.error(e.response?.data?.detail || '测试失败') }
  finally { emailTesting.value = false }
}

async function testWechat() {
  wechatTesting.value = true
  try {
    const res = await api.post('/api/settings/wechat/test')
    ElMessage.success(res.data.message)
  } catch (e) { ElMessage.error(e.response?.data?.detail || '测试失败') }
  finally { wechatTesting.value = false }
}

async function testServerchan() {
  serverchanTesting.value = true
  try {
    const res = await api.post('/api/settings/serverchan/test')
    ElMessage.success(res.data.message)
    if (res.data.errors && res.data.errors.length > 0) {
      ElMessage.warning(`部分失败: ${res.data.errors[0]}`)
    }
  } catch (e) { ElMessage.error(e.response?.data?.detail || '测试失败') }
  finally { serverchanTesting.value = false }
}

onMounted(() => {
  loadSmtpConfig()
  loadWechatConfig()
  loadServerchanConfig()
  loadAutoRemind()
})
</script>

<style scoped>
.settings-page { display: flex; flex-direction: column; gap: 16px; }
.toolbar { display: flex; justify-content: space-between; align-items: center; }
.toolbar-left { display: flex; align-items: center; gap: 16px; }
.page-title { font-size: 1.125rem; font-weight: 600; color: var(--brand-foreground); }

.status-badge { padding: 4px 12px; border-radius: var(--radius-full); font-size: 0.75rem; font-weight: 500; background: var(--brand-muted); color: var(--brand-muted-foreground); }
.status-badge.active { background: #dcfce7; color: #16a34a; }

.settings-card { background: var(--brand-card); border: 1px solid var(--brand-border); border-radius: var(--radius-lg); padding: 24px; }
.highlight-card { border-color: var(--brand-primary); border-width: 2px; }
.card-header { margin-bottom: 20px; }
.card-header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.card-title { font-size: 1rem; font-weight: 600; color: var(--brand-foreground); margin: 0; }
.card-desc { font-size: 0.8rem; color: var(--brand-muted-foreground); margin: 0; }

.auto-remind-form { display: flex; gap: 24px; margin-bottom: 16px; flex-wrap: wrap; }
.auto-days-input { width: 100px; }
.form-hint-inline { font-size: 0.8rem; color: var(--brand-muted-foreground); margin-left: 8px; }
.last-run-text { font-size: 0.875rem; color: var(--brand-muted-foreground); }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
.wechat-url-group { max-width: 600px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 0.875rem; font-weight: 500; color: var(--brand-foreground); }
.form-label.required::after { content: '*'; color: #dc2626; margin-left: 4px; }
.form-input { padding: 10px 12px; border: 1px solid var(--brand-border); border-radius: var(--radius-lg); font-size: 0.875rem; color: var(--brand-foreground); background: white; transition: border-color 0.2s ease; }
.form-input:focus { outline: none; border-color: var(--brand-ring); }
.form-input::placeholder { color: var(--brand-muted-foreground); }
.form-textarea { padding: 10px 12px; border: 1px solid var(--brand-border); border-radius: var(--radius-lg); font-size: 0.875rem; color: var(--brand-foreground); background: white; resize: vertical; font-family: inherit; }
.form-textarea:focus { outline: none; border-color: var(--brand-ring); }
.form-hint { font-size: 0.75rem; color: var(--brand-muted-foreground); margin-top: 2px; }

.card-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-save { display: inline-flex; align-items: center; justify-content: center; padding: 10px 24px; background: var(--brand-primary); color: white; border: none; border-radius: var(--radius-lg); font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: opacity 0.2s ease; min-width: 100px; }
.btn-save:hover:not(:disabled) { opacity: 0.9; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-test { display: inline-flex; align-items: center; justify-content: center; padding: 10px 20px; background: white; color: var(--brand-primary); border: 1px solid var(--brand-primary); border-radius: var(--radius-lg); font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; white-space: nowrap; min-width: 100px; }
.btn-test:hover:not(:disabled) { background: rgba(45, 125, 112, 0.05); }
.btn-test:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-toggle { display: inline-flex; align-items: center; justify-content: center; padding: 10px 24px; border: none; border-radius: var(--radius-lg); font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; background: var(--brand-muted); color: var(--brand-muted-foreground); }
.btn-toggle.on { background: #dc2626; color: white; }

.loading-spinner { width: 16px; height: 16px; border: 2px solid currentColor; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.ref-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.ref-tab { padding: 8px 16px; background: var(--brand-muted); border: 1px solid var(--brand-border); border-radius: var(--radius-lg); font-size: 0.875rem; color: var(--brand-muted-foreground); cursor: pointer; transition: all 0.2s ease; }
.ref-tab.active { background: var(--brand-primary); border-color: var(--brand-primary); color: white; }

.smtp-reference { overflow-x: auto; }
.ref-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.ref-table th { text-align: left; padding: 10px 12px; background: var(--brand-muted); color: var(--brand-muted-foreground); font-weight: 500; }
.ref-table td { padding: 10px 12px; border-bottom: 1px solid var(--brand-border); color: var(--brand-foreground); }
.ref-table tbody tr:last-child td { border-bottom: none; }

.wechat-steps { display: flex; flex-direction: column; gap: 16px; }
.step { display: flex; gap: 16px; align-items: flex-start; }
.step-num { width: 32px; height: 32px; border-radius: 50%; background: var(--brand-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; flex-shrink: 0; }
.step-content h4 { font-size: 0.875rem; font-weight: 600; color: var(--brand-foreground); margin: 0 0 4px 0; }
.step-content p { font-size: 0.8rem; color: var(--brand-muted-foreground); margin: 0; }
</style>