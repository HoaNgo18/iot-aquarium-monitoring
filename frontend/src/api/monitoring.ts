import axios from 'axios'
import type { AlertRecord, Device, TelemetryReading, Thresholds, ThresholdValues } from '../types/monitoring'

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

export async function getAlerts(
  deviceId: string,
  activeOnly: boolean,
  signal: AbortSignal,
): Promise<AlertRecord[]> {
  const response = await client.get<AlertRecord[]>(
    `/devices/${encodeURIComponent(deviceId)}/alerts`,
    { params: { active_only: activeOnly, limit: 50 }, signal },
  )
  return response.data
}

export async function getReadingHistory(
  deviceId: string,
  from: string,
  signal: AbortSignal,
): Promise<TelemetryReading[]> {
  const response = await client.get<TelemetryReading[]>(
    `/devices/${encodeURIComponent(deviceId)}/telemetry`,
    { params: { from, limit: 500 }, signal },
  )
  return response.data
}

export function getThresholds(deviceId: string, signal: AbortSignal): Promise<Thresholds | null> {
  return getOrNull(`/devices/${encodeURIComponent(deviceId)}/thresholds`, signal)
}

export async function saveThresholds(deviceId: string, values: ThresholdValues, signal: AbortSignal): Promise<Thresholds> {
  return (await client.put<Thresholds>(`/devices/${encodeURIComponent(deviceId)}/thresholds`, values, { signal })).data
}

export async function acknowledgeAlert(deviceId: string, alertId: number, signal: AbortSignal): Promise<AlertRecord> {
  return (await client.post<AlertRecord>(`/devices/${encodeURIComponent(deviceId)}/alerts/${alertId}/acknowledge`, null, { signal })).data
}
