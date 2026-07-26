<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'

import PhonePreviewShell from '../../components/common/PhonePreviewShell.vue'

const router = useRouter()
</script>

<template>
  <PhonePreviewShell>
  <section class="comparison-page-shell">
    <header class="comparison-header">
      <button type="button" aria-label="返回上一级" @click="router.back()">
        <ChevronLeft :size="21" :stroke-width="1.9" />
      </button>
      <h1>多商品横评</h1>
      <span aria-hidden="true"></span>
    </header>
    <div class="page-header">
      <div class="badge">STEP 04 · 第二阶段入口</div>
      <h2>多商品横评对比</h2>
      <p class="subtitle">第一版保留稳定的大模型多方案横向对比队列与数据合同入口</p>
    </div>

    <div class="comparison-panel">
      <div class="placeholder-icon">📊</div>
      <h2>多维横评功能准备中</h2>
      <p class="desc-text">
        你选定的目标商品及分析结果已成功暂存至横评对比队列中。第二阶段将支持多候选商品规格参数、全网正负向舆情及价格性价比的矩阵式呈现。
      </p>

      <div class="mock-comparison-table">
        <div class="table-header">
          <span>对比维度</span>
          <span class="active-col">Logitech G Pro</span>
          <span>Razer Viper V2</span>
        </div>
        <div class="table-row">
          <span class="label">综合推荐度</span>
          <span class="val highlight">82%</span>
          <span class="val">78%</span>
        </div>
        <div class="table-row">
          <span class="label">重量规格</span>
          <span class="val">63g (轻量)</span>
          <span class="val">58g</span>
        </div>
        <div class="table-row">
          <span class="label">全网低价</span>
          <span class="val">￥299 起</span>
          <span class="val">￥429 起</span>
        </div>
      </div>

      <div class="action-row">
        <button class="back-btn" @click="router.back()">
          &lt; 返回主验真结果
        </button>
      </div>
    </div>
  </section>
  </PhonePreviewShell>
</template>

<style scoped>
.comparison-page-shell {
  width: 100%;
  padding: 0 14px 24px;
  box-sizing: border-box;
  margin: 0 auto;
}

.comparison-header {
  min-height: 56px;
  margin: 0 -14px 18px;
  padding: 0 14px;
  display: grid;
  grid-template-columns: 36px 1fr 36px;
  align-items: center;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid #ececee;
}

.comparison-header button {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: #34353b;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.comparison-header h1 {
  margin: 0;
  color: #161823;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 10px;
}

h2 {
  font-size: 22px;
  font-weight: 800;
  color: #161823;
  margin: 0 0 8px;
}

.subtitle {
  color: #707178;
  font-size: 14px;
}

.comparison-panel {
  background: #ffffff;
  border: 1px solid #ececee;
  border-radius: 16px;
  padding: 20px 14px;
  text-align: center;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 14px rgba(22, 24, 35, 0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.placeholder-icon {
  font-size: 48px;
}

h2 {
  font-size: 20px;
  color: #161823;
  margin: 0;
}

.desc-text {
  font-size: 14px;
  color: #616269;
  max-width: 540px;
  line-height: 1.6;
}

.mock-comparison-table {
  width: 100%;
  max-width: 560px;
  background: #f7f7f8;
  border: 1px solid #ececee;
  border-radius: 16px;
  overflow: hidden;
  margin: 10px 0;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 12px 16px;
  font-size: 13px;
}

.table-header {
  background: #f1f1f2;
  font-weight: 700;
  color: #707178;
}

.active-col {
  color: #fe2c55;
}

.table-row {
  border-top: 1px solid #ececee;
  color: #4d4e54;
}

.table-row .label {
  font-weight: 600;
  text-align: left;
}

.table-row .highlight {
  color: #00a69f;
  font-weight: 800;
}

.action-row {
  margin-top: 10px;
}

.back-btn {
  background: #2563eb;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}
</style>
