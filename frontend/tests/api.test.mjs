import test from 'node:test';
import assert from 'node:assert/strict';
import { decodeReading, decodeThresholds, encodeThresholds, metricStatus } from '../src/dashboard/api.js';
const wire = { temperature_min_c: 22, temperature_max_c: 30, ph_min: 6.5, ph_max: 8.5, turbidity_warning_pct: 60, turbidity_critical_pct: 80 };
const thresholds = decodeThresholds(wire);
test('threshold payload round-trips without invented fields', () => assert.deepEqual(encodeThresholds(thresholds), wire));
test('backend boundaries and severity rules', () => {
  for (const [metric,value,status] of [['temperature',22,'normal'],['temperature',30,'normal'],['temperature',40,'warning'],['ph',6.4,'warning'],['ph',8.5,'normal'],['turbidity',59.9,'normal'],['turbidity',60,'warning'],['turbidity',80,'danger']]) assert.equal(metricStatus(metric,value,thresholds),status);
});
test('null remains unknown, never zero or normal', () => {
  const reading = decodeReading({ id: 1, measured_at: '2026-10-22T10:00:00Z', temperature_c: null, ph: 7, turbidity_pct: null, signal_strength_dbm: -60 });
  assert.equal(reading.temperature,null); assert.equal(reading.turbidity,null);
  assert.equal(reading.time.toISOString(),'2026-10-22T10:00:00.000Z');
  assert.equal(metricStatus('ph',null,thresholds),'neutral');
  assert.equal(metricStatus('ph',7,null),'neutral');
});
