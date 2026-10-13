<script setup lang="ts">
import { computed } from 'vue'
import MetricCard from './MetricCard.vue'
import type { Device, MetricSummary, ReadingState, TelemetryReading } from '../types/monitoring'

const props = defineProps<{
  device: Device | null
  reading: TelemetryReading | null
  state: ReadingState
}>()

const metric = computed<MetricSummary>(() => ({
  title: 'Trạng thái thiết bị',
  value: props.state === 'loading'
    ? 'Đang tải…'
    : props.device?.connectivity === 'online'
      ? 'Đang kết nối'
      : props.device?.connectivity === 'offline'
        ? 'Mất kết nối'
        : 'Chưa xác định',
  description: props.device
    ? `${props.device.sensor_status === 'error' ? 'Cảm biến lỗi' : props.device.sensor_status === 'normal' ? 'Cảm biến bình thường' : 'Chưa rõ trạng thái cảm biến'}${props.reading ? ` · RSSI mẫu gần nhất: ${props.reading.signal_strength_dbm} dBm` : ''}`
    : 'Chưa nhận được trạng thái thiết bị',
  accent: 'slate',
}))
</script>

<template>
  <article class="metric-card device-metric">
    <p class="metric-title">Thiết bị</p>
    <p class="metric-value metric-device-value" :title="metric.description">
      {{ props.device?.sensor_status === 'error' ? 'Lỗi cảm biến' : metric.value === 'Đang kết nối' ? 'Online' : metric.value === 'Mất kết nối' ? 'Offline' : metric.value }}
    </p>
    <p class="metric-description">
      <template v-if="props.reading">RSSI {{ props.reading.signal_strength_dbm }} dBm</template>
      <template v-else>Chưa có dữ liệu</template>
    </p>
  </article>
</template>
