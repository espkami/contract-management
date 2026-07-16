<template>
  <div class="login-container">
    <!-- Left Panel: Brand Area -->
    <div class="login-brand-panel">
      <!-- Subtle background pattern -->
      <div class="brand-pattern"></div>
      
      <!-- Decorative circles -->
      <div class="brand-circle-1"></div>
      <div class="brand-circle-2"></div>

      <!-- Logo -->
      <div class="brand-logo">
        <img src="../assets/logo.png" alt="Logo" class="brand-logo-img" />
      </div>

      <!-- Brand text -->
      <h1 class="brand-title">合同管理系统</h1>
    </div>

    <!-- Right Panel: Login Form -->
    <div class="login-form-panel">
      <!-- Logo for mobile -->
      <div class="mobile-header">
        <img src="../assets/logo.png" alt="Logo" class="mobile-logo-img" />
        <span class="mobile-title">合同管理系统</span>
      </div>

      <!-- Welcome header -->
      <div class="login-header">
        <h2 class="login-title">欢迎回来</h2>
        <p class="login-subtitle">请输入您的账号信息以登录系统</p>
      </div>

      <!-- Login form -->
      <form class="login-form" @submit.prevent="doLogin">
        <!-- Username -->
        <div class="form-item" :class="{ 'has-error': errors.username }">
          <label class="form-label">用户名</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <input
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              autocomplete="username"
              class="form-input"
              @blur="validateUsername"
              @keyup.enter="doLogin"
            />
          </div>
          <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
        </div>

        <!-- Password -->
        <div class="form-item" :class="{ 'has-error': errors.password }">
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              autocomplete="current-password"
              class="form-input"
              @blur="validatePassword"
              @keyup.enter="doLogin"
            />
            <button type="button" class="password-toggle" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <div v-if="errors.password" class="form-error">{{ errors.password }}</div>
        </div>

        <!-- Remember me & Forgot password -->
        <div class="form-options">
          <label class="remember-me">
            <input v-model="form.remember" type="checkbox" class="remember-checkbox" />
            <span class="remember-text">记住我</span>
          </label>
          <a href="#" class="forgot-link">忘记密码?</a>
        </div>

        <!-- Login button -->
        <button type="submit" class="login-button" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>

      <!-- Copyright -->
      <div class="login-footer">
        <p>© 2026 合同管理系统 · 出版物资大厦工程部赵震珉</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const showPassword = ref(false)
const form = reactive({ username: '', password: '', remember: false })
const errors = reactive({ username: '', password: '' })

function validateUsername() {
  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    return false
  }
  errors.username = ''
  return true
}

function validatePassword() {
  if (!form.password) {
    errors.password = '请输入密码'
    return false
  }
  errors.password = ''
  return true
}

async function doLogin() {
  const valid = validateUsername() & validatePassword()
  if (!valid) return
  try {
    loading.value = true
    await auth.login(form.username, form.password)
    router.push('/dashboard')
  } catch (error) {
    if (error !== false) {
      ElMessage.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--brand-background);
}

/* Left Panel - Brand */
.login-brand-panel {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 50%;
  position: relative;
  overflow: hidden;
  background: var(--color-primary-900);
}

@media (min-width: 1024px) {
  .login-brand-panel {
    display: flex;
  }
}

.brand-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h40v40H0V0zm1 1v38h38V1H1z' fill='white' fill-opacity='0.4'/%3E%3C/svg%3E");
}

.brand-circle-1 {
  position: absolute;
  top: 80px;
  left: 80px;
  width: 256px;
  height: 256px;
  border-radius: 50%;
  background: rgba(45, 125, 112, 0.15);
}

.brand-circle-2 {
  position: absolute;
  bottom: 64px;
  right: 64px;
  width: 192px;
  height: 192px;
  border-radius: 50%;
  background: rgba(77, 156, 142, 0.1);
}

.brand-logo {
  position: relative;
  z-index: 10;
  margin-bottom: 48px;
}

.brand-logo-img {
  width: 120px;
  height: auto;
}

.brand-title {
  position: relative;
  z-index: 10;
  font-size: 2.25rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.025em;
  margin-bottom: 16px;
}

.brand-subtitle {
  position: relative;
  z-index: 10;
  font-size: 1rem;
  color: white;
  opacity: 0.6;
  max-width: 320px;
  text-align: center;
  line-height: 1.5;
}

/* Right Panel - Form */
.login-form-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 24px;
  background: var(--brand-card);
}

@media (min-width: 1024px) {
  .login-form-panel {
    width: 50%;
    padding: 48px;
  }
}

.mobile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
  justify-content: center;
}

@media (min-width: 1024px) {
  .mobile-header {
    display: none;
  }
}

.mobile-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--brand-foreground);
}

.mobile-logo-img {
  width: 40px;
  height: auto;
}

.login-header {
  margin-bottom: 32px;
  text-align: center;
}

@media (min-width: 1024px) {
  .login-header {
    text-align: left;
  }
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--brand-foreground);
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

.login-form {
  width: 100%;
  max-width: 400px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item.has-error .form-input {
  border-color: var(--state-error);
}

.form-error {
  font-size: 0.75rem;
  color: var(--state-error);
  padding-top: 4px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-foreground);
  margin-bottom: 6px;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--neutral-400);
  pointer-events: none;
}

.form-input {
  width: 100%;
  border: 1px solid var(--brand-border);
  border-radius: var(--radius-lg);
  padding: 10px 40px 10px 40px;
  font-size: 0.875rem;
  color: var(--brand-foreground);
  background: white;
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: var(--brand-muted-foreground);
}

.form-input:focus {
  outline: none;
  border-color: var(--brand-ring);
  box-shadow: 0 0 0 3px rgba(45, 125, 112, 0.1);
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 4px;
  color: var(--neutral-400);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.password-toggle:hover {
  color: var(--brand-foreground);
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.remember-checkbox {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--brand-border);
  accent-color: var(--brand-primary);
  cursor: pointer;
}

.remember-text {
  font-size: 0.875rem;
  color: var(--brand-muted-foreground);
}

.forgot-link {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--brand-primary);
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-button {
  width: 100%;
  background: var(--brand-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  padding: 12px 32px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
}

.login-button:hover:not(:disabled) {
  opacity: 0.9;
}

.login-button:disabled {
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

.login-footer {
  margin-top: auto;
  padding-top: 40px;
  text-align: center;
}

.login-footer p {
  font-size: 0.75rem;
  color: var(--brand-muted-foreground);
  opacity: 0.6;
}
</style>