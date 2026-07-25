<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { ChevronRight, ShoppingCart, X } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'

const router = useRouter()
const session = useSessionStore()
const showChannelsModal = ref(false)

const emit = defineEmits<{
  navigate: []
}>()

interface DisplayChannel {
  platform: string
  price: string
  tag: string
}

const channels = ref<DisplayChannel[]>([])

async function loadChannels() {
  const productId = session.selectedProduct?.product_id
  if (!productId) {
    channels.value = []
    return
  }

  try {
    const result = await api.getPurchaseChannels(productId)
    channels.value = result.map((channel) => ({
      platform: channel.channel_name,
      price: "待确认",
      tag: channel.availability === "available" ? "可购买" : channel.note || "待确认",
    }))
  } catch (error) {
    channels.value = []
    console.warn("闁荤姵鍔﹂崢娲箯閸楃偑鈧帡鎮╃拋鍐差棜闂佸憡姊绘慨鎯归崶銊ョ窞閺夊牜鍋夎", error)
  }
}


onMounted(() => { void loadChannels() })
watch(() => session.selectedProduct?.product_id, () => { void loadChannels() })
function openModal() {
  emit('navigate')
  router.push('/price-comparison')
}

function closeModal() {
  showChannelsModal.value = false
}
</script>

<template>
  <div class="multi-channel-container">
    <!-- Gradient Glow Banner Card (Matching Screenshot) -->
    <div class="purple-glow-card" @click="openModal">
      <div class="card-left-section">
        <div class="cart-icon-box">
          <ShoppingCart :size="19" :stroke-width="1.8" />
        </div>
        <div class="text-group">
          <div class="title-row">
            <span class="main-title">查看全网低价</span>
            <ChevronRight class="arrow-sym" :size="15" :stroke-width="1.8" />
          </div>
          <span class="sub-title">低价快比，放心买</span>
        </div>
      </div>

      <div class="card-right-section">
        <div class="platform-badges-row">
          <span class="app-icon app-icon--tmall" aria-label="天猫"></span>
          <span class="app-icon app-icon--jd" aria-label="京东"></span>
          <span class="summary-text">{{ channels.length }}源比价</span>
          <span class="app-icon app-icon--douyin" aria-label="抖音"></span>
          <span class="app-icon app-icon--pdd" aria-label="拼多多"></span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showChannelsModal" class="modal-backdrop" @click.self="closeModal">
      <div class="channel-modal">
        <div class="modal-header">
          <div>
            <h3>全网比价汇总（{{ channels.length }}个渠道）</h3>
            <span class="demo-tag">已配置渠道数据</span>
          </div>
          <button class="close-btn" aria-label="关闭" @click="closeModal">
            <X :size="18" :stroke-width="1.8" />
          </button>
        </div>

        <div class="channel-list">
          <div v-for="c in channels" :key="c.platform" class="channel-item">
            <div class="item-meta">
              <span class="platform-name">{{ c.platform }}</span>
              <span class="tag-chip">{{ c.tag }}</span>
            </div>
            <div class="item-price">
              <span class="price-val">{{ c.price }}</span>
              <button class="buy-btn" @click="closeModal">前往</button>
            </div>
          </div>
        </div>

        <button class="modal-close-bar" @click="closeModal">返回验真结果</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-channel-container {
  width: 100%;
}

.purple-glow-card {
  position: relative;
  overflow: hidden;
  display: flex;
  gap: 8px;
  justify-content: space-between;
  align-items: center;
  background:
    radial-gradient(circle at 0% 50%, rgba(137, 65, 255, 0.18), transparent 42%),
    rgba(13, 24, 38, 0.82);
  border: 1px solid transparent;
  border-radius: 14px;
  background-clip: padding-box;
  padding: 16px 12px;
  cursor: pointer;
  box-shadow:
    inset 0 0 16px rgba(166, 132, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 0 18px rgba(164, 70, 255, 0.3),
    0 0 26px rgba(31, 119, 255, 0.22),
    0 8px 18px rgba(0, 0, 0, 0.14);
  transition: all 0.2s ease;
}

.purple-glow-card::before {
  position: absolute;
  inset: 0;
  padding: 1px;
  pointer-events: none;
  background: linear-gradient(105deg, #a744ff 0%, #7d42ff 34%, #1f7dff 72%, #2da9ff 100%);
  border-radius: 14px;
  content: "";
  mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  mask-composite: exclude;
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
}

.purple-glow-card::after {
  position: absolute;
  inset: 1px;
  pointer-events: none;
  border: 1px solid rgba(138, 92, 246, 0.14);
  border-radius: 13px;
  box-shadow:
    inset 8px 0 20px rgba(164, 70, 255, 0.12),
    inset -8px 0 20px rgba(31, 125, 255, 0.1),
    0 0 24px rgba(164, 70, 255, 0.2),
    0 0 30px rgba(31, 125, 255, 0.16);
  content: "";
}

.purple-glow-card:hover {
  background: rgba(18, 31, 49, 0.88);
  box-shadow:
    inset 0 0 16px rgba(166, 132, 255, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 0 22px rgba(164, 70, 255, 0.38),
    0 0 32px rgba(31, 119, 255, 0.28),
    0 8px 18px rgba(0, 0, 0, 0.14);
}

.card-left-section {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: max-content;
}

.cart-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: transparent;
  border: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.text-group {
  display: flex;
  flex-direction: column;
  min-width: max-content;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: max-content;
}

.main-title {
  flex: 0 0 auto;
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
  white-space: nowrap;
}

.arrow-sym {
  color: #c084fc;
}

.sub-title {
  display: block;
  max-width: 118px;
  overflow: hidden;
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.52);
  margin-top: 6px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-right-section {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1 1 auto;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  min-width: 0;
}

.platform-badges-row {
  display: flex;
  align-items: center;
  gap: 5px;
  max-width: 100%;
  overflow: hidden;
}

.app-icon {
  position: relative;
  flex: 0 0 auto;
  width: 22px;
  height: 22px;
  overflow: hidden;
  border-radius: 6px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.22),
    0 4px 10px rgba(0, 0, 0, 0.22);
}

.app-icon--tmall {
  background: linear-gradient(145deg, #ff3150, #c8002b);
}

.app-icon--tmall::before {
  position: absolute;
  top: 5px;
  left: 5px;
  width: 12px;
  height: 10px;
  background: #fff;
  border-radius: 6px 6px 4px 4px;
  clip-path: polygon(0 30%, 17% 0, 32% 28%, 68% 28%, 83% 0, 100% 30%, 100% 100%, 0 100%);
  content: "";
}

.app-icon--tmall::after {
  position: absolute;
  top: 10px;
  left: 8px;
  width: 2px;
  height: 2px;
  background: #c8002b;
  border-radius: 50%;
  box-shadow: 5px 0 0 #c8002b;
  content: "";
}

.app-icon--jd {
  background: linear-gradient(145deg, #f7f7fb, #dfe5f0);
}

.app-icon--jd::before {
  position: absolute;
  top: 5px;
  left: 5px;
  width: 12px;
  height: 12px;
  background: #d71024;
  border-radius: 50%;
  content: "";
}

.app-icon--jd::after {
  position: absolute;
  top: 9px;
  left: 9px;
  width: 4px;
  height: 4px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 -5px 0 -1px #d71024, 5px -2px 0 -1px #d71024;
  content: "";
}

.app-icon--douyin {
  background: #05070b;
}

.app-icon--douyin::before {
  position: absolute;
  top: 4px;
  left: 8px;
  width: 7px;
  height: 12px;
  border-right: 3px solid #fff;
  border-bottom: 3px solid #fff;
  border-radius: 0 0 7px 7px;
  box-shadow:
    -2px 1px 0 #00f2ea,
    2px -1px 0 #ff0050;
  content: "";
}

.app-icon--douyin::after {
  position: absolute;
  top: 12px;
  left: 5px;
  width: 7px;
  height: 7px;
  border: 3px solid #fff;
  border-radius: 50%;
  box-shadow:
    -1px 1px 0 #00f2ea,
    1px -1px 0 #ff0050;
  content: "";
}

.app-icon--pdd {
  background: linear-gradient(145deg, #ff4c5d, #d9192f);
}

.app-icon--pdd::before {
  position: absolute;
  inset: 5px;
  background:
    linear-gradient(45deg, transparent 40%, #fff 42% 58%, transparent 60%),
    linear-gradient(-45deg, transparent 40%, #fff 42% 58%, transparent 60%);
  border: 2px solid #fff;
  border-radius: 3px;
  transform: rotate(45deg);
  content: "";
}

.summary-text {
  flex: 0 0 auto;
  padding: 3px 6px;
  font-size: 10px;
  font-weight: 500;
  line-height: 1;
  color: rgba(230, 236, 255, 0.82);
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(166, 132, 255, 0.16);
  border-radius: 999px;
}

@media (max-width: 380px) {
  .purple-glow-card {
    padding: 14px 11px;
  }

  .cart-icon-box {
    width: 40px;
    height: 40px;
  }

  .sub-title {
    max-width: 104px;
  }

  .summary-text {
    display: none;
  }
}

@media (max-width: 370px) {
  .card-right-section {
    display: none;
  }

  .sub-title {
    max-width: 160px;
  }
}

@media (max-width: 350px) {
  .sub-title {
    max-width: 136px;
  }
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 15, 29, 0.85);
  backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.channel-modal {
  width: 100%;
  max-width: 420px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 18px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-header h3 {
  margin: 0 0 2px;
  font-size: 15px;
  font-weight: 600;
}

.demo-tag {
  font-size: 11px;
  font-weight: 400;
  color: #64748b;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.platform-name {
  font-size: 13px;
  font-weight: 600;
}

.tag-chip {
  font-size: 12px;
  font-weight: 400;
  color: #38bdf8;
}

.item-price {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-val {
  font-size: 15px;
  font-weight: 600;
  color: #f43f5e;
}

.buy-btn {
  background: #2563eb;
  border: none;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
}

.modal-close-bar {
  width: 100%;
  padding: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
</style>
