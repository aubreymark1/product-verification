<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import StatusMessage from '../../components/common/StatusMessage.vue'
import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { CategoryProfile, ConditionField } from '../../types/api'

const router = useRouter()
const session = useSessionStore()
const profile = ref<CategoryProfile | null>(null)
const form = reactive<Record<string, unknown>>({})
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

function setStringField(key: string, event: Event) {
  form[key] = (event.target as HTMLInputElement).value
}

function setNumberField(key: string, event: Event) {
  const value = (event.target as HTMLInputElement).value
  form[key] = value === '' ? undefined : Number(value)
}

function setBooleanField(key: string, event: Event) {
  form[key] = (event.target as HTMLInputElement).checked
}

function stringValue(key: string): string {
  return typeof form[key] === 'string' ? form[key] as string : ''
}

function numberValue(key: string): string | number {
  return typeof form[key] === 'number' || typeof form[key] === 'string' ? form[key] as string | number : ''
}

onMounted(async () => {
  if (!session.hasProduct) { error.value = '请先在视频页确认商品'; loading.value = false; return }
  try { profile.value = await api.getProfile(session.categoryId) } catch (err) { error.value = err instanceof Error ? err.message : '品类配置加载失败' } finally { loading.value = false }
})

function toggleMulti(field: ConditionField, option: string) {
  const current = Array.isArray(form[field.key]) ? [...form[field.key] as string[]] : []
  form[field.key] = current.includes(option) ? current.filter((item) => item !== option) : [...current, option]
}

async function submit() {
  if (!session.selectedProduct || !profile.value) return
  submitting.value = true
  error.value = ''
  try {
    const result = await api.runVerification({ video_id: session.videoId, product_id: session.selectedProduct.product_id, category_id: profile.value.category_id, conditions: { ...form }, raw_query: '' })
    session.setVerificationResult(result)
    await router.push(`/verification/${result.result_id}`)
  } catch (err) { error.value = err instanceof Error ? err.message : '验真请求失败' } finally { submitting.value = false }
}
</script>

<template>
  <section><div class="page-header"><p class="card-kicker">第二步 · 动态条件</p><h1>告诉我们你的使用条件</h1><p v-if="session.selectedProduct">当前候选：{{ session.selectedProduct.product_name }}</p></div>
    <StatusMessage v-if="loading" type="loading" message="正在读取品类配置…" /><StatusMessage v-else-if="error && !profile" type="error" :message="error" />
    <form v-else-if="profile" class="panel" @submit.prevent="submit"><p class="card-kicker">字段由“{{ profile.category_name }}”的品类配置驱动。</p>
      <div v-for="field in profile.condition_fields" :key="field.key" class="form-field"><label :for="field.key">{{ field.label }}<span v-if="field.required"> *</span></label>
        <select v-if="field.type === 'single_select'" :id="field.key" :value="stringValue(field.key)" :required="field.required" @change="setStringField(field.key, $event)"><option value="">请选择</option><option v-for="option in field.options" :key="option" :value="option">{{ option }}</option></select>
        <div v-else-if="field.type === 'multi_select'" class="choice-list"><label v-for="option in field.options" :key="option"><input type="checkbox" :checked="Array.isArray(form[field.key]) && (form[field.key] as string[]).includes(option)" @change="toggleMulti(field, option)" /> {{ option }}</label></div>
        <input v-else-if="field.type === 'number'" :id="field.key" :value="numberValue(field.key)" type="number" :min="field.min ?? undefined" :max="field.max ?? undefined" :required="field.required" @input="setNumberField(field.key, $event)" />
        <textarea v-else-if="field.type === 'text'" :id="field.key" :value="stringValue(field.key)" rows="3" :required="field.required" @input="setStringField(field.key, $event)" />
        <input v-else :id="field.key" :checked="form[field.key] === true" type="checkbox" :required="field.required" @change="setBooleanField(field.key, $event)" />
      </div><StatusMessage v-if="error" type="error" :message="error" /><button class="primary-button" type="submit" :disabled="submitting">{{ submitting ? '分析中…' : '提交并开始验真' }}</button>
    </form>
  </section>
</template>
