<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import StatusMessage from '../../components/common/StatusMessage.vue'
import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { IdentifyResult, Video } from '../../types/api'

const router = useRouter()
const session = useSessionStore()
const video = ref<Video | null>(null)
const candidates = ref<IdentifyResult | null>(null)
const loading = ref(true)
const error = ref('')
const selecting = ref(false)
const identifying = ref(false)

onMounted(async () => {
  try { video.value = await api.getVideo(session.videoId) } catch (err) { error.value = err instanceof Error ? err.message : '视频加载失败' } finally { loading.value = false }
})

async function identifyObject() {
  if (!video.value?.objects[0]) return
  selecting.value = true
  identifying.value = true
  try {
    const object = video.value.objects[0]
    candidates.value = await api.identify(video.value.video_id, 0, object.bbox)
    session.setIdentification(candidates.value)
  } catch (err) { error.value = err instanceof Error ? err.message : '识别失败' } finally { identifying.value = false }
}

function confirmProduct(product: IdentifyResult['candidates'][number]) {
  session.setProduct(product)
  router.push('/conditions')
}
</script>

<template>
  <section>
    <div class="page-header"><p class="card-kicker">第一版 Mock 纵向流程</p><h1>从视频里开始验一验</h1><p>先选择演示对象，系统会根据品类配置继续询问使用条件。</p></div>
    <StatusMessage v-if="loading" type="loading" message="正在加载演示视频信息…" />
    <StatusMessage v-else-if="error" type="error" :message="error" />
    <template v-else-if="video">
      <div class="panel">
        <div class="video-stage">
          <div class="stage-copy"><strong>{{ video.title }}</strong><br /><small>无真实视频文件 · 当前为联调占位画面</small></div>
          <div v-for="object in video.objects" :key="object.object_id" class="bbox" :style="{ left: `${object.bbox.x * 100}%`, top: `${object.bbox.y * 100}%`, width: `${object.bbox.width * 100}%`, height: `${object.bbox.height * 100}%` }">
            <button :aria-label="`选择${object.label}`" @click="identifyObject">{{ selecting ? object.label : '可选对象' }}</button>
          </div>
        </div>
        <div class="actions"><button class="primary-button" :disabled="identifying" @click="identifyObject">{{ identifying ? '识别中…' : '验一验' }}</button><span v-if="selecting" class="card-kicker">已暂停演示，点击对象框确认选择</span></div>
      </div>
      <div v-if="candidates" class="panel" style="margin-top: 18px"><h2>候选商品确认</h2><p class="card-kicker">请选择最符合的视频对象的候选项。</p><div class="grid candidate-grid"><article v-for="candidate in candidates.candidates" :key="candidate.product_id" class="candidate-card"><h3>{{ candidate.product_name }}</h3><p>匹配置信度：{{ Math.round(candidate.confidence * 100) }}%</p><button class="secondary-button" @click="confirmProduct(candidate)">确认并填写条件</button></article></div></div>
    </template>
  </section>
</template>
