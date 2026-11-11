<script setup>
import { nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'

const router = useRouter()
const messages = ref([
  { role: 'assistant', content: '嗨~ 我是 UnudeAI 助手 💜 可以帮我写生图提示词、聊创作灵感,或者随便聊聊。' },
])
const input = ref('')
const busy = ref(false)
const listEl = ref(null)

async function send() {
  if (!input.value.trim() || busy.value) return
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  const text = input.value.trim()
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  busy.value = true
  scrollBottom()
  try {
    const history = messages.value.slice(0, -1).map((m) => ({ role: m.role, content: m.content }))
    const data = await api('/chat', { method: 'POST', body: { message: text, history } })
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '(服务暂不可用: ' + e.message + ')' })
  } finally {
    busy.value = false
    scrollBottom()
  }
}

function scrollBottom() {
  nextTick(() => listEl.value?.scrollTo({ top: listEl.value.scrollHeight, behavior: 'smooth' }))
}
</script>

<template>
  <div class="chat-page">
    <h1 class="page-title">AI LOVER</h1>
    <div ref="listEl" class="msgs">
      <div v-for="(m, i) in messages" :key="i" class="bubble" :class="m.role">
        {{ m.content }}
      </div>
      <div v-if="busy" class="bubble assistant typing">对方正在输入...</div>
    </div>
    <div class="input-bar">
      <input v-model="input" placeholder="说点什么..." @keyup.enter="send" />
      <button class="send" :disabled="busy" @click="send">➤</button>
    </div>
  </div>
</template>

<style scoped>
.chat-page { display: flex; flex-direction: column; height: calc(100vh - 76px); padding: 20px 16px 12px; }
.page-title { margin-bottom: 12px; }
.msgs { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-bottom: 10px; }
.bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
.bubble.assistant { align-self: flex-start; background: var(--bg-card); border: 1px solid var(--border); }
.bubble.user { align-self: flex-end; background: var(--primary); color: #fff; }
.typing { color: var(--text-dim); font-size: 12px; }
.input-bar { display: flex; gap: 8px; }
.send {
  width: 46px; border: none; border-radius: 12px;
  background: var(--primary); color: #fff; font-size: 17px; cursor: pointer;
}
.send:disabled { opacity: 0.5; }
</style>
