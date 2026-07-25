<script setup lang="ts">
import { computed } from 'vue'
import type { CandidateProduct } from '../../types/api'
import type { DemoInsights } from '../../types/api'

const props = defineProps<{
  product?: CandidateProduct | null
  categoryName?: string
  demoInsights?: DemoInsights | null
}>()

const averageRating = computed(() => {
  const reviews = props.demoInsights?.reviews ?? []
  if (!reviews.length) return null
  return reviews.reduce((total, review) => total + review.rating, 0) / reviews.length
})
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
        <p class="product-features">轻量化 · 无线连接 · 电竞使用</p>
        <div v-if="averageRating !== null" class="hero-review-summary">
          <span class="hero-review-label">用户口碑</span>
          <strong>★ {{ averageRating.toFixed(1) }}</strong>
          <span>· {{ demoInsights?.reviews.length }} 条</span>
          <span class="hero-demo-mark">演示</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.product-hero-card-container {
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.hero-card {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  align-items: start;
  column-gap: 12px;
  min-width: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
}

.product-thumb-slot {
  width: 92px;
  height: 92px;
  border-radius: 16px;
  background:
    radial-gradient(circle at 35% 22%, rgba(255, 255, 255, 0.1), transparent 42%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.025));
  border: 1px solid rgba(255, 255, 255, 0.075);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.045),
    0 12px 24px rgba(0, 0, 0, 0.18);
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
  gap: 0;
  flex: 1;
  min-width: 0;
  padding-top: 0;
}

.product-title {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
  line-height: 1.48;
  letter-spacing: 0;
  word-break: normal;
  overflow-wrap: break-word;
}

.product-features {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.46);
  font-size: 11px;
  font-weight: 400;
  line-height: 1.5;
  white-space: normal;
  overflow-wrap: break-word;
}

.hero-review-summary {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 7px;
  color: rgba(255, 255, 255, 0.44);
  font-size: 10px;
}

.hero-review-summary strong {
  color: #ffd37a;
  font-weight: 600;
}

.hero-review-label {
  color: #8de8df;
}

.hero-demo-mark {
  padding: 2px 5px;
  color: #ffc66d;
  border: 1px solid rgba(255, 198, 109, 0.25);
  border-radius: 999px;
  font-size: 9px;
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

@media (max-width: 390px) {
  .hero-card {
    column-gap: 12px;
  }

  .product-thumb-slot {
    width: 92px;
    height: 92px;
    border-radius: 16px;
  }

  .product-title {
    font-size: 13px;
    line-height: 1.48;
  }

  .product-features {
    width: 100%;
  }
}

@media (max-width: 370px) {
  .hero-card {
    grid-template-columns: 82px minmax(0, 1fr);
    column-gap: 10px;
  }

  .product-thumb-slot {
    width: 82px;
    height: 82px;
    border-radius: 14px;
  }

  .product-title {
    font-size: 13px;
  }

}
</style>
