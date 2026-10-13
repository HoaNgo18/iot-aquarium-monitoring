import axios from 'axios'
import type { Device, TelemetryReading } from '../types/monitoring'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

async function getOrNull<T>(path: string, signal: AbortSignal): Promise<T | null> {
  try {
    const response = await client.get<T>(path, { signal })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) return null
    throw error
  }
}

export function getDevice(deviceId: string, signal: AbortSignal): Promise<Device | null> {
  return getOrNull(`/devices/${encodeURIComponent(deviceId)}`, signal)
}

export function getLatestReading(
  deviceId: string,
  signal: AbortSignal,
): Promise<TelemetryReading | null> {
  return getOrNull(`/devices/${encodeURIComponent(deviceId)}/telemetry/latest`, signal)
}

export function describeApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') return 'Máy chủ phản hồi quá chậm. Vui lòng thử lại.'
    if (!error.response) return 'Không kết nối được máy chủ. Vui lòng kiểm tra kết nối và thử lại.'
  }
  return 'Không tải được dữ liệu thiết bị. Vui lòng thử lại.'
}
