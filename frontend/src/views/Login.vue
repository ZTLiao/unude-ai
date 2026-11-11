<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../store'

const router = useRouter()
const mode = ref('login')
const email = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    if (mode.value === 'login') await login(email.value, password.value)
    else await register(email.value, password.value)
    router.push('/create')
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page login-page">
    <h1 class="page-title">UNUDE AI</h1>
    <p class="slogan">多模型 AI 创作 · 生图 · 生视频</p>

    <div class="seg">
      <button :class="{ on: mode === 'login' }" @click="mode = 'login'">登录</button>
      <button :class="{ on: mode === 'register' }" @click="mode = 'register'">注册</button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <form @submit.prevent="submit">
      <input v-model="email" type="email" placeholder="邮箱账号" required />
      <input v-model="password" type="password" placeholder="密码" required />
      <button class="btn-primary" :disabled="busy" style="margin-top: 16px">
        {{ busy ? '请稍候...' : mode === 'login' ? '登录' : '注册(送 100 积分)' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login-page { padding-top: 80px; }
.slogan { color: var(--text-dim); font-size: 13px; margin: -10px 0 24px; }
input { margin-bottom: 12px; }
.seg {
  display: flex;
  background: var(--bg-input);
  border-radius: 999px;
  padding: 4px;
  margin-bottom: 20px;
}
.seg button {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-dim);
  padding: 10px;
  border-radius: 999px;
  font-size: 14px;
  cursor: pointer;
}
.seg button.on { background: var(--primary); color: #fff; font-weight: 600; }
</style>
