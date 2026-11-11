import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/discover', component: () => import('./views/Discover.vue') },
  { path: '/short', component: () => import('./views/Short.vue') },
  { path: '/create', component: () => import('./views/Create.vue') },
  { path: '/ai-lover', component: () => import('./views/AILover.vue') },
  { path: '/my', component: () => import('./views/My.vue') },
  { path: '/login', component: () => import('./views/Login.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
