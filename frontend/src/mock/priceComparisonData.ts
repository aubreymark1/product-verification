export interface PriceChannel {
  id: string
  name: string
  tag: string
  score: string
  price: string
  originalPrice: string
  offer: string
  shipping: string[]
  arrival: string
  warranty: string
  stars: number
  sales: string
  accent: 'teal' | 'blue' | 'violet'
}

export const priceChannels: PriceChannel[] = [
  { id: 'best-price', name: '优选低价渠道', tag: '当前低价', score: '98%', price: '259.00', originalPrice: '289.00', offer: '满 200 减 30 · 新人券 ¥10', shipping: ['包邮', '48 小时内发货', '7 天无理由'], arrival: '2-3 天', warranty: '2 年质保', stars: 5, sales: '2.3 万+', accent: 'teal' },
  { id: 'self-operated', name: '平台自营渠道', tag: '正品保障', score: '92%', price: '279.00', originalPrice: '299.00', offer: '平台券 ¥20', shipping: ['包邮', '次日达', '7 天无理由'], arrival: '次日达', warranty: '2 年质保', stars: 4, sales: '1.8 万+', accent: 'blue' },
  { id: 'official', name: '官方旗舰渠道', tag: '官方直营', score: '86%', price: '299.00', originalPrice: '299.00', offer: '无优惠', shipping: ['包邮', '48 小时内发货', '7 天无理由'], arrival: '2-3 天', warranty: '2 年质保', stars: 4, sales: '1.2 万+', accent: 'violet' },
]
