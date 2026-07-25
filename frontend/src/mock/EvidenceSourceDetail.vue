<script setup lang="ts">
import { ChevronUp, ExternalLink, ThumbsUp } from 'lucide-vue-next'
import type { EvidenceItem } from './evidenceData'

defineProps<{
  item: EvidenceItem | null
}>()
</script>

<template>
  <section
    v-if="item?.source"
    class="source-detail"
  >
    <header class="source-detail__header">
      <span>来源详情</span>
      <ChevronUp :size="16" />
    </header>

    <div class="source-detail__content">
      <div class="source-detail__label">
        <span>{{ item.source.sourceLabel }}</span>
        <span>·</span>
        <span>{{ item.title }}</span>
      </div>

      <blockquote>
        “{{ item.source.quote }}”
      </blockquote>

      <footer>
        <span>
          来源：{{ item.source.platform }} · {{ item.source.author }}
        </span>

        <span
          v-if="item.source.likes !== undefined"
          class="source-detail__likes"
        >
          <ThumbsUp :size="14" />
          点赞 {{ item.source.likes }}
        </span>

        <a
          v-if="item.source.originalUrl"
          :href="item.source.originalUrl"
          class="source-detail__link"
          @click.prevent
        >
          查看原评论
          <ExternalLink :size="13" />
        </a>
      </footer>
    </div>
  </section>
</template>

<style scoped>
.source-detail {
  overflow: hidden;
  background: rgba(7, 18, 29, 0.93);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
}

.source-detail__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 36px;
  padding: 0 11px;

  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.source-detail__content {
  padding: 0 11px 10px;
}

.source-detail__label {
  display: flex;
  gap: 5px;
  align-items: center;

  font-size: 10px;
  color: rgba(255, 255, 255, 0.58);
}

.source-detail__label span:first-child {
  padding: 3px 5px;
  background: rgba(255, 255, 255, 0.07);
  border-radius: 4px;
}

blockquote {
  margin: 8px 0;
  font-size: 11px;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.82);
}

footer {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

.source-detail__likes,
.source-detail__link {
  display: inline-flex;
  gap: 4px;
  align-items: center;
}

.source-detail__link {
  margin-left: auto;
  color: #55a8ff;
  text-decoration: none;
}
</style>
