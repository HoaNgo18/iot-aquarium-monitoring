import { onScopeDispose, ref, watch, type Ref } from 'vue'
import { describeApiError, getAlerts } from '../api/monitoring'
import type { AlertRecord, ReadingState } from '../types/monitoring'

export function useAlerts(deviceId: Ref<string>, activeOnly: Ref<boolean>) {
  const alerts = ref<AlertRecord[]>([])
  const state = ref<ReadingState>('loading')
  const errorMessage = ref('')
  let controller: AbortController | null = null

  async function refresh(background = false) {
    controller?.abort()
    const request = new AbortController()
    controller = request
    const targetDevice = deviceId.value
    const targetFilter = activeOnly.value
    if (!background) alerts.value = []
    if (!background || state.value !== 'ready') state.value = 'loading'
    errorMessage.value = ''
    try {
      const result = await getAlerts(targetDevice, targetFilter, request.signal)
      if (request.signal.aborted || targetDevice !== deviceId.value || targetFilter !== activeOnly.value) return
      alerts.value = result
      state.value = result.length ? 'ready' : 'empty'
    } catch (error) {
      if (request.signal.aborted || targetDevice !== deviceId.value || targetFilter !== activeOnly.value) return
      errorMessage.value = describeApiError(error).replace('dữ liệu thiết bị', 'cảnh báo')
      state.value = 'error'
    }
  }

  watch([deviceId, activeOnly], () => void refresh(), { immediate: true })
  onScopeDispose(() => controller?.abort())

  return { alerts, state, errorMessage, refresh }
}
