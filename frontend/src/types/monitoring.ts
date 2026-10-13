export type MetricAccent = 'blue' | 'cyan' | 'slate'

export interface MetricSummary {
  title: string
  value: string
  description: string
  accent: MetricAccent
}

export interface TelemetryReading {
  id: number
  device_id: string
  sequence: number
  measured_at: string
  received_at: string
  water_level_cm: number | null
  rainfall_mm: number
  signal_strength_dbm: number
  sensor_status: 'normal' | 'error'
}

export interface Device {
  id: string
  connectivity: 'online' | 'offline' | 'unknown'
  sensor_status: 'normal' | 'error' | 'unknown'
  last_seen_at: string | null
  created_at: string
  updated_at: string
}

export type ReadingState = 'loading' | 'ready' | 'empty' | 'error'
