<script setup lang="ts">
import { computed, onScopeDispose, ref, watch } from 'vue'
import { getReadingHistory, getThresholds } from '../api/monitoring'
import type { TelemetryReading, Thresholds } from '../types/monitoring'

const props = defineProps<{ deviceId: string }>()
const metric = ref<'temperature_c' | 'ph' | 'turbidity_pct'>('temperature_c')
const hours = ref(1)
const rows = ref<TelemetryReading[]>([])
const thresholds = ref<Thresholds | null>(null)
const loading = ref(true)
const error = ref('')
let controller: AbortController | null = null

async function refresh(background = false) {
  controller?.abort()
  const request = new AbortController()
  controller = request
  const target = props.deviceId
  const period = hours.value
  if (!background) {
    rows.value = []
    thresholds.value = null
    loading.value = true
  }
  error.value = ''
  try {
    const from = new Date(Date.now() - period * 3600000).toISOString()
    const [readings, limits] = await Promise.all([
      getReadingHistory(target, from, request.signal),
      getThresholds(target, request.signal),
    ])
    if (request.signal.aborted || target !== props.deviceId || period !== hours.value) return
    rows.value = [...readings].sort((a, b) =>
      Date.parse(a.measured_at) - Date.parse(b.measured_at) || a.id - b.id)
    thresholds.value = limits
  } catch {
    if (request.signal.aborted || target !== props.deviceId || period !== hours.value) return
    request.abort()
    error.value = 'Không tải được lịch sử hoặc ngưỡng. Biểu đồ có thể chứa dữ liệu từ lần tải trước.'
  } finally {
    if (controller === request) loading.value = false
  }
}

watch(() => [props.deviceId, hours.value], () => void refresh(), { immediate: true })
onScopeDispose(() => controller?.abort())
defineExpose({ refresh })

const label = computed(() => ({
  temperature_c: 'Nhiệt độ nước (°C)', ph: 'pH', turbidity_pct: 'Độ đục tương đối (%)',
})[metric.value])
const limits = computed(() => {
  const t = thresholds.value
  if (!t) return []
  if (metric.value === 'temperature_c') return [t.temperature_min_c, t.temperature_max_c]
  if (metric.value === 'ph') return [t.ph_min, t.ph_max]
  return [t.turbidity_warning_pct, t.turbidity_critical_pct]
})
const values = computed(() => rows.value.map(row => row[metric.value]))
const bounds = computed(() => {
  if (metric.value === 'turbidity_pct') return [0, 100]
  const known = values.value.filter((v): v is number => v !== null)
  const all = [...known, ...limits.value]
  if (!all.length) return [0, 1]
  const padding = metric.value === 'ph' ? 0.2 : 1
  return [Math.min(...all) - padding, Math.max(...all) + padding]
})
const timeBounds = computed(() => {
  const first = rows.value[0]
  const last = rows.value[rows.value.length - 1]
  return first && last ? [Date.parse(first.measured_at), Date.parse(last.measured_at)] : [0, 1]
})
function x(time: string) {
  const [start = 0, end = 1] = timeBounds.value
  return end === start ? 360 : 32 + (Date.parse(time) - start) / (end - start) * 672
}
function y(value: number) {
  const [low = 0, high = 1] = bounds.value
  return 210 - (value - low) / (high - low) * 192
}
const segments = computed(() => {
  const paths: string[] = []
  let current = ''
  for (const row of rows.value) {
    const value = row[metric.value]
    if (value === null) {
      if (current) paths.push(current)
      current = ''
    } else {
      current += `${current ? ' L' : 'M'}${x(row.measured_at)},${y(value)}`
    }
  }
  if (current) paths.push(current)
  return paths
})
const points = computed(() => rows.value.flatMap(row => {
  const value = row[metric.value]
  return value === null ? [] : [{ id: row.id, x: x(row.measured_at), y: y(value), value, time: row.measured_at }]
}))
const number = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const time = new Intl.DateTimeFormat('vi-VN', {
  hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'Asia/Ho_Chi_Minh',
})
function formatTime(value: string) { return time.format(new Date(value)) }
</script>

<template>
  <article class="panel chart-panel" aria-labelledby="history-title" :aria-busy="loading">
    <div class="panel-heading">
      <h2 id="history-title">Lịch sử</h2>
      <label class="sr-only" for="history-metric">Chỉ số biểu đồ</label>
      <select id="history-metric" v-model="metric">
        <option value="temperature_c">Nhiệt độ</option>
        <option value="ph">pH</option>
        <option value="turbidity_pct">Độ đục</option>
      </select>
      <label class="sr-only" for="history-period">Khoảng thời gian</label>
      <select id="history-period" v-model.number="hours">
        <option :value="1">1 giờ</option>
        <option :value="6">6 giờ</option>
        <option :value="24">24 giờ</option>
      </select>
    </div>
    <div class="chart-legend">
      <span>{{ label }}</span>
      <span v-if="thresholds">
        <i class="legend-line threshold-warning" aria-hidden="true"></i>
        {{ metric === 'turbidity_pct' ? 'Cảnh báo / nguy hiểm' : 'Khoảng cấu hình' }}:
        {{ limits.map(value => number.format(value)).join(' / ') }}
      </span>
    </div>
    <p v-if="error" class="history-error" role="alert">
      {{ error }} <button type="button" @click="refresh()">Thử lại</button>
    </p>
    <div class="chart-area">
      <svg v-if="points.length" class="water-chart" viewBox="0 0 720 240" role="img" :aria-label="label">
        <title>{{ label }} theo thời gian; các đoạn bị ngắt khi cảm biến không có số đo</title>
        <path class="chart-grid" d="M32 18H704 M32 114H704 M32 210H704" />
        <text class="chart-text" x="0" y="18">{{ number.format(bounds[1] ?? 1) }}</text>
        <text class="chart-text" x="0" y="224">{{ number.format(bounds[0] ?? 0) }}</text>
        <path v-for="(limit, index) in limits" :key="index"
          class="chart-threshold chart-threshold-warning" :d="`M32 ${y(limit)}H704`" />
        <path v-for="(path, index) in segments" :key="index" class="chart-series" :d="path" />
        <circle v-for="point in points" :key="point.id" :cx="point.x" :cy="point.y" r="2" fill="var(--accent)">
          <title>{{ formatTime(point.time) }}: {{ number.format(point.value) }}</title>
        </circle>
      </svg>
      <p v-else class="chart-empty">
        {{ loading ? 'Đang tải lịch sử…' : error ? 'Lịch sử chưa sẵn sàng' : 'Chưa có số đo hợp lệ trong khoảng đã chọn' }}
      </p>
    </div>
    <div class="history-time-axis" v-if="rows.length">
      <span>{{ formatTime(rows[0]!.measured_at) }}</span>
      <span>{{ formatTime(rows[rows.length - 1]!.measured_at) }} (giờ VN)</span>
    </div>
    <p class="history-note">Ngưỡng mặc định phục vụ demo; cần cấu hình theo loài cá và hiệu chuẩn cảm biến.</p>
    <p v-if="metric === 'turbidity_pct'" class="history-note">0%: trong · 100%: đục. Chỉ số tương đối, không phải NTU.</p>
    <p v-if="rows.length === 500" class="history-note">Hiển thị tối đa 500 mẫu gần nhất; chọn khoảng ngắn hơn để xem chi tiết.</p>
  </article>
</template>
