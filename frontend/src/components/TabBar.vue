<script setup>
const tabs = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/discover', label: 'Discover', icon: '🧭' },
  { path: '/short', label: 'Short', icon: '🎬' },
  { path: '/create', label: 'Create', icon: '➕' },
  { path: '/ai-lover', label: 'AI Lover', icon: '💜' },
  { path: '/my', label: 'My', icon: '👤' },
]
</script>

<template>
  <nav class="tabbar">
    <router-link v-for="t in tabs" :key="t.path" :to="t.path" class="tab" active-class="active">
      <span class="icon">{{ t.icon }}</span>
      <span class="label">{{ t.label }}</span>
    </router-link>
  </nav>
</template>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  display: flex;
  background: rgba(13, 6, 24, 0.95);
  border-top: 1px solid var(--border);
  backdrop-filter: blur(10px);
  z-index: 50;
}
.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 9px 0 10px;
  text-decoration: none;
  color: var(--text-dim);
  font-size: 11px;
}
.tab .icon { font-size: 19px; filter: grayscale(0.6) opacity(0.75); }
.tab.active { color: var(--primary-soft); }
.tab.active .icon { filter: none; }
</style>
