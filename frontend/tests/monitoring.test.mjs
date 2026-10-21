import test from 'node:test'
import assert from 'node:assert/strict'
import { parseThresholds, sampleFreshness } from '../src/domain/monitoring.ts'

const draft = () => ({ temperature_min_c: '22', temperature_max_c: '30', ph_min: '6.5', ph_max: '8.5', turbidity_warning_pct: '60', turbidity_critical_pct: '80' })
const now = Date.parse('2026-10-21T10:00:00Z')
const at = seconds => new Date(now - seconds * 1000).toISOString()

test('all six thresholds round-trip without dropping fields', () => {
  assert.deepEqual(parseThresholds(draft()).values, { temperature_min_c: 22, temperature_max_c: 30, ph_min: 6.5, ph_max: 8.5, turbidity_warning_pct: 60, turbidity_critical_pct: 80 })
})
test('blank and non-finite thresholds cannot silently become zero', () => {
  for (const bad of ['', ' ', 'Infinity', 'NaN', 'abc']) assert.equal(parseThresholds({ ...draft(), ph_min: bad }).values, null)
})
test('reversed/equal pairs and out-of-domain values are rejected', () => {
  for (const change of [{ ph_min: '8.5' }, { ph_max: '15' }, { temperature_min_c: '31' }, { temperature_min_c: '-56' }, { turbidity_warning_pct: '80' }, { turbidity_critical_pct: '101' }]) assert.equal(parseThresholds({ ...draft(), ...change }).values, null)
})
test('fractional values and technical boundaries are supported', () => {
  assert.equal(parseThresholds({ ...draft(), ph_min: '0', ph_max: '14', temperature_min_c: '-55', temperature_max_c: '125', turbidity_warning_pct: '0', turbidity_critical_pct: '100' }).error, '')
})
test('missing/invalid timestamps do not invent a sample age', () => {
  for (const value of [null, 'not-a-date']) assert.equal(sampleFreshness(value, now).ageSeconds, null)
})
test('staleness changes at 60 seconds without receiving a new sample', () => {
  assert.equal(sampleFreshness(at(59), now).stale, false)
  assert.equal(sampleFreshness(at(60), now).stale, true)
  assert.equal(sampleFreshness(at(59), now + 1000).stale, true)
})
test('a fresh sample clears stale state and long gaps show elapsed days', () => {
  assert.equal(sampleFreshness(at(86401), now).label, '1 ngày trước')
  assert.equal(sampleFreshness(at(0), now).stale, false)
})
test('future clock skew is explicit, small jitter is tolerated', () => {
  assert.equal(sampleFreshness(at(-30), now).clockSkew, false)
  assert.equal(sampleFreshness(at(-31), now).clockSkew, true)
  assert.equal(sampleFreshness(at(-31), now).label, 'Giờ mẫu ở tương lai')
})
