<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { ConditionField } from '../../types/api'

const props = defineProps<{
  fields: ConditionField[]
  modelValue?: Record<string, unknown>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, unknown>]
}>()

const formData = reactive<Record<string, unknown>>({ ...props.modelValue })

watch(formData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

function setStringValue(key: string, val: string) {
  formData[key] = val
}

function setNumberValue(key: string, val: string) {
  formData[key] = val === '' ? undefined : Number(val)
}

function setBooleanValue(key: string, checked: boolean) {
  formData[key] = checked
}

function toggleMultiSelect(field: ConditionField, option: string) {
  const current = Array.isArray(formData[field.key]) ? [...(formData[field.key] as string[])] : []
  if (current.includes(option)) {
    formData[field.key] = current.filter((item) => item !== option)
  } else {
    formData[field.key] = [...current, option]
  }
}

function isMultiSelected(key: string, option: string): boolean {
  return Array.isArray(formData[key]) && (formData[key] as string[]).includes(option)
}

function getStringValue(key: string): string {
  return typeof formData[key] === 'string' ? (formData[key] as string) : ''
}

function getNumberValue(key: string): string | number {
  return typeof formData[key] === 'number' || typeof formData[key] === 'string'
    ? (formData[key] as string | number)
    : ''
}
</script>

<template>
  <div class="dynamic-form-container">
    <div v-for="field in fields" :key="field.key" class="form-item">
      <label :for="`field-${field.key}`" class="field-label">
        <span class="label-text">{{ field.label }}</span>
        <span v-if="field.required" class="required-star">*</span>
      </label>

      <!-- single_select -->
      <div v-if="field.type === 'single_select'" class="select-wrapper">
        <select
          :id="`field-${field.key}`"
          :value="getStringValue(field.key)"
          :required="field.required"
          class="dark-input dark-select"
          @change="setStringValue(field.key, ($event.target as HTMLSelectElement).value)"
        >
          <option value="" disabled selected>请选择{{ field.label }}</option>
          <option v-for="opt in field.options" :key="opt" :value="opt">
            {{ opt }}
          </option>
        </select>
        <span class="select-arrow">▼</span>
      </div>

      <!-- multi_select -->
      <div v-else-if="field.type === 'multi_select'" class="chip-group">
        <button
          v-for="opt in field.options"
          :key="opt"
          type="button"
          class="chip-button"
          :class="{ active: isMultiSelected(field.key, opt) }"
          @click="toggleMultiSelect(field, opt)"
        >
          <span class="chip-icon">{{ isMultiSelected(field.key, opt) ? '✓' : '+' }}</span>
          {{ opt }}
        </button>
      </div>

      <!-- number -->
      <div v-else-if="field.type === 'number'" class="input-wrapper">
        <input
          :id="`field-${field.key}`"
          type="number"
          :value="getNumberValue(field.key)"
          :min="field.min ?? undefined"
          :max="field.max ?? undefined"
          :required="field.required"
          placeholder="请输入数值"
          class="dark-input"
          @input="setNumberValue(field.key, ($event.target as HTMLInputElement).value)"
        />
      </div>

      <!-- text -->
      <div v-else-if="field.type === 'text'" class="input-wrapper">
        <textarea
          :id="`field-${field.key}`"
          :value="getStringValue(field.key)"
          rows="3"
          :required="field.required"
          placeholder="请输入具体要求或描述…"
          class="dark-input dark-textarea"
          @input="setStringValue(field.key, ($event.target as HTMLInputElement).value)"
        ></textarea>
      </div>

      <!-- boolean -->
      <div v-else-if="field.type === 'boolean'" class="toggle-wrapper">
        <label class="toggle-switch">
          <input
            :id="`field-${field.key}`"
            type="checkbox"
            :checked="formData[field.key] === true"
            :required="field.required"
            @change="setBooleanValue(field.key, ($event.target as HTMLInputElement).checked)"
          />
          <span class="toggle-slider"></span>
        </label>
        <span class="toggle-text">{{ formData[field.key] ? '是 / 开启' : '否 / 关闭' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dynamic-form-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required-star {
  color: #ff4d4f;
}

.dark-input {
  width: 100%;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 12px 16px;
  color: #f8fafc;
  font-size: 14px;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.dark-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
  background: rgba(15, 23, 42, 0.85);
}

.select-wrapper {
  position: relative;
}

.dark-select {
  appearance: none;
  cursor: pointer;
  padding-right: 36px;
}

.select-arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 10px;
  pointer-events: none;
}

.dark-textarea {
  resize: vertical;
  min-height: 80px;
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip-button:hover {
  border-color: rgba(56, 189, 248, 0.4);
  color: #f8fafc;
  background: rgba(30, 41, 59, 0.9);
}

.chip-button.active {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.25));
  border-color: #10b981;
  color: #34d399;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
}

.chip-icon {
  font-size: 12px;
  font-weight: 700;
}

.toggle-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 26px;
  transition: 0.3s;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: #94a3b8;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .toggle-slider {
  background: linear-gradient(90deg, #06b6d4, #3b82f6);
  border-color: #38bdf8;
}

input:checked + .toggle-slider:before {
  transform: translateX(22px);
  background-color: #ffffff;
}

.toggle-text {
  font-size: 13px;
  color: #94a3b8;
}
</style>
