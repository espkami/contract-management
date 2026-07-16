import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const form = new FormData()
    form.append('username', username)
    form.append('password', password)
    const res = await api.post('/api/auth/login', form)
    token.value = res.data.access_token
    user.value = { username: res.data.username, role: res.data.role }
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function logout() {
    await api.post('/api/auth/logout').catch(() => {})
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAdmin, login, logout }
})
