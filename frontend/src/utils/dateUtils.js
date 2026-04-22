/**
 * 将 UTC 时间字符串转换为本地时区的格式化字符串
 * @param {string} utcTimeString - UTC 时间字符串（ISO 8601 格式）
 * @param {string} locale - 地区代码，默认 'zh-CN'
 * @returns {string} 格式化后的本地时间字符串
 */
export function formatLocalTime(utcTimeString, locale = 'zh-CN') {
  if (!utcTimeString) return '-'

  // 确保时间字符串以 'Z' 结尾（表示 UTC）
  const timeStr = utcTimeString.endsWith('Z') ? utcTimeString : `${utcTimeString}Z`

  const date = new Date(timeStr)

  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return utcTimeString
  }

  return date.toLocaleString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

/**
 * 将 UTC 时间字符串转换为相对时间（如：3分钟前）
 * @param {string} utcTimeString - UTC 时间字符串
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(utcTimeString) {
  if (!utcTimeString) return '-'

  const timeStr = utcTimeString.endsWith('Z') ? utcTimeString : `${utcTimeString}Z`
  const date = new Date(timeStr)

  if (isNaN(date.getTime())) {
    return utcTimeString
  }

  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  if (diffDay < 7) return `${diffDay}天前`

  return formatLocalTime(utcTimeString)
}
