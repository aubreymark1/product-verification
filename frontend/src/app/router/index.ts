import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/video' },
    { path: '/video', component: () => import('../../features/video/VideoPage.vue') },
    { path: '/conditions', component: () => import('../../features/conditions/ConditionsPage.vue') },
    { path: '/verification/:resultId', component: () => import('../../features/verification/VerificationPage.vue') },
    { path: '/recommendations', component: () => import('../../features/verification/RecommendationPage.vue') },
    { path: '/price-comparison', name: 'price-comparison', component: () => import('../../features/verification/LowPricePage.vue') },
    { path: '/comparison', component: () => import('../../features/comparison/ComparisonPage.vue') },
  ],
})

export default router
