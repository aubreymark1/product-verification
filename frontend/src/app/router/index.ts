import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('../../features/dashboard/DashboardPage.vue') },
    { path: '/video', component: () => import('../../features/video/VideoPage.vue') },
    { path: '/conditions', component: () => import('../../features/conditions/ConditionsPage.vue') },
    { path: '/verification/:resultId', component: () => import('../../features/verification/VerificationPage.vue') },
    { path: '/comparison', component: () => import('../../features/comparison/ComparisonPage.vue') },
  ],
})

export default router
