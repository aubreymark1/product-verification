<script setup lang="ts">
import { ref } from 'vue'

import StatusMessage from '../../components/common/StatusMessage.vue'
import EvidenceCard from '../../components/evidence/EvidenceCard.vue'
import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { Evidence } from '../../types/api'

const session = useSessionStore()
const evidence = ref<Evidence | null>(null)
const evidenceLoading = ref(false)
const error = ref('')

async function openEvidence(id: string) {
  evidenceLoading.value = true
  error.value = ''
  try { evidence.value = await api.getEvidence(id) } catch (err) { error.value = err instanceof Error ? err.message : '证据加载失败' } finally { evidenceLoading.value = false }
}

async function addComparison() {
  if (!session.selectedProduct) return
  try { await api.addComparison({ product_id: session.selectedProduct.product_id, category_id: session.categoryId, result_id: session.verificationResult?.result_id }); window.alert('已加入横评占位队列') } catch (err) { error.value = err instanceof Error ? err.message : '操作失败' }
}
</script>

<template>
  <section><div class="page-header"><p class="card-kicker">第三步 · 验真结果</p><h1>证据汇总</h1></div>
    <StatusMessage v-if="!session.verificationResult" type="empty" message="还没有可展示的验真结果，请从视频页开始一次 Mock 流程。" />
    <template v-else><div class="panel"><div class="result-summary"><strong>{{ session.verificationResult.summary }}</strong><p>整体置信度：{{ Math.round(session.verificationResult.confidence * 100) }}%</p></div><div class="actions"><button class="secondary-button" @click="addComparison">加入横评（占位）</button></div></div>
      <div class="grid evidence-columns"><div><h2>支持证据</h2><EvidenceCard v-for="item in session.verificationResult.support" :key="item.id" title="支持" :item="item" @evidence="openEvidence" /></div><div><h2>风险证据</h2><EvidenceCard v-for="item in session.verificationResult.risks" :key="item.id" title="风险" :item="item" @evidence="openEvidence" /></div><div><h2>待确认项</h2><EvidenceCard v-for="item in session.verificationResult.uncertain" :key="item.id" title="待确认" :item="item" @evidence="openEvidence" /></div></div>
    </template>
    <StatusMessage v-if="error" type="error" :message="error" />
    <div v-if="evidenceLoading" class="modal-backdrop"><div class="modal">正在加载证据详情…</div></div>
    <div v-if="evidence" class="modal-backdrop" @click.self="evidence = null"><article class="modal"><p class="card-kicker">{{ evidence.source_type }} · {{ evidence.relation_level }}</p><h2>{{ evidence.source_title }}</h2><p>{{ evidence.summary }}</p><p>{{ evidence.content }}</p><p class="card-kicker">来源平台：{{ evidence.source_platform }} · 来源链接：{{ evidence.source_url ?? '暂无（演示数据）' }}</p><button class="primary-button" @click="evidence = null">关闭</button></article></div>
  </section>
</template>
