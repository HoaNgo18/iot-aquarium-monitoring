export type MetricAccent = 'blue' | 'cyan' | 'slate'

export interface MetricSummary {
  title: string
  value: string
  description: string
  accent: MetricAccent
  unit?: string
}

export interface TelemetryReading {
  id: number
  device_id: string
  sequence: number
  measured_at: string
  received_at: string
  temperature_c: number | null
  ph: number | null
  turbidity_pct: number | null
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

export interface AlertRecord {
  id: number
  device_id: string
  alert_type: string
  severity: string
  message: string
  started_at: string
  ended_at: string | null
  acknowledged_at: string | null
}

export interface Thresholds {
  device_id: string
  temperature_min_c: number
  temperature_max_c: number
  ph_min: number
  ph_max: number
  turbidity_warning_pct: number
  turbidity_critical_pct: number
  updated_at: string
}

export type ThresholdValues = Omit<Thresholds, 'device_id' | 'updated_at'>
