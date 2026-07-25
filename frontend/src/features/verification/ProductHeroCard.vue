<script setup lang="ts">
import type { CandidateProduct } from '../../types/api'

defineProps<{
  product?: CandidateProduct | null
  categoryName?: string
}>()
</script>

<template>
  <div class="product-hero-card-container">
    <div class="hero-card">
      <div class="product-thumb-slot">
        <img
          v-if="product?.image_url"
          :src="product.image_url"
          :alt="product.product_name"
          class="product-img"
        />
      </div>

      <div class="product-info-col">
        <h3 class="product-title">
          {{ product?.product_name || '轻量化电竞鼠标 G Pro' }}
        </h3>
        <span class="category-name">
          {{ categoryName || '鼠标/电竞游戏鼠标' }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-hero-card-container {
  width: 100%;
}

.hero-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
}

.product-thumb-slot {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
  overflow: hidden;
}

.product-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.product-title {
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  line-height: 1.3;
}

.category-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.tag-badge-row {
  margin-top: 2px;
}

.game-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  padding: 2px 8px;
  border-radius: 12px;
}
</style>
