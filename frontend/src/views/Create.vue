<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { auth } from '../store'

const router = useRouter()

const models = ref([])
const typeTab = ref('image') // image | video
const selectedModel = ref('')
const prompt = ref('')
const ratio = ref('1:1')
const busy = ref(false)
const error = ref('')
const task = ref(null) // 当前轮询的任务
const preview = ref(null) // 完成的作品

const ratios = ['1:1', '3:4', '9:16', '16:9']

const filteredModels = computed(() => models.value.filter((m) => m.type === typeTab.value))

function pickModel(m) {
  selectedModel.value = m.key
}

async function loadModels() {
  models.value = await api('/models')
  const first = filteredModels.value[0]
  if (first) selectedModel.value = first.key
}

function submit() {
  error.value = ''
  if (!auth.isLoggedIn) {
    router.push('/login')
    return
  }
  if (!prompt.value.trim()) {
    error.value = '请输入提示词'
    return
  }
  busy.value = true
  preview.value = null
  api('/generate', {
    method: 'POST',
    body: { model: selectedModel.value, prompt: prompt.value, ratio: ratio.value },
  })
    .then((data) => poll(data.task_id))
    .catch((e) => {
      error.value = e.message
      busy.value = false
    })
}

function poll(taskId) {
  task.value = { status: 'running', progress: 0 }
  const timer = setInterval(async () => {
    try {
      const t = await api(`/tasks/${taskId}`)
      task.value = t
      if (t.status === 'succeeded') {
        clearInterval(timer)
        busy.value = false
        preview.value = t
        task.value = null
      } else if (t.status === 'failed') {
        clearInterval(timer)
        busy.value = false
        error.value = t.error || '生成失败'
        task.value = null
      }
    } catch {
      clearInterval(timer)
      busy.value = false
    }
  }, 1500)
}

onMounted(loadModels)
</script>

<template>
  <div class="page">
    <h1 class="page-title">CREATE</h1>

    <div class="seg">
      <button :class="{ on: typeTab === 'image' }" @click="typeTab = 'image'; loadModels()">文生图</button>
      <button :class="{ on: typeTab === 'video' }" @click="typeTab = 'video'; loadModels()">文生视频</button>
    </div>

    <div class="models">
      <button
        v-for="m in filteredModels"
        :key="m.key"
        class="model-chip"
        :class="{ active: selectedModel === m.key }"
        @click="pickModel(m)"
      >
        <span class="m-name">{{ m.name }}</span>
        <span class="m-cost">{{ m.cost_credits ? m.cost_credits + ' 积分' : '免费' }}</span>
        <span class="m-desc">{{ m.desc }}</span>
      </button>
    </div>

    <textarea v-model="prompt" placeholder="描述你想要创作的内容,例如:一只在星空中漂浮的橙色猫宇航员,赛博朋克风格"></textarea>

    <div v-if="typeTab === 'image'" class="ratios">
      <button
        v-for="r in ratios"
        :key="r"
        class="chip"
        :class="{ active: ratio === r }"
        @click="ratio = r"
      >
        {{ r }}
      </button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <button class="btn-primary" :disabled="busy" @click="submit">
      {{ busy ? '生成中...' : '开始生成' }}
    </button>

    <div v-if="task" class="progress-card card">
      <div class="bar"><div class="fill" :style="{ width: task.progress + '%' }"></div></div>
      <p class="p-text">{{ task.status === 'running' ? 'AI 正在创作... ' + task.progress + '%' : '排队中...' }}</p>
    </div>

    <div v-if="preview" class="card preview">
      <img v-if="preview.result_url.endsWith('.mp4') === false && typeTab === 'image'" :src="preview.result_url" />
      <video v-else :src="preview.result_url" controls autoplay loop />
      <p class="done">生成完成!</p>
    </div>
  </div>
</template>

<style scoped>
.seg {
  display: flex;
  background: var(--bg-input);
  border-radius: 999px;
  padding: 4px;
  margin-bottom: 16px;
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

.models { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }
.model-chip {
  display: grid;
  grid-template-columns: auto auto 1fr;
  align-items: baseline;
  gap: 8px;
  text-align: left;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  color: var(--text);
  cursor: pointer;
}
.model-chip.active { border-color: var(--primary); background: rgba(139, 92, 246, 0.12); }
.m-name { font-size: 14px; font-weight: 600; }
.m-cost { font-size: 12px; color: #fbbf24; }
.m-desc { font-size: 12px; color: var(--text-dim); justify-self: end; text-align: right; }

textarea { margin-bottom: 12px; }
.ratios { display: flex; gap: 8px; margin-bottom: 14px; }
.ratios .chip { flex: 1; text-align: center; }

.progress-card { margin-top: 18px; padding: 14px; }
.bar { height: 8px; background: var(--bg-input); border-radius: 999px; overflow: hidden; }
.fill { height: 100%; background: var(--primary); border-radius: 999px; transition: width 0.5s; }
.p-text { font-size: 12px; color: var(--text-dim); margin-top: 8px; text-align: center; }

.preview { margin-top: 18px; }
.preview img, .preview video { width: 100%; display: block; }
.done { text-align: center; color: var(--primary-soft); font-size: 13px; padding: 10px; }
</style>
