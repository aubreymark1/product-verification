<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import StatusMessage from '../../components/common/StatusMessage.vue'
import AiAnalysisLoading from '../verification/AiAnalysisLoading.vue'
import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { CategoryProfile } from '../../types/api'

const router = useRouter()
const session = useSessionStore()
const profile = ref<CategoryProfile | null>(null)
const formData = reactive<Record<string, unknown>>({})
const rawQuery = ref('')
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  // Fallback product set if user accessed /conditions directly
  if (!session.hasProduct) {
    session.videoId = 'demo_video_001'
    session.categoryId = 'gaming_mouse'
    session.setProduct({
      product_id: 'atk_a9_ultimate',
      product_name: '轻量化电竞鼠标 G Pro',
      confidence: 0.98,
      image_url: '/assets/mock/products/62e1042760e7bac7a95e2a27a8bfde1e.png',
    })
  }

  try {
    profile.value = await api.getProfile(session.categoryId || 'gaming_mouse')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '品类配置加载失败'
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!session.selectedProduct || !profile.value) return
  submitting.value = true
  error.value = ''

  try {
    // 1.5s transition delay for AI Loading Animation
    const [result] = await Promise.all([
      api.runVerification({
        video_id: session.videoId,
        product_id: session.selectedProduct.product_id,
        category_id: profile.value.category_id,
        conditions: { ...formData },
        raw_query: rawQuery.value,
      }),
      new Promise((resolve) => setTimeout(resolve, 1500)),
    ])
    session.setVerificationResult(result)
    await router.push(`/verification/${result.result_id}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '验真请求失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="conditions-page-shell">
    <div class="page-header">
      <div class="header-badge">STEP 02 · 动态条件配置</div>
      <h1 class="page-title">个性化使用需求</h1>
    </div>

    <!-- AI Loading overlay during submit -->
    <AiAnalysisLoading v-if="submitting" />

    <!-- Form Content -->
    <template v-else>
      <StatusMessage v-if="loading" type="loading" message="正在读取品类配置与条件规则…" />
      <StatusMessage v-else-if="error && !profile" type="error" :message="error" />

      <form v-else-if="profile" class="form-glass-card" @submit.prevent="submit">
        <textarea
          v-model="rawQuery"
          class="requirements-input"
          rows="6"
          placeholder="请输入你的使用需求"
        ></textarea>

        <StatusMessage v-if="error" type="error" :message="error" />

        <!-- Submit Button -->
        <div class="submit-row">
          <button class="gradient-submit-btn" type="submit" :disabled="submitting">
            <span class="btn-text">🚀 提交并开始 AI 深度验真</span>
          </button>
        </div>
      </form>
    </template>
  </section>
</template>

<style scoped>
.conditions-page-shell {
  max-width: 680px;
  margin: 0 auto;
  overflow-x: hidden;
}

.page-header {
  margin-bottom: 20px;
}

.header-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 10px;
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: #f8fafc;
  margin: 0 0 6px;
}

.product-subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
}

.highlight-product {
  color: #38bdf8;
  font-weight: 600;
}

.form-glass-card {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-sizing: border-box;
}

.category-meta-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(30, 41, 59, 0.5);
  padding: 10px 14px;
  border-radius: 12px;
  border-left: 3px solid #06b6d4;
}

.meta-tag {
  font-size: 13px;
  font-weight: 700;
  color: #06b6d4;
}

.meta-desc {
  font-size: 12px;
  color: #94a3b8;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 4px 0;
}

.submit-row {
  margin-top: 6px;
}

.gradient-submit-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 8px 24px rgba(6, 182, 212, 0.3);
}

.gradient-submit-btn:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}

.gradient-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.requirements-input {
  width: 100%;
  min-height: 144px;
  box-sizing: border-box;
  padding: 14px 16px;
  resize: vertical;
  color: #f8fafc;
  font: inherit;
  font-size: 14px;
  line-height: 1.6;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
}

.requirements-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
}
</style>
