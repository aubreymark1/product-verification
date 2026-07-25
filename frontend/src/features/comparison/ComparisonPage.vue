<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <section class="comparison-page-shell">
    <div class="page-header">
      <div class="badge">STEP 04 · 第二阶段入口</div>
      <h1>多商品横评对比</h1>
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
        <button class="back-btn" @click="router.push('/verification/res_demo')">
          &lt; 返回主验真结果
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.comparison-page-shell {
  max-width: 720px;
  margin: 0 auto;
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

h1 {
  font-size: 28px;
  font-weight: 800;
  color: #f8fafc;
  margin: 0 0 8px;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
}

.comparison-panel {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 32px;
  text-align: center;
  backdrop-filter: blur(12px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
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
  color: #f8fafc;
  margin: 0;
}

.desc-text {
  font-size: 14px;
  color: #cbd5e1;
  max-width: 540px;
  line-height: 1.6;
}

.mock-comparison-table {
  width: 100%;
  max-width: 560px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  background: rgba(15, 23, 42, 0.8);
  font-weight: 700;
  color: #94a3b8;
}

.active-col {
  color: #38bdf8;
}

.table-row {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
}

.table-row .label {
  font-weight: 600;
  text-align: left;
}

.table-row .highlight {
  color: #34d399;
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
