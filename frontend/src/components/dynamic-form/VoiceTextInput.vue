<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

export type VoiceState = 'idle' | 'listening' | 'transcribing' | 'done'

export interface StructuredRequirements {
  budgetMax?: number
  primaryUsage?: string
  connection?: string
  preferences?: string[]
}

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'structuredChange': [req: StructuredRequirements]
  'confirm': []
}>()

const voiceState = ref<VoiceState>('idle')
const textContent = ref(props.modelValue || '')

// Structured requirements state
const structuredReq = ref<StructuredRequirements>({})

// Timer references to prevent memory leaks / duplicate executions
let listeningTimer: number | null = null
let transcribingTimer: number | null = null
let typewriterTimer: number | null = null

const fullText = '预算300元以内，主要玩FPS，希望无线、轻量、低延迟。'

function clearAllTimers() {
  if (listeningTimer !== null) {
    clearTimeout(listeningTimer)
    listeningTimer = null
  }
  if (transcribingTimer !== null) {
    clearTimeout(transcribingTimer)
    transcribingTimer = null
  }
  if (typewriterTimer !== null) {
    clearInterval(typewriterTimer)
    typewriterTimer = null
  }
}

onUnmounted(() => {
  clearAllTimers()
})

function handleVoiceButtonClick() {
  // Prevent clicks during active listening or transcribing
  if (voiceState.value === 'listening' || voiceState.value === 'transcribing') {
    return
  }

  // Clear previous timers and text if re-triggering from 'done'
  clearAllTimers()

  if (voiceState.value === 'done') {
    // Reset old transcription
    textContent.value = ''
    structuredReq.value = {}
    emit('update:modelValue', '')
    emit('structuredChange', {})
  }

  // 1. Transition to 'listening' (~1s)
  voiceState.value = 'listening'

  listeningTimer = window.setTimeout(() => {
    // 2. Transition to 'transcribing' (~0.6s total for typewriter)
    voiceState.value = 'transcribing'
    textContent.value = ''
    let charIndex = 0

    const totalDuration = 600 // 0.6 seconds
    const intervalTime = Math.floor(totalDuration / fullText.length)

    typewriterTimer = window.setInterval(() => {
      if (charIndex < fullText.length) {
        textContent.value += fullText[charIndex]
        emit('update:modelValue', textContent.value)
        charIndex++
      } else {
        if (typewriterTimer !== null) {
          clearInterval(typewriterTimer)
          typewriterTimer = null
        }

        // 3. Transition to 'done' and fill structured requirements
        voiceState.value = 'done'
        const structured: StructuredRequirements = {
          budgetMax: 300,
          primaryUsage: 'FPS',
          connection: 'wireless',
          preferences: ['lightweight', 'low_latency'],
        }
        structuredReq.value = structured
        emit('structuredChange', structured)
      }
    }, intervalTime)
  }, 1000)
}

function onManualInput(e: Event) {
  const val = (e.target as HTMLTextAreaElement).value
  textContent.value = val
  emit('update:modelValue', val)
}

function onConfirmRequirements() {
  emit('confirm')
}
</script>

<template>
  <div class="voice-input-card">
    <div class="card-header">
      <span class="header-title">语音 / 文本需求描述</span>
      <span class="header-badge">AI 识别流</span>
    </div>

    <!-- Manual Text Area -->
    <div class="textarea-wrapper">
      <textarea
        :value="textContent"
        rows="3"
        placeholder="点击“语音输入”自动识别，或在此输入个性化使用需求…"
        class="custom-textarea"
        @input="onManualInput"
      ></textarea>
    </div>

    <!-- Voice Control Button Bar -->
    <div class="voice-action-bar">
      <button
        type="button"
        class="voice-state-button"
        :class="voiceState"
        :disabled="voiceState === 'listening' || voiceState === 'transcribing'"
        @click="handleVoiceButtonClick"
      >
        <!-- Ripple Animation for Listening State -->
        <span v-if="voiceState === 'listening'" class="ripple-ring"></span>

        <!-- Microphone SVG Icon for idle / listening -->
        <svg
          v-if="voiceState === 'idle' || voiceState === 'listening'"
          class="btn-svg-icon"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="22"></line>
        </svg>

        <!-- Loading Spinner SVG for transcribing state -->
        <svg
          v-else-if="voiceState === 'transcribing'"
          class="btn-svg-icon spinner"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
        >
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="12"></circle>
        </svg>

        <!-- Refresh SVG Icon for done state -->
        <svg
          v-else-if="voiceState === 'done'"
          class="btn-svg-icon"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>

        <span class="button-label">
          <template v-if="voiceState === 'idle'">语音输入</template>
          <template v-else-if="voiceState === 'listening'">正在聆听...</template>
          <template v-else-if="voiceState === 'transcribing'">正在识别需求</template>
          <template v-else-if="voiceState === 'done'">重新输入</template>
        </span>
      </button>
    </div>

    <!-- Generated Tags Display (Synchronous Output) -->
    <div v-if="voiceState === 'done' || structuredReq.budgetMax" class="generated-tags-section">
      <span class="tags-title">解析结果标签：</span>
      <div class="tag-pills-row">
        <span class="tag-pill">预算 ≤ 300元</span>
        <span class="tag-pill">FPS</span>
        <span class="tag-pill">无线</span>
        <span class="tag-pill">轻量化</span>
        <span class="tag-pill">低延迟</span>
      </div>
    </div>

    <!-- Confirm Requirements Action Button -->
    <div class="confirm-bar">
      <button type="button" class="confirm-req-btn" @click="onConfirmRequirements">
        <span>确认需求</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.voice-input-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 14px;
  font-weight: 700;
  color: #f8fafc;
}

.header-badge {
  font-size: 11px;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 2px 8px;
  border-radius: 10px;
}

.textarea-wrapper {
  width: 100%;
}

.custom-textarea {
  width: 100%;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 12px;
  color: #f8fafc;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
}

.custom-textarea:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
}

.voice-action-bar {
  display: flex;
  align-items: center;
}

.voice-state-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.25s ease;
  user-select: none;
}

/* State Styling */
.voice-state-button.idle {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(56, 189, 248, 0.4);
  color: #38bdf8;
}

.voice-state-button.idle:hover {
  background: rgba(56, 189, 248, 0.2);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}

.voice-state-button.listening {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #f87171;
}

.voice-state-button.transcribing {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  color: #22d3ee;
}

.voice-state-button.done {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #34d399;
}

.voice-state-button.done:hover {
  background: rgba(16, 185, 129, 0.3);
}

/* SVG Animations */
.spinner {
  animation: spin 1s linear infinite;
}

.ripple-ring {
  position: absolute;
  inset: -4px;
  border-radius: 28px;
  border: 2px solid #ef4444;
  animation: ripple 1.2s cubic-bezier(0, 0.2, 0.8, 1) infinite;
  pointer-events: none;
}

/* Generated Tags */
.generated-tags-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 12px;
  padding: 12px;
}

.tags-title {
  font-size: 12px;
  color: #34d399;
  font-weight: 600;
}

.tag-pills-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-pill {
  font-size: 12px;
  font-weight: 500;
  color: #34d399;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 4px 10px;
  border-radius: 14px;
}

.confirm-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}

.confirm-req-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #2563eb, #06b6d4);
  border: none;
  border-radius: 10px;
  padding: 8px 16px;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.confirm-req-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@keyframes ripple {
  0% { transform: scale(0.95); opacity: 1; }
  100% { transform: scale(1.15); opacity: 0; }
}
</style>
