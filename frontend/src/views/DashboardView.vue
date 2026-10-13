<script setup lang="ts">
import { computed, ref } from 'vue'
import AlertList from '../components/AlertList.vue'
import DeviceStatus from '../components/DeviceStatus.vue'
import MetricCard from '../components/MetricCard.vue'
import WaterLevelChart from '../components/WaterLevelChart.vue'
import { useReadings } from '../composables/useReadings'
import type { MetricSummary } from '../types/monitoring'

const deviceIdPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/
const queryDeviceId = new URLSearchParams(window.location.search).get('device_id')
const deviceId = ref(queryDeviceId && deviceIdPattern.test(queryDeviceId) ? queryDeviceId : 'node-001')
const deviceInput = ref(deviceId.value)
const { device, latest, state, errorMessage, refresh } = useReadings(deviceId)
const numberFormatter = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 2 })
const timeFormatter = new Intl.DateTimeFormat('vi-VN', {
  dateStyle: 'short',
  timeStyle: 'medium',
  timeZone: 'Asia/Ho_Chi_Minh',
})
const measuredAt = computed(() => latest.value ? timeFormatter.format(new Date(latest.value.measured_at)) : '')
const stateLabel = computed(() => ({
  loading: 'Đang tải dữ liệu',
  ready: 'Đã tải dữ liệu',
  empty: 'Chưa có số đo',
  error: 'Không tải được dữ liệu',
})[state.value])

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
  {
    title: 'Mực nước',
    value: state.value === 'loading' ? 'Đang tải…' : latest.value?.water_level_cm != null
      ? `${numberFormatter.format(latest.value.water_level_cm)} cm`
      : '-- cm',
    description: latest.value?.sensor_status === 'error'
      ? 'Cảm biến lỗi · Mẫu này không có giá trị mực nước hợp lệ'
      : latest.value ? 'Số đo gần nhất từ thiết bị' : 'Chưa có số đo mực nước',
    accent: 'blue',
  },
  {
    title: 'Lượng mưa',
    value: state.value === 'loading' ? 'Đang tải…' : latest.value
      ? `${numberFormatter.format(latest.value.rainfall_mm)} mm`
      : '-- mm',
    description: 'Lượng mưa trong chu kỳ gần nhất',
    accent: 'cyan',
  },
])
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <h1>IoT Flood Monitoring</h1>
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
        <button type="button" :disabled="state === 'loading'" @click="refresh">Cập nhật</button>
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
            {{ Math.max(0, Date.now() - new Date(latest.measured_at).getTime()) < 60000
              ? 'vừa xong'
              : Math.max(0, Date.now() - new Date(latest.measured_at).getTime()) < 3600000
                ? `${Math.floor((Date.now() - new Date(latest.measured_at).getTime()) / 60000)} phút trước`
                : Math.max(0, Date.now() - new Date(latest.measured_at).getTime()) < 86400000
                  ? `${Math.floor((Date.now() - new Date(latest.measured_at).getTime()) / 3600000)} giờ trước`
                  : `${Math.floor((Date.now() - new Date(latest.measured_at).getTime()) / 86400000)} ngày trước` }}
          </time>
        </span>
        <span v-else>{{ state === 'loading' ? 'Đang tải…' : 'Chưa có mẫu' }}</span>
        <span class="sensor-state" v-if="latest?.sensor_status === 'error'">Cảm biến lỗi</span>
      </section>

      <div v-if="state === 'error'" class="data-notice data-notice-error" role="alert">
        {{ errorMessage }}
      </div>
      <div v-else-if="state === 'empty'" class="data-notice" role="status">
        {{ device ? 'Chưa có dữ liệu' : `Không tìm thấy thiết bị ${deviceId}` }}
      </div>
      <div v-else-if="state === 'ready' && device?.connectivity === 'offline'" class="data-notice" role="status">
        Thiết bị offline · Số liệu từ mẫu gần nhất
      </div>

      <section
        class="metrics"
        :class="{ 'metrics-stale': device?.connectivity === 'offline' }"
        aria-label="Các chỉ số hiện tại"
        :aria-busy="state === 'loading'"
      >
        <MetricCard v-for="metric in metrics" :key="metric.title" :metric="metric" />
        <DeviceStatus :device="device" :reading="latest" :state="state" />
      </section>

      <section class="workspace-grid">
        <WaterLevelChart />
        <AlertList />
      </section>
    </main>

  </div>
</template>
