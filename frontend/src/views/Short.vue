<script setup>
import WorksFeed from '../components/WorksFeed.vue'
</script>

<template>
  <div class="page">
    <h1 class="page-title">SHORT</h1>
    <p class="hint">AI 生成的视频作品</p>
    <WorksFeed work-type="video" />
  </div>
</template>

<style scoped>
.hint { color: var(--text-dim); font-size: 13px; margin: -10px 0 16px; }
</style>
