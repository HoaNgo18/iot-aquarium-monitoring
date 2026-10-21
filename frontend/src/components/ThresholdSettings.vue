<script setup lang="ts">
import { computed, onScopeDispose, reactive, ref, watch } from 'vue'
import { getThresholds, saveThresholds } from '../api/monitoring'
import { parseThresholds, thresholdFields, type ThresholdDraft } from '../domain/monitoring'
import type { Thresholds } from '../types/monitoring'

const props = defineProps<{ deviceId: string }>()
const emit = defineEmits<{ saved: [deviceId: string] }>()
const draft = reactive(Object.fromEntries(thresholdFields.map(field => [field, ''])) as ThresholdDraft)
const loading = ref(true)
const saving = ref(false)
const exists = ref(false)
const error = ref('')
const message = ref('')
const savedSnapshot = ref('')
let request: AbortController | null = null
const dirty = computed(() => JSON.stringify(draft) !== savedSnapshot.value)
const groups = [
  { title: 'Nhiệt độ nước (°C)', fields: [{ key: 'temperature_min_c', label: 'Nhiệt độ tối thiểu', min: -55, max: 125 }, { key: 'temperature_max_c', label: 'Nhiệt độ tối đa', min: -55, max: 125 }] },
  { title: 'pH', fields: [{ key: 'ph_min', label: 'pH tối thiểu', min: 0, max: 14 }, { key: 'ph_max', label: 'pH tối đa', min: 0, max: 14 }] },
  { title: 'Độ đục tương đối (%)', fields: [{ key: 'turbidity_warning_pct', label: 'Độ đục cảnh báo', min: 0, max: 100 }, { key: 'turbidity_critical_pct', label: 'Độ đục nguy hiểm', min: 0, max: 100 }] },
] as const

function apply(values: Thresholds) {
  for (const field of thresholdFields) draft[field] = String(values[field])
  savedSnapshot.value = JSON.stringify(draft)
}

async function load() {
  request?.abort()
  const current = new AbortController()
  request = current
  const device = props.deviceId
  loading.value = true
  saving.value = false
  exists.value = false
  error.value = message.value = ''
  for (const field of thresholdFields) draft[field] = ''
  try {
    const result = await getThresholds(device, current.signal)
    if (current.signal.aborted || device !== props.deviceId) return
    exists.value = result !== null
    if (result) apply(result)
    else error.value = 'Chưa tìm thấy thiết bị. Ngưỡng có thể cấu hình sau khi thiết bị gửi dữ liệu.'
  } catch {
    if (!current.signal.aborted) error.value = 'Không tải được ngưỡng. Hãy thử tải lại.'
  } finally {
    if (request === current) loading.value = false
  }
}

async function save() {
  if (saving.value || loading.value || !exists.value) return
  error.value = message.value = ''
  const parsed = parseThresholds(draft)
  if (!parsed.values) { error.value = parsed.error; return }
  request?.abort()
  const current = new AbortController()
  request = current
  const device = props.deviceId
  saving.value = true
  try {
    const result = await saveThresholds(device, parsed.values, current.signal)
    if (current.signal.aborted || device !== props.deviceId) return
    apply(result)
    message.value = 'Đã lưu ngưỡng. Cảnh báo được đánh giá từ mẫu đo tiếp theo.'
    emit('saved', device)
  } catch {
    if (!current.signal.aborted && device === props.deviceId) error.value = 'Không xác nhận được kết quả lưu. Tải lại ngưỡng để kiểm tra trước khi thử lại.'
  } finally {
    if (request === current) saving.value = false
  }
}

watch(() => props.deviceId, () => void load(), { immediate: true })
onScopeDispose(() => request?.abort())
</script>

<template>
  <section class="panel threshold-panel" aria-labelledby="thresholds-title">
    <div class="panel-heading">
      <h2 id="thresholds-title">Cấu hình ngưỡng</h2>
      <button type="button" :disabled="loading || saving" @click="load">Tải lại ngưỡng</button>
    </div>
    <form class="threshold-form" novalidate @submit.prevent="save">
      <p class="settings-note">Ngưỡng áp dụng riêng cho {{ deviceId }}. Chọn theo loài cá và kết quả hiệu chuẩn; độ đục không phải NTU.</p>
      <p v-if="loading" role="status">Đang tải ngưỡng…</p>
      <fieldset :disabled="loading || saving || !exists" class="threshold-grid">
        <div v-for="group in groups" :key="group.title" class="threshold-group">
          <h3>{{ group.title }}</h3>
          <label v-for="field in group.fields" :key="field.key" :for="field.key">
            {{ field.label }}
            <input :id="field.key" :value="draft[field.key]" @input="draft[field.key] = ($event.target as HTMLInputElement).value" type="number" step="any" :min="field.min" :max="field.max" required />
          </label>
        </div>
      </fieldset>
      <p v-if="error" class="settings-error" role="alert">{{ error }}</p>
      <p v-if="message" class="settings-success" role="status">{{ message }}</p>
      <div class="settings-actions">
        <button type="submit" :disabled="loading || saving || !exists || !dirty">{{ saving ? 'Đang lưu…' : 'Lưu ngưỡng' }}</button>
        <span v-if="exists && dirty && !loading" class="settings-note">Có thay đổi chưa lưu</span>
      </div>
    </form>
  </section>
</template>
