<script setup lang="ts">
const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <div class="rerecommend-card-container">
    <div class="rerecommend-card" @click="emit('click')">
      <div class="left-group">
        <div class="refresh-circle">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
        </div>
        <div class="text-group">
          <div class="title-row">
            <span class="title-text">继续帮我找更合适的</span>
            <span class="arrow">&gt;</span>
          </div>
          <span class="sub-text">基于需求重新筛选，发现更多好物</span>
        </div>
      </div>
    </div>

    <!-- AI Footer Disclaimer -->
    <div class="ai-footer-disclaimer">
      <span class="shield-icon">🛡️</span>
      <span>AI 结论基于公开内容，仅供参考</span>
    </div>
  </div>
</template>

<style scoped>
.rerecommend-card-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rerecommend-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #121824;
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rerecommend-card:hover {
  background: rgba(18, 24, 36, 0.9);
  border-color: rgba(56, 189, 248, 0.5);
}

.left-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(56, 189, 248, 0.12);
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-group {
  display: flex;
  flex-direction: column;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.arrow {
  font-size: 12px;
  color: #38bdf8;
}

.sub-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.ai-footer-disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  padding: 8px 0 16px;
}

.shield-icon {
  font-size: 11px;
}
</style>
