export interface RecommendationProduct {
  product_id: string
  product_name: string
  image_url: string | null
  rank: number
  score: number
  reason: string
  description: string
  evidence: string[]
  price: string
  product_tag: string
  source: string
}

export const recommendationProducts: RecommendationProduct[] = [
  {
    product_id: 'recommendation_g304',
    product_name: '罗技 G304 LIGHTSPEED',
    image_url: null,
    rank: 1,
    score: 93,
    reason: '更适合 FPS 抓握',
    description: '轻量灵活、延迟低，FPS 表现在同价位更优。',
    evidence: ['轻量化约 99g，长时间游戏手不累；', 'LIGHTSPEED 无线延迟接近有线；', '职业选手与 FPS 玩家口碑较高。'],
    price: '249',
    product_tag: '无线游戏鼠标',
    source: '测评视频、玩家社区、电商评价',
  },
  {
    product_id: 'recommendation_viper',
    product_name: '雷蛇 毒蝰 V2 X 极速版',
    image_url: null,
    rank: 2,
    score: 88,
    reason: '更轻更灵活',
    description: '重量更轻，操控跟手，适合高速移动场景。',
    evidence: ['重量约 54g，极致轻量化设计；', 'Focus X 传感器，定位精准；', '用户评价认为比有线鼠标更跟手。'],
    price: '279',
    product_tag: '无线游戏鼠标',
    source: '专业测评、电商评价、玩家反馈',
  },
  {
    product_id: 'recommendation_a950',
    product_name: '达尔优 A950 Air',
    image_url: null,
    rank: 3,
    score: 85,
    reason: '续航更强',
    description: '长续航、三模连接，适合多设备玩家。',
    evidence: ['续航可达约 80 小时；', '支持 2.4G、蓝牙和有线三模连接；', '性价比较高，价格在 300 元以内。'],
    price: '239',
    product_tag: '三模游戏鼠标',
    source: '实验室测试、用户评价、玩家数据',
  },
]
