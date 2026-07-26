import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { CandidateProduct, IdentifyResult, VerificationResult } from '../../types/api'
import type { RecommendationProduct } from '../../mock/recommendationData'
import type { PriceChannel } from '../../mock/priceComparisonData'

export const useSessionStore = defineStore('session', () => {
  const videoId = ref('demo_video_001')
  const categoryId = ref('')
  const selectedProduct = ref<CandidateProduct | null>(null)
  const identifyResult = ref<IdentifyResult | null>(null)
  const verificationResult = ref<VerificationResult | null>(null)
  const selectedPriceProduct = ref<CandidateProduct | RecommendationProduct | null>(null)
  const recommendationProducts = ref<RecommendationProduct[]>([])
  const selectedRecommendation = ref<RecommendationProduct | null>(null)
  const priceChannels = ref<PriceChannel[]>([])
  const inheritedConditions = ref<Record<string, unknown>>({})

  const hasProduct = computed(() => Boolean(selectedProduct.value && categoryId.value))

  function setIdentification(result: IdentifyResult) {
    identifyResult.value = result
    categoryId.value = result.category_id
  }

  function setProduct(product: CandidateProduct) {
    selectedProduct.value = product
  }

  function setVerificationResult(result: VerificationResult) {
    verificationResult.value = result
  }

  function setSelectedPriceProduct(product: CandidateProduct | RecommendationProduct) {
    selectedPriceProduct.value = product
  }

  /**
   * 从“继续筛选”重新进入标准验真入口。
   * 保留当前视频，清除上一轮识别、商品与验真结论，避免把旧结果带入新一轮。
   */
  function restartVerification() {
    categoryId.value = ''
    selectedProduct.value = null
    identifyResult.value = null
    verificationResult.value = null
    selectedPriceProduct.value = null
    inheritedConditions.value = {}
  }

  return {
    videoId,
    categoryId,
    selectedProduct,
    identifyResult,
    verificationResult,
    selectedPriceProduct,
    recommendationProducts,
    selectedRecommendation,
    priceChannels,
    inheritedConditions,
    hasProduct,
    setIdentification,
    setProduct,
    setVerificationResult,
    setSelectedPriceProduct,
    restartVerification,
  }
})
