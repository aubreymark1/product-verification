export type EvidenceType = 'risk' | 'support' | 'pending'

export interface EvidenceSource {
  platform: string
  author: string
  quote: string
  likes?: number
  sourceLabel: string
  originalUrl?: string
}

export interface EvidenceItem {
  id: string
  title: string
  summary?: string
  source?: EvidenceSource
}

export interface EvidenceGroup {
  type: EvidenceType
  title: string
  items: EvidenceItem[]
}

export const mockEvidenceGroups: EvidenceGroup[] = [
  {
    type: 'risk',
    title: '风险证据',
    items: [
      {
        id: 'risk-side-button',
        title: '部分用户反馈侧键存在轻微松动',
        summary: '多条长期使用反馈提及侧键晃动，但暂未影响正常使用。',
        source: {
          platform: '贴吧',
          author: '外设用户_86',
          sourceLabel: '贴吧用户评论',
          quote:
            '用了两周，左侧前进键偶尔会有轻微晃动，不影响使用，但希望品控能再稳定一些。',
          likes: 86,
          originalUrl: '#',
        },
      },
      {
        id: 'risk-battery',
        title: '重度使用情况下需要关注续航',
        summary: '高回报率和灯效开启后，续航时间可能明显缩短。',
        source: {
          platform: '抖音',
          author: '外设实验室',
          sourceLabel: '测评视频评论',
          quote:
            '日常办公续航没有问题，但高回报率连续打游戏时，充电频率会明显增加。',
          likes: 43,
          originalUrl: '#',
        },
      },
    ],
  },
  {
    type: 'support',
    title: '支持证据',
    items: [
      {
        id: 'support-weight',
        title: '鼠标重量轻，长时间使用手感舒适',
        summary: '多位用户认为其重量适合长时间 FPS 游戏。',
        source: {
          platform: '京东',
          author: '已购用户',
          sourceLabel: '电商已购评价',
          quote:
            '重量比之前用的鼠标轻很多，连续打几个小时手腕也没有明显疲劳。',
          likes: 128,
          originalUrl: '#',
        },
      },
      {
        id: 'support-latency',
        title: '低延迟表现优秀，游戏内操作响应及时',
        summary: '多项测评认为无线连接延迟接近有线体验。',
        source: {
          platform: 'B站',
          author: '硬件观察站',
          sourceLabel: '专业测评视频',
          quote:
            '在 FPS 实测中没有感受到明显延迟，快速甩枪和连续点击响应稳定。',
          likes: 352,
          originalUrl: '#',
        },
      },
      {
        id: 'support-build',
        title: '多位测评博主与用户认可手感和做工',
        summary: '握持舒适度和模具成熟度得到较多正向反馈。',
        source: {
          platform: '抖音',
          author: '键鼠研究所',
          sourceLabel: '测评视频',
          quote:
            '模具比较成熟，抓握和趴握都容易适应，整体做工属于同类产品中较稳的一档。',
          likes: 219,
          originalUrl: '#',
        },
      },
    ],
  },
  {
    type: 'pending',
    title: '待确认项',
    items: [
      {
        id: 'pending-polling-rate',
        title: '是否支持 4K 回报率',
        summary: '不同版本及接收器配置可能存在差异，需要确认具体型号。',
      },
      {
        id: 'pending-switch',
        title: '不同批次的微动手感是否存在差异',
        summary: '目前公开评价中存在少量批次差异反馈，证据不足。',
      },
    ],
  },
]