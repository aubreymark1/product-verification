import axios from 'axios'

import type { ApiResponse, BBox, CategoryProfile, Evidence, IdentifyResult, PurchaseChannel, RerunRecommendationRequest, VerificationRequest, VerificationResult, Video } from '../types/api'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api',
  timeout: 8000,
})

async function unwrap<T>(request: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await request
  if (!response.data.success || response.data.data === null) {
    throw new Error(response.data.error?.message ?? '请求失败')
  }
  return response.data.data
}

export const api = {
  uploadVideo: (file: File) => {
    const body = new FormData()
    body.append('file', file)
    return unwrap<Video>(client.post('/videos/upload', body))
  },
  getVideo: (videoId: string) => unwrap<Video>(client.get(`/videos/${videoId}`)),
  identify: (videoId: string, timestamp: number, selection: BBox) => unwrap<IdentifyResult>(client.post('/vision/identify', { video_id: videoId, timestamp, selection })),
  getProfile: (categoryId: string) => unwrap<CategoryProfile>(client.get(`/categories/${categoryId}/profile`)),
  runVerification: (payload: VerificationRequest) => unwrap<VerificationResult>(client.post('/verification/run', payload)),
  rerunRecommendation: (payload: RerunRecommendationRequest) => unwrap<VerificationResult>(client.post('/recommendations/rerun', payload)),
  getEvidence: (evidenceId: string) => unwrap<Evidence>(client.get(`/evidence/${evidenceId}`)),
  getPurchaseChannels: (productId: string) => unwrap<PurchaseChannel[]>(client.get(`/purchase-channels/${productId}`)),
  addComparison: (payload: { product_id: string; category_id: string; result_id?: string }) => unwrap<{ comparison_id: string; message: string }>(client.post('/comparison/add', payload)),
}
