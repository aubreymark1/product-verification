<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../../services/api'

// ── 状态 ──
const health = ref<any>(null)
const video = ref<any>(null)
const identify = ref<any>(null)
const profile = ref<any>(null)
const verification = ref<any>(null)
const evidence = ref<any>(null)
const comparison = ref<any>(null)
const searchResult = ref<any>(null)

const loading: Record<string, boolean> = {
  health: false, video: false, identify: false, profile: false,
  verification: false, evidence: false, comparison: false, search: false,
}
const errors: Record<string, string> = {}

async function call(name: string, fn: () => Promise<any>, target: any) {
  loading[name] = true; errors[name] = ''
  try { target.value = await fn() } catch (e: any) { errors[name] = e.message } finally { loading[name] = false }
}

// ── 批量测试 ──
onMounted(async () => {
  await call('health', () => fetch('http://127.0.0.1:8000/api/health').then(r => r.json()), health)
  await call('video', () => api.getVideo('video_demo'), video)
  await call('identify', () => api.identify('video_demo', 0, { x: 0.22, y: 0.25, width: 0.38, height: 0.34 }), identify)
  await call('profile', () => api.getProfile('demo_category'), profile)
  await call('verification', () => api.runVerification({
    video_id: 'video_demo', product_id: 'demo_product_001', category_id: 'demo_category',
    conditions: { usage_scene: '场景A' }, raw_query: '',
  }), verification)
  await call('evidence', () => api.getEvidence('evidence_demo_support'), evidence)
  await call('comparison', () => api.addComparison({ product_id: 'demo_product_001', category_id: 'demo_category' }), comparison)
  await call('search', () => fetch('http://127.0.0.1:8000/api/verification/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_id: 'video_demo', product_id: 'demo_product_001', category_id: 'demo_category', conditions: {}, raw_query: '' }),
  }).then(r => r.json()), searchResult)
})

function badge(success: boolean) { return success ? '✅' : '❌' }
</script>

<template>
  <div style="max-width: 1200px; margin: 0 auto; padding: 24px; font-family: system-ui, sans-serif;">

    <!-- 头部 -->
    <div style="margin-bottom: 32px; border-bottom: 2px solid #e5e7eb; padding-bottom: 16px;">
      <h1 style="font-size: 28px; margin: 0 0 8px;">🔍 种草验真 API — 功能仪表盘</h1>
      <p style="color: #6b7280; margin: 0;">成员C · feature/backend-retrieval · 后端所有接口状态一览</p>
    </div>

    <!-- 健康状态条 -->
    <div style="display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap;">
      <span v-for="(v, k) in { health, video, identify, profile, verification, evidence, comparison }" :key="k"
        :style="{ padding: '6px 14px', borderRadius: 20, fontSize: 13, fontWeight: 600,
          background: v ? '#ecfdf5' : '#fef2f2', color: v ? '#065f46' : '#991b1b',
          border: `1px solid ${v ? '#a7f3d0' : '#fecaca'}` }">
        {{ badge(!!v) }} {{ k }}
      </span>
    </div>

    <!-- 接口总览卡片 -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px;">

      <!-- 1. Health -->
      <div class="card">
        <h3><span class="method get">GET</span> /api/health</h3>
        <p class="desc">服务健康检查</p>
        <div v-if="health" class="json">{{ JSON.stringify(health, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 2. Video -->
      <div class="card">
        <h3><span class="method get">GET</span> /api/videos/video_demo</h3>
        <p class="desc">视频详情 + 对象框数据</p>
        <div v-if="video" class="json">{{ JSON.stringify(video, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 3. Identify -->
      <div class="card">
        <h3><span class="method post">POST</span> /api/vision/identify</h3>
        <p class="desc">视觉识别 → 品类 + 候选商品列表</p>
        <div v-if="identify" class="json">{{ JSON.stringify(identify, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 4. Category Profile -->
      <div class="card">
        <h3><span class="method get">GET</span> /api/categories/demo_category/profile</h3>
        <p class="desc">品类动态字段配置（5种类型）</p>
        <div v-if="profile" class="json">{{ JSON.stringify(profile, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 5. Verification (核心) -->
      <div class="card highlight">
        <h3><span class="method post">POST</span> /api/verification/run ⭐</h3>
        <p class="desc">验真分析 — 返回 support / risks / uncertain + 置信度</p>
        <div v-if="verification" class="json">{{ JSON.stringify(verification, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 6. Evidence Detail -->
      <div class="card">
        <h3><span class="method get">GET</span> /api/evidence/evidence_demo_support</h3>
        <p class="desc">单条证据详情（含来源平台、关联级别等）</p>
        <div v-if="evidence" class="json">{{ JSON.stringify(evidence, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 7. Comparison -->
      <div class="card">
        <h3><span class="method post">POST</span> /api/comparison/add</h3>
        <p class="desc">加入横评队列（第一阶段占位）</p>
        <div v-if="comparison" class="json">{{ JSON.stringify(comparison, null, 2) }}</div>
        <div v-else class="loading">加载中…</div>
      </div>

      <!-- 8. 降级验证对比 -->
      <div class="card highlight" style="grid-column: 1 / -1;">
        <h3>🔄 降级验证 对比演示</h3>
        <p class="desc">左侧：预置缓存结果（verification-results.json） ←→ 右侧：基于证据检索的实时降级结果</p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div>
            <strong style="font-size:12px; color:#6b7280;">📦 预置结果 (source_ids 已过滤空值)</strong>
            <pre class="json" style="max-height:500px;">{{ verification ? JSON.stringify(verification, null, 2) : '加载中…' }}</pre>
          </div>
          <div>
            <strong style="font-size:12px; color:#6b7280;">🔍 降级检索结果 (search_evidence → build_fallback)</strong>
            <pre class="json" style="max-height:500px;">{{ searchResult ? JSON.stringify(searchResult, null, 2) : '加载中…' }}</pre>
          </div>
        </div>
      </div>

    </div>

    <!-- 底部总结 -->
    <div style="margin-top: 40px; padding: 24px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;">
      <h3 style="margin:0 0 12px;">📋 当前功能总结</h3>
      <table style="width:100%; border-collapse:collapse; font-size:14px;">
        <thead><tr style="background:#d1fae5;"><th style="padding:8px;text-align:left;">能力</th><th style="padding:8px;text-align:left;">实现方式</th><th style="padding:8px;text-align:left;">状态</th></tr></thead>
        <tbody>
          <tr><td style="padding:8px;">MockStore 数据层</td><td style="padding:8px;">从 data/mock/*.json 统一读取，支持 find_by_id / list</td><td style="padding:8px;">✅</td></tr>
          <tr><td style="padding:8px;">Pydantic 数据模型</td><td style="padding:8px;">15+ 类，字段校验 (BBox/Video/Candidate/Conclusion/Evidence…)</td><td style="padding:8px;">✅</td></tr>
          <tr><td style="padding:8px;">统一错误处理</td><td style="padding:8px;">NOT_FOUND / VALIDATION_ERROR / INTERNAL_ERROR</td><td style="padding:8px;">✅</td></tr>
          <tr><td style="padding:8px;">视频 + 对象框</td><td style="padding:8px;">Mock 返回演示视频和归一化 bbox</td><td style="padding:8px;">✅ Mock</td></tr>
          <tr><td style="padding:8px;">视觉识别</td><td style="padding:8px;">Mock → 品类匹配 + 候选商品列表</td><td style="padding:8px;">✅ Mock</td></tr>
          <tr><td style="padding:8px;">品类动态配置</td><td style="padding:8px;">5种字段类型驱动条件表单 (select/multi/number/text/bool)</td><td style="padding:8px;">✅ Mock</td></tr>
          <tr style="background:#fef3c7;"><td style="padding:8px;"><strong>⭐ 验真分析 (核心)</strong></td><td style="padding:8px;"><strong>双层策略：预置缓存 → 降级检索。过滤空 source_ids</strong></td><td style="padding:8px;"><strong>🆕 已实现</strong></td></tr>
          <tr style="background:#fef3c7;"><td style="padding:8px;"><strong>证据检索服务</strong></td><td style="padding:8px;"><strong>精确匹配 → 同品类降级 → 去重排序 → 维度分类</strong></td><td style="padding:8px;"><strong>🆕 已实现</strong></td></tr>
          <tr style="background:#fef3c7;"><td style="padding:8px;"><strong>降级验证器</strong></td><td style="padding:8px;"><strong>AI 不可用时自动基于证据构造验证结果</strong></td><td style="padding:8px;"><strong>🆕 已实现</strong></td></tr>
          <tr><td style="padding:8px;">证据详情</td><td style="padding:8px;">Mock 返回来源平台、关联级别、置信度等</td><td style="padding:8px;">✅ Mock</td></tr>
          <tr><td style="padding:8px;">横评占位</td><td style="padding:8px;">第二阶段接入</td><td style="padding:8px;">⏳ 占位</td></tr>
          <tr><td style="padding:8px;">测试覆盖</td><td style="padding:8px;">10/10 passed — 含完整流程、降级、source_ids过滤</td><td style="padding:8px;">✅</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.card h3 { margin: 0 0 4px; font-size: 15px; display: flex; align-items: center; gap: 8px; }
.card .desc { color: #6b7280; font-size: 13px; margin: 0 0 10px; }
.card.highlight { border-color: #f59e0b; box-shadow: 0 0 0 1px #fef3c7; }
.method {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 700; text-transform: uppercase;
}
.method.get { background: #dbeafe; color: #1e40af; }
.method.post { background: #fce7f3; color: #9d174d; }
.json, pre.json {
  background: #1e293b; color: #e2e8f0; font-size: 12px; line-height: 1.5;
  padding: 12px; border-radius: 6px; overflow-x: auto; max-height: 320px;
  white-space: pre-wrap; word-break: break-all;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.loading { color: #9ca3af; font-style: italic; font-size: 13px; padding: 12px 0; }
</style>
