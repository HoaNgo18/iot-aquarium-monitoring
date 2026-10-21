import { computed, onScopeDispose, ref, type Ref } from 'vue'
import { sampleFreshness } from '../domain/monitoring'
import type { TelemetryReading } from '../types/monitoring'

export function useSampleAge(reading: Ref<TelemetryReading | null>) {
  const now = ref(Date.now())
  const timer = window.setInterval(() => { now.value = Date.now() }, 1000)
  onScopeDispose(() => window.clearInterval(timer))
  return computed(() => sampleFreshness(reading.value?.measured_at ?? null, now.value))
}
