<script setup lang="ts">
import { computed, ref } from 'vue'
import AlertList from '../components/AlertList.vue'
import DeviceStatus from '../components/DeviceStatus.vue'
import MetricCard from '../components/MetricCard.vue'
import WaterQualityHistory from '../components/WaterQualityHistory.vue'
import ThresholdSettings from '../components/ThresholdSettings.vue'
import { useSampleAge } from '../composables/useSampleAge'
import { useReadings } from '../composables/useReadings'
import { useAlerts } from '../composables/useAlerts'
import { useRealtime } from '../composables/useRealtime'
import type { MetricSummary } from '../types/monitoring'

const deviceIdPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/
const queryDeviceId = new URLSearchParams(window.location.search).get('device_id')
const deviceId = ref(queryDeviceId && deviceIdPattern.test(queryDeviceId) ? queryDeviceId : 'tank-001')
const deviceInput = ref(deviceId.value)
const { device, latest, state, errorMessage, refresh: refreshReadings } = useReadings(deviceId)
const freshness = useSampleAge(latest)
const activeOnly = ref(true)
const { alerts, state: alertState, errorMessage: alertError, refresh: refreshAlerts } = useAlerts(deviceId, activeOnly)
const history = ref<InstanceType<typeof WaterQualityHistory> | null>(null)
const { state: realtimeState } = useRealtime(deviceId, async () => {
  await Promise.all([refreshReadings(true), refreshAlerts(true), history.value?.refresh(true)])
})

async function refresh() {
  await Promise.all([refreshReadings(), refreshAlerts(), history.value?.refresh()])
}
function refreshAcknowledgement(target: string) {
  if (target === deviceId.value) void refreshAlerts(true)
}
function thresholdsSaved(target: string) {
  if (target === deviceId.value) void history.value?.refresh(true)
}
const numberFormatter = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const timeFormatter = new Intl.DateTimeFormat('vi-VN', {
  dateStyle: 'short',
  timeStyle: 'medium',
  timeZone: 'Asia/Ho_Chi_Minh',
})
const measuredAt = computed(() => latest.value ? timeFormatter.format(new Date(latest.value.measured_at)) : '')

function selectDevice() {
  const value = deviceInput.value.trim()
  if (!deviceIdPattern.test(value)) return
  if (value === deviceId.value) {
    void refresh()
    return
  }
  deviceId.value = value
  const url = new URL(window.location.href)
  url.searchParams.set('device_id', value)
  window.history.replaceState(null, '', url)
}

const metrics = computed<MetricSummary[]>(() => [
  { title: 'Nhiệt độ nước', field: 'temperature_c' as const, unit: '°C', accent: 'blue' as const },
  { title: 'pH', field: 'ph' as const, unit: '', accent: 'cyan' as const },
  { title: 'Độ đục tương đối', field: 'turbidity_pct' as const, unit: '%', accent: 'slate' as const },
].map(({ title, field, unit, accent }) => {
  const value = latest.value?.[field]
  return {
    title,
    value: state.value === 'loading' ? 'Đang tải…' : value != null
      ? numberFormatter.format(value) : '--',
    unit,
    description: latest.value && value == null ? 'Cảm biến lỗi · Không có số đo hợp lệ'
      : field === 'turbidity_pct' ? '0%: trong · 100%: đục · Không phải NTU'
      : latest.value ? 'Số đo gần nhất từ thiết bị' : 'Chưa có số đo',
    accent,
  }
}))
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <h1>Giám sát bể nuôi cá</h1>
      <div class="topbar-controls">
        <form class="device-selector" @submit.prevent="selectDevice">
          <label for="device-id" class="sr-only">Mã thiết bị</label>
          <input
            id="device-id"
            v-model="deviceInput"
            name="device-id"
            required
            maxlength="64"
            pattern="[A-Za-z0-9][A-Za-z0-9_\-]{0,63}"
            title="Từ 1 đến 64 ký tự: chữ, số, gạch dưới hoặc gạch ngang; bắt đầu bằng chữ hoặc số."
            autocomplete="off"
            spellcheck="false"
          />
          <button type="submit" class="device-select-button">Chọn</button>
        </form>
        <button type="button" :disabled="state === 'loading' || alertState === 'loading'" @click="refresh">Cập nhật</button>
        <div class="connection-state" role="status">
          <span
            class="state-dot"
            :class="{
              'state-dot-online': device?.connectivity === 'online',
              'state-dot-offline': device?.connectivity === 'offline',
            }"
            aria-hidden="true"
          ></span>
          <span>{{ device?.connectivity === 'online' ? 'Online' : device?.connectivity === 'offline' ? 'Offline' : 'Chưa rõ' }}</span>
        </div>
      </div>
    </header>

    <main>
      <section class="status-strip" aria-label="Thông tin mẫu đo">
        <span class="device-code">{{ deviceId }}</span>
        <span class="status-divider" aria-hidden="true"></span>
        <span class="sample-time" v-if="latest">
          Lấy mẫu
          <time :datetime="latest.measured_at" :title="`${measuredAt} (giờ Việt Nam)`">
            {{ freshness.label }}
          </time>
        </span>
        <span v-else>{{ state === 'loading' ? 'Đang tải…' : 'Chưa có mẫu' }}</span>
        <span class="sensor-state" v-if="latest?.sensor_status === 'error'">Cảm biến lỗi</span>
        <span class="realtime-state" :class="{ 'realtime-live': realtimeState === 'connected' }" role="status">
          {{ realtimeState === 'connected' ? 'Live' : realtimeState === 'connecting' ? 'Đang kết nối' : realtimeState === 'reconnecting' ? 'Đang kết nối lại' : 'Mất kết nối' }}
        </span>
      </section>

      <div v-if="realtimeState === 'reconnecting' || realtimeState === 'offline'" class="data-notice" role="status">
        Mất kết nối cập nhật trực tiếp · Số liệu từ lần tải gần nhất
      </div>

      <div v-if="state === 'error'" class="data-notice data-notice-error" role="alert">
        {{ errorMessage }}
      </div>
      <div v-else-if="state === 'empty'" class="data-notice" role="status">
        {{ device ? 'Chưa có dữ liệu' : `Không tìm thấy thiết bị ${deviceId}` }}
      </div>
      <div v-else-if="state === 'ready' && device?.connectivity === 'offline'" class="data-notice" role="status">
        Thiết bị offline · Số liệu từ mẫu gần nhất
      </div>

      <div v-if="latest && freshness.stale" class="data-notice" role="status">
        Dữ liệu cũ · Mẫu gần nhất: {{ freshness.label }}. Chưa có mẫu mới trong ít nhất 60 giây; kiểm tra thiết bị và kết nối.
      </div>
      <div v-if="latest && freshness.clockSkew" class="data-notice data-notice-error" role="status">
        Giờ mẫu đo ở tương lai so với máy đang xem. Kiểm tra đồng bộ thời gian trước khi sử dụng số đo.
      </div>

      <section
        class="metrics"
        :class="{ 'metrics-stale': device?.connectivity === 'offline' || realtimeState !== 'connected' || freshness.stale || freshness.clockSkew }"
        aria-label="Các chỉ số hiện tại"
        :aria-busy="state === 'loading'"
      >
        <MetricCard v-for="metric in metrics" :key="metric.title" :metric="metric" />
        <DeviceStatus :device="device" :reading="latest" :state="state" />
      </section>

      <section class="workspace-grid">
        <WaterQualityHistory ref="history" :device-id="deviceId" />
        <AlertList
          :device-id="deviceId"
          v-model:active-only="activeOnly"
          :alerts="alerts"
          :state="alertState"
          :error-message="alertError"
          @retry="refreshAlerts"
          @acknowledged="refreshAcknowledgement"
        />
      </section>
      <ThresholdSettings :device-id="deviceId" @saved="thresholdsSaved" />
    </main>

  </div>
</template>
