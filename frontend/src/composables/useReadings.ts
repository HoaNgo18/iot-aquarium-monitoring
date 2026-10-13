import { onScopeDispose, ref, watch, type Ref } from 'vue'
import { describeApiError, getDevice, getLatestReading } from '../api/monitoring'
import type { Device, ReadingState, TelemetryReading } from '../types/monitoring'

export function useReadings(deviceId: Ref<string>) {
  const device = ref<Device | null>(null)
  const latest = ref<TelemetryReading | null>(null)
  const state = ref<ReadingState>('loading')
  const errorMessage = ref('')
  let controller: AbortController | null = null

  async function refresh() {
    controller?.abort()
    const request = new AbortController()
    controller = request
    state.value = 'loading'
    device.value = null
    latest.value = null
    errorMessage.value = ''
    try {
      const [deviceResult, readingResult] = await Promise.all([
        getDevice(deviceId.value, request.signal),
        getLatestReading(deviceId.value, request.signal),
      ])
      if (request.signal.aborted) return
      device.value = deviceResult
      latest.value = readingResult
      state.value = readingResult ? 'ready' : 'empty'
    } catch (error) {
      if (request.signal.aborted) return
      request.abort()
      errorMessage.value = describeApiError(error)
      state.value = 'error'
    }
  }

  watch(deviceId, refresh, { immediate: true })
  onScopeDispose(() => controller?.abort())

  return { device, latest, state, errorMessage, refresh }
}
