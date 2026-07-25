<script setup lang="ts">
const props = defineProps<{
  show: boolean
  title?: string
  step?: number
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <Transition name="drawer">
    <div v-if="show" class="drawer-backdrop" @click.self="emit('close')">
      <div class="drawer-panel">
        <!-- Top handle bar -->
        <div class="drawer-handle-zone">
          <div class="handle"></div>
        </div>

        <!-- Clean Native Header -->
        <div v-if="title" class="drawer-header">
          <h2 class="drawer-title">{{ title }}</h2>
          <button class="drawer-close-btn" @click="emit('close')">✕</button>
        </div>

        <!-- Body -->
        <div class="drawer-body">
          <slot></slot>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.38);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 80;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.drawer-panel {
  width: 100%;
  max-height: 88%;
  background: #0b0f17;
  border-top-left-radius: 14px;
  border-top-right-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-bottom: none;
  box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #f8fafc;
}

.drawer-handle-zone {
  display: flex;
  justify-content: center;
  padding: 10px 0 2px;
}

.handle {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.18);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.drawer-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.2px;
}

.drawer-close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  transition: color 0.15s ease;
}

.drawer-close-btn:hover {
  color: rgba(255, 255, 255, 0.9);
}

.drawer-body {
  padding: 18px 24px 28px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.drawer-enter-active, .drawer-leave-active {
  transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.28s ease;
}

.drawer-enter-from, .drawer-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
