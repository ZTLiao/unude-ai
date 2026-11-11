import { reactive } from 'vue'
import { api, getToken, setToken, clearToken } from './api'

export const auth = reactive({
  user: null,
  get isLoggedIn() {
    return !!this.user
  },
})

export async function restoreSession() {
  if (!getToken()) return
  try {
    auth.user = await api('/auth/me')
  } catch {
    clearToken()
    auth.user = null
  }
}

export async function login(email, password) {
  const data = await api('/auth/login', { method: 'POST', params: { email, password } })
  setToken(data.token)
  auth.user = data.user
  return data.user
}

export async function register(email, password, nickname = '') {
  const data = await api('/auth/register', {
    method: 'POST',
    params: { email, password, nickname },
  })
  setToken(data.token)
  auth.user = data.user
  return data.user
}

export function logout() {
  clearToken()
  auth.user = null
}
