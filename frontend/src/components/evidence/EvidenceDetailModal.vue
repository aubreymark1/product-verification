<script setup lang="ts">
import { ExternalLink, FileSearch, X } from 'lucide-vue-next'

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
      <div class="card-header">
        <div class="source-title-group">
          <div class="source-icon">
            <FileSearch :size="18" :stroke-width="1.8" />
          </div>
          <div class="source-badge-row">
            <span class="source-type-tag">{{ evidence.source_type }}</span>
            <span class="relation-level-tag">{{ evidence.relation_level }}</span>
            <span class="demo-tag">演示数据，仅用于功能展示</span>
          </div>
        </div>
        <button class="close-icon-btn" aria-label="关闭" @click="emit('close')">
          <X :size="18" :stroke-width="1.8" />
        </button>
      </div>

      <div class="detail-scroll-body">
        <h3 class="evidence-title">{{ evidence.source_title }}</h3>
        <p class="evidence-summary">{{ evidence.summary }}</p>

        <div class="quote-box">
          <span class="quote-mark left">“</span>
          <p class="quote-text">{{ evidence.content }}</p>
          <span class="quote-mark right">”</span>
        </div>

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
            <span>查看原评论</span>
            <ExternalLink :size="15" :stroke-width="1.8" />
          </a>
          <span v-else class="source-link-btn disabled">
            <span>查看原评论</span>
            <ExternalLink :size="15" :stroke-width="1.8" />
          </span>
        </div>

        <button class="modal-primary-btn" @click="emit('close')">知道了</button>
      </div>
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
  align-items: flex-start;
  justify-content: center;
  padding: 96px 0 0;
}

.evidence-detail-card {
  width: 100%;
  max-width: 430px;
  max-height: calc(100vh - 96px);
  background: rgba(9, 20, 32, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-bottom: 0;
  border-radius: 24px 24px 0 0;
  padding: 0;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.035),
    0 18px 42px rgba(0, 0, 0, 0.38);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: modalIn 0.25s ease-out;
}

.card-header {
  min-height: 72px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 18px 18px 14px;
  flex: 0 0 72px;
}

.detail-scroll-body {
  overflow-y: auto;
  scrollbar-width: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 18px 20px;
}

.detail-scroll-body::-webkit-scrollbar {
  display: none;
}

.source-title-group {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.source-icon {
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  display: grid;
  place-items: center;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 10px;
}

.source-badge-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.source-type-tag {
  font-size: 11px;
  background: rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.07);
  padding: 2px 8px;
  border-radius: 10px;
}

.relation-level-tag {
  font-size: 11px;
  background: rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(255, 255, 255, 0.07);
  padding: 2px 8px;
  border-radius: 10px;
}

.demo-tag {
  font-size: 10px;
  color: #94a3b8;
}

.close-icon-btn {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.evidence-title {
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0;
}

.evidence-summary {
  font-size: 14px;
  color: #cbd5e1;
  margin: 0;
  line-height: 1.5;
  font-weight: 400;
}

.quote-box {
  position: relative;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.055);
  border-radius: 12px;
  padding: 16px 20px;
}

.quote-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.82);
  line-height: 1.65;
  margin: 0;
}

.quote-mark {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.2);
  font-weight: 400;
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
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.42);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

.source-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  flex: 0 0 auto;
  color: #5aa7ff;
  text-decoration: none;
  cursor: pointer;
  font-weight: 500;
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
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

@keyframes modalIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
