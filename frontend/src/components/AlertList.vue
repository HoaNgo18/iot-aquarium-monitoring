<script setup lang="ts">
import { onScopeDispose, ref, watch } from 'vue'
import { acknowledgeAlert } from '../api/monitoring'
import type { AlertRecord, ReadingState } from '../types/monitoring'

const props = defineProps<{
  deviceId: string
  alerts: AlertRecord[]
  state: ReadingState
  errorMessage: string
  activeOnly: boolean
}>()

const emit = defineEmits<{
  'update:activeOnly': [value: boolean]
  retry: []
  acknowledged: [deviceId: string]
}>()

const acknowledging = ref<number | null>(null)
const acknowledgementError = ref('')
let acknowledgementRequest: AbortController | null = null
watch(() => props.deviceId, () => {
  acknowledgementRequest?.abort()
  acknowledgementRequest = null
  acknowledging.value = null
  acknowledgementError.value = ''
})
onScopeDispose(() => acknowledgementRequest?.abort())

async function acknowledge(id: number) {
  if (acknowledging.value !== null) return
  const device = props.deviceId
  const request = new AbortController()
  acknowledgementRequest = request
  acknowledging.value = id
  acknowledgementError.value = ''
  try {
    await acknowledgeAlert(device, id, request.signal)
    if (!request.signal.aborted && device === props.deviceId) emit('acknowledged', device)
  } catch {
    if (!request.signal.aborted && device === props.deviceId) acknowledgementError.value = 'Không xác nhận được cảnh báo. Tải lại danh sách để kiểm tra trước khi thử lại.'
  } finally {
    if (acknowledgementRequest === request) acknowledging.value = null
  }
}

const clockFormatter = new Intl.DateTimeFormat('vi-VN', {
  hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'Asia/Ho_Chi_Minh',
})
const fullTimeFormatter = new Intl.DateTimeFormat('vi-VN', {
  dateStyle: 'short', timeStyle: 'medium', timeZone: 'Asia/Ho_Chi_Minh',
})
const severityLabels: Record<string, string> = { warning: 'Cảnh báo', critical: 'Nguy hiểm' }

function fullTime(value: string) {
  return `${fullTimeFormatter.format(new Date(value))} (giờ Việt Nam)`
}
</script>

<template>
  <article class="panel alerts-panel" aria-labelledby="alerts-title">
    <div class="panel-heading">
      <h2 id="alerts-title">Cảnh báo</h2>
      <span v-if="state === 'ready'" class="alert-count">{{ alerts.length }}</span>
    </div>
    <div class="alert-filters" role="group" aria-label="Lọc cảnh báo">
      <button type="button" :aria-pressed="activeOnly" @click="emit('update:activeOnly', true)">Đang xảy ra</button>
      <button type="button" :aria-pressed="!activeOnly" @click="emit('update:activeOnly', false)">Gần đây</button>
    </div>
    <div class="alert-results" :aria-busy="state === 'loading'">
      <p v-if="acknowledgementError" class="settings-error acknowledgement-error" role="alert">{{ acknowledgementError }}</p>
      <p v-if="state === 'loading'" class="empty-state" role="status">Đang tải…</p>
      <div v-else-if="state === 'error'" class="alert-error" role="alert">
        <p>{{ errorMessage }}</p>
        <button type="button" @click="emit('retry')">Thử lại</button>
      </div>
      <p v-else-if="state === 'empty'" class="empty-state" role="status">{{ activeOnly ? 'Không có cảnh báo đang xảy ra' : 'Chưa có cảnh báo' }}</p>
      <ul v-else class="alert-list" aria-label="Danh sách cảnh báo">
        <li v-for="alert in alerts" :key="alert.id" class="alert-row" :class="{ 'alert-resolved': alert.ended_at !== null }">
          <time class="alert-time" :datetime="alert.started_at" :title="fullTime(alert.started_at)">{{ clockFormatter.format(new Date(alert.started_at)) }}</time>
          <span class="alert-severity" :class="{ 'alert-warning': alert.severity === 'warning', 'alert-critical': alert.severity === 'critical' }">{{ severityLabels[alert.severity] ?? alert.severity }}</span>
          <div class="alert-content">
            <p>{{ alert.message }}</p>
            <p class="alert-lifecycle">
              <span v-if="alert.ended_at" :title="`Kết thúc: ${fullTime(alert.ended_at)}`">Đã kết thúc</span>
              <span v-else>Đang xảy ra</span>
              <span v-if="alert.acknowledged_at" :title="`Xác nhận: ${fullTime(alert.acknowledged_at)}`"> · Đã xác nhận</span>
            </p>
            <button v-if="!alert.acknowledged_at" class="acknowledge-button" type="button"
              :aria-label="`Xác nhận cảnh báo #${alert.id}`" :disabled="acknowledging !== null"
              @click="acknowledge(alert.id)">{{ acknowledging === alert.id ? 'Đang xác nhận…' : 'Xác nhận' }}</button>
          </div>
        </li>
      </ul>
    </div>
    <p v-if="state === 'ready' && alerts.length === 50" class="alert-limit">Hiển thị 50 cảnh báo mới nhất</p>
  </article>
</template>
