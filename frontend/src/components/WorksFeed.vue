<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'

const props = defineProps({
  onlyMine: { type: Boolean, default: false },
  workType: { type: String, default: '' },
})
const emit = defineEmits(['count'])

const works = ref([])
const loading = ref(true)
const liked = ref(new Set())

async function load() {
  loading.value = true
  try {
    works.value = await api('/works', {
      params: { only_mine: props.onlyMine || undefined, work_type: props.workType || undefined },
    })
    emit('count', works.value.length)
  } catch (e) {
    works.value = []
  } finally {
    loading.value = false
  }
}

async function like(id) {
  if (liked.value.has(id)) return
  liked.value.add(id)
  const data = await api(`/works/${id}/like`, { method: 'POST' })
  const w = works.value.find((x) => x.id === id)
  if (w) w.like_count = data.like_count
}

onMounted(load)
defineExpose({ load })
</script>

<template>
  <div v-if="loading" class="empty">加载中...</div>
  <div v-else-if="works.length === 0" class="empty">还没有作品,去 Create 创作第一个吧</div>
  <div v-else class="masonry">
    <div v-for="w in works" :key="w.id" class="card item">
      <img v-if="w.work_type === 'image'" :src="w.media_url" class="thumb" loading="lazy" />
      <video v-else :src="w.media_url" class="thumb" muted loop playsinline
        @mouseenter="$event.target.play()" @mouseleave="$event.target.pause()" />
      <div class="meta">
        <p class="prompt">{{ w.prompt }}</p>
        <div class="row">
          <span class="model">{{ w.model }}</span>
          <button class="like" :class="{ liked: liked.has(w.id) }" @click="like(w.id)">
            ♥ {{ w.like_count }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.masonry { column-count: 2; column-gap: 10px; }
.item { break-inside: avoid; margin-bottom: 10px; }
.thumb { width: 100%; display: block; object-fit: cover; }
.meta { padding: 8px 10px 10px; }
.prompt {
  font-size: 12px;
  color: var(--text-dim);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.row { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.model { font-size: 11px; color: var(--primary-soft); }
.like {
  background: none; border: none; color: var(--text-dim);
  font-size: 12px; cursor: pointer; padding: 2px 4px;
}
.like.liked { color: #f472b6; }
</style>
