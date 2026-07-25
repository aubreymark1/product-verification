<script setup lang="ts">
import type { Conclusion } from '../../types/api'

defineProps<{ item: Conclusion; title: string }>()
const emit = defineEmits<{ evidence: [id: string] }>()
</script>

<template>
  <article class="evidence-card">
    <div class="card-kicker">{{ title }} · 置信度 {{ Math.round(item.confidence * 100) }}%</div>
    <p>{{ item.claim }}</p>
    <button v-for="sourceId in item.source_ids" :key="sourceId" class="text-button" @click="emit('evidence', sourceId)">查看证据 {{ sourceId }}</button>
  </article>
</template>
