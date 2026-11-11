<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth, logout } from '../store'
import WorksFeed from '../components/WorksFeed.vue'

const router = useRouter()
const feed = ref(null)
const credits = ref(0)

async function refresh() {
  if (!auth.isLoggedIn) return
  const data = await api('/auth/me')
  auth.user = data
  credits.value = data.credits
}

function goLogin() {
  router.push('/login')
}

function exit() {
  logout()
  router.push('/login')
}

onMounted(refresh)
</script>

<template>
  <div class="page">
    <h1 class="page-title">MY</h1>

    <div v-if="!auth.isLoggedIn" class="not-login">
      <p class="empty">登录后查看你的作品和积分</p>
      <button class="btn-primary" @click="goLogin">去登录 / 注册</button>
    </div>

    <div v-else>
      <div class="card profile">
        <div class="avatar">{{ (auth.user?.nickname || 'U')[0].toUpperCase() }}</div>
        <div class="info">
          <p class="nick">{{ auth.user?.nickname }}</p>
          <p class="email">{{ auth.user?.email }}</p>
        </div>
        <div class="credits">
          <span class="c-num">{{ credits }}</span>
          <span class="c-label">积分</span>
        </div>
      </div>

      <button class="btn-ghost" @click="exit">退出登录</button>

      <h2 class="sub">我的作品</h2>
      <WorksFeed ref="feed" only-mine />
    </div>
  </div>
</template>

<style scoped>
.not-login { padding-top: 40px; }
.profile { display: flex; align-items: center; padding: 16px; gap: 12px; }
.avatar {
  width: 52px; height: 52px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 700;
}
.info { flex: 1; }
.nick { font-size: 16px; font-weight: 600; }
.email { font-size: 12px; color: var(--text-dim); }
.credits { text-align: center; }
.c-num { display: block; font-size: 20px; font-weight: 700; color: #fbbf24; }
.c-label { font-size: 11px; color: var(--text-dim); }
.btn-ghost {
  margin-top: 12px; width: 100%;
  background: none; border: 1px solid var(--border);
  color: var(--text-dim); border-radius: 999px; padding: 10px;
  font-size: 13px; cursor: pointer;
}
.sub { font-size: 16px; margin: 22px 0 12px; }
</style>
