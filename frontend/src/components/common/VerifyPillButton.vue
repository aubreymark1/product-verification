<script setup lang="ts">
const emit = defineEmits<{
  click: [e: MouseEvent]
}>()
</script>

<template>
  <button type="button" class="minimal-verify-pill" @click="emit('click', $event)">
    <span class="icon-svg">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    </span>
    <span class="label">验一验</span>
    <span class="arrow">&gt;</span>
  </button>
</template>

<style scoped>
.minimal-verify-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #f8fafc;
  font-size: 12px;
  font-weight: 300;
  letter-spacing: 0.3px;
  cursor: pointer;
  backdrop-filter: blur(16px);
  transition: all 0.2s ease;
  user-select: none;
}

.minimal-verify-pill:hover {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(56, 189, 248, 0.5);
  color: #ffffff;
}

.minimal-verify-pill:active {
  transform: scale(0.97);
}

.icon-svg {
  display: flex;
  align-items: center;
  color: #38bdf8;
}

.label {
  letter-spacing: 0.5px;
}

.arrow {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 1px;
}
</style>
