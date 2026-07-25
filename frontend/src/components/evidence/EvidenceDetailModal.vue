<script setup lang="ts">
import type { Evidence } from '../../types/api'

defineProps<{
  evidence: Evidence | null
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div v-if="evidence" class="modal-backdrop" @click.self="emit('close')">
    <div class="evidence-detail-card">
      <!-- Top header -->
      <div class="card-header">
        <div class="source-badge-row">
          <span class="source-type-tag">{{ evidence.source_type }}</span>
          <span class="relation-level-tag">{{ evidence.relation_level }}</span>
          <span class="demo-tag">演示数据，仅用于功能展示</span>
        </div>
        <button class="close-icon-btn" @click="emit('close')">✕</button>
      </div>

      <!-- Title & Summary -->
      <h3 class="evidence-title">{{ evidence.source_title }}</h3>
      <p class="evidence-summary">{{ evidence.summary }}</p>

      <!-- Content quote box -->
      <div class="quote-box">
        <span class="quote-mark left">“</span>
        <p class="quote-text">{{ evidence.content }}</p>
        <span class="quote-mark right">”</span>
      </div>

      <!-- Source Meta Footer -->
      <div class="meta-footer">
        <div class="meta-left">
          <span>来源：{{ evidence.source_platform }}</span>
          <span v-if="evidence.published_at">· {{ evidence.published_at }}</span>
          <span>· 点赞 86</span>
        </div>
        <a
          v-if="evidence.source_url"
          :href="evidence.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="source-link-btn"
        >
          查看原评论 &gt;
        </a>
        <span v-else class="source-link-btn disabled">查看原评论 &gt;</span>
      </div>

      <button class="modal-primary-btn" @click="emit('close')">知道了</button>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 15, 29, 0.82);
  backdrop-filter: blur(8px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.evidence-detail-card {
  width: 100%;
  max-width: 540px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  animation: modalIn 0.25s ease-out;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-badge-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.source-type-tag {
  font-size: 11px;
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
}

.relation-level-tag {
  font-size: 11px;
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
}

.demo-tag {
  font-size: 10px;
  color: #94a3b8;
}

.close-icon-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
}

.evidence-title {
  font-size: 18px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.evidence-summary {
  font-size: 14px;
  color: #cbd5e1;
  margin: 0;
  line-height: 1.5;
}

.quote-box {
  position: relative;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px 20px;
}

.quote-text {
  font-size: 13px;
  color: #e2e8f0;
  line-height: 1.6;
  margin: 0;
}

.quote-mark {
  font-size: 24px;
  color: #38bdf8;
  font-weight: 800;
}

.quote-mark.left {
  float: left;
  margin-right: 6px;
}

.quote-mark.right {
  float: right;
  margin-left: 6px;
}

.meta-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

.source-link-btn {
  color: #38bdf8;
  text-decoration: none;
  cursor: pointer;
  font-weight: 600;
}

.source-link-btn.disabled {
  opacity: 0.6;
  cursor: default;
}

.modal-primary-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: none;
  background: #2563eb;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
