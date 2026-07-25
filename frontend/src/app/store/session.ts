import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { CandidateProduct, IdentifyResult, VerificationResult } from '../../types/api'

export const useSessionStore = defineStore('session', () => {
  const videoId = ref('demo_video_001')
  const categoryId = ref('')
  const selectedProduct = ref<CandidateProduct | null>(null)
  const identifyResult = ref<IdentifyResult | null>(null)
  const verificationResult = ref<VerificationResult | null>(null)

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

  return { videoId, categoryId, selectedProduct, identifyResult, verificationResult, hasProduct, setIdentification, setProduct, setVerificationResult }
})
