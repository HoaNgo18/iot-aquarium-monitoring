import { snapshot, request as apiRequest, encodeThresholds, decodeThresholds, metricStatus } from './api.js';

export function mountDashboard(root, onDeviceChange, realtimeLabel) {
const lifetime = new AbortController();
const request = (id, suffix, options = {}) => apiRequest(id, suffix, { ...options, signal: lifetime.signal });
const listeners = [];
const listen = (target, type, handler) => { target.addEventListener(type, handler); listeners.push(() => target.removeEventListener(type, handler)); };
const METRICS = {
  temperature: { label: 'Nhiệt độ', unit: '°C', color: '#4fa8ff', decimals: 1 },
  ph: { label: 'Độ pH', unit: '', color: '#b488ff', decimals: 1 },
  turbidity: { label: 'Độ đục', unit: '%', color: '#f0b85c', decimals: 0 },
};

const DEFAULT_THRESHOLDS = {
  tempMin: 22,
  tempMax: 30,
  phMin: 6.5,
  phMax: 8.5,
  turbidityWarn: 45,
  turbidityDanger: 70,
};

const state = {
  deviceId: 'tank-demo-001',
  metric: 'temperature',
  range: 60,
  thresholdsByDevice: {},
  draft: {},
  dirty: false,
  data: [],
  lastUpdatedAt: new Date(),
  alertTab: 'active',
  loading: false,
  device: null, latest: null, alerts: [], error: '', saving: false,
};
const profileForDevice = () => ({ online: !state.error && state.device?.connectivity === 'online', rssi: !state.error && state.device?.connectivity === 'online' ? state.latest?.rssi : null, name: state.deviceId });
const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
function age(timestamp) {
  if (!timestamp) return 'Chưa có dữ liệu';
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < -30) return 'Giờ mẫu ở tương lai';
  return seconds < 60 ? `${Math.max(0, seconds)} giây trước` : seconds < 3600 ? `${Math.floor(seconds / 60)} phút trước` : `${Math.floor(seconds / 3600)} giờ trước`;
}

const dashboardRoot = root;
const $ = (selector, root = dashboardRoot) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const vnTime = (date, withSeconds = false) => new Intl.DateTimeFormat('vi-VN', {
  timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', ...(withSeconds ? { second: '2-digit' } : {}), hour12: false,
}).format(date);

function getThresholds() {
  return state.thresholdsByDevice[state.deviceId] || { ...DEFAULT_THRESHOLDS };
}

function getMetricThreshold(metric, thresholds = getThresholds()) {
  if (metric === 'temperature') return { min: thresholds.tempMin, max: thresholds.tempMax, warningOnly: false };
  if (metric === 'ph') return { min: thresholds.phMin, max: thresholds.phMax, warningOnly: false };
  return { min: 0, max: thresholds.turbidityWarn, danger: thresholds.turbidityDanger, warningOnly: true };
}

function evaluateMetric(metric, value) {
  return metricStatus(metric, value, state.thresholdsByDevice[state.deviceId]);
}

function statusLabel(status) {
  return {
    normal: '✓ Bình thường', warning: '△ Cảnh báo', danger: '! Nguy hiểm', neutral: '— Chưa có dữ liệu',
  }[status];
}

function currentData() {
  return state.data.filter(row => row.time >= Date.now() - state.range * 60000).slice(-500);
}

function updateHeader() {
  const profile = profileForDevice();
  $('#device-id').textContent = state.deviceId;
  const stale = state.latest && Date.now() - state.latest.time >= 60000;
  $('#sample-time').textContent = `${age(state.latest?.time)}${stale ? ' · Dữ liệu cũ' : ''}`;
  const pill = $('#connection-pill');
  pill.classList.toggle('is-offline', !profile.online);
  pill.innerHTML = `<span class="status-dot ${profile.online ? 'status-dot--live' : ''}" aria-hidden="true"></span><span><strong>${state.error ? 'Lỗi kết nối API' : profile.online ? 'Online' : state.device?.connectivity === 'offline' ? 'Offline' : 'Chưa xác định'}</strong><small>${profile.online ? realtimeLabel() : 'Tạm dừng nhận dữ liệu'}</small></span>`;
  if (!profile.online) $('.status-dot', pill).style.background = 'var(--neutral)';
  const liveBadge = $('#live-badge');
  liveBadge.classList.toggle('is-paused', !profile.online);
  liveBadge.lastChild.textContent = profile.online ? ` ${realtimeLabel()}` : ' TẠM DỪNG';
}

function drawSparkline(canvas, values, color) {
  values = values.filter(Number.isFinite);
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, rect.width * dpr);
  canvas.height = Math.max(1, rect.height * dpr);
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  if (values.length < 2) return;
  const min = Math.min(...values); const max = Math.max(...values); const span = max - min || 1;
  const x = (i) => i / (values.length - 1) * rect.width;
  const y = (v) => rect.height - 3 - ((v - min) / span) * (rect.height - 6);
  const gradient = ctx.createLinearGradient(0, 0, 0, rect.height);
  gradient.addColorStop(0, `${color}20`); gradient.addColorStop(1, `${color}00`);
  ctx.beginPath(); ctx.moveTo(x(0), y(values[0]));
  values.forEach((v, i) => ctx.lineTo(x(i), y(v)));
  ctx.lineTo(rect.width, rect.height); ctx.lineTo(0, rect.height); ctx.closePath(); ctx.fillStyle = gradient; ctx.fill();
  ctx.beginPath(); ctx.moveTo(x(0), y(values[0])); values.forEach((v, i) => ctx.lineTo(x(i), y(v)));
  ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
}

function updateKpis() {
  const profile = profileForDevice();
  const latest = profile.online ? state.latest : null; const previous = state.data.filter(row => latest && row.time < latest.time).at(-1);
  ['temperature', 'ph', 'turbidity'].forEach((metric) => {
    const card = $(`#${metric}-card`); const config = METRICS[metric]; const value = latest?.[metric];
    const status = profile.online ? evaluateMetric(metric, value) : 'neutral';
    card.dataset.status = status;
    $('[data-value]', card).textContent = value == null ? '--' : value.toFixed(config.decimals).replace('.', ',');
    const badge = $('.status-badge', card); badge.className = `status-badge status-badge--${status}`; badge.textContent = statusLabel(status);
    const trend = $('[data-trend]', card);
    if (value == null || previous?.[metric] == null) { trend.className = 'trend'; trend.textContent = value == null ? '— Chưa có dữ liệu' : `Cập nhật ${age(latest.time)}`; }
    else {
      const diff = value - previous[metric]; const direction = Math.abs(diff) < 0.04 ? 'stable' : diff > 0 ? 'up' : 'down';
      const icon = direction === 'up' ? '↑' : direction === 'down' ? '↓' : '→';
      trend.className = `trend ${direction}`;
      trend.textContent = `${icon} ${Math.abs(diff).toFixed(config.decimals).replace('.', ',')} ${config.unit} · ${age(latest.time)}`;
    }
    drawSparkline($('.sparkline', card), state.data.slice(-22).map((item) => item[metric]), config.color);
  });

  const deviceCard = $('#device-card');
  deviceCard.dataset.status = profile.online ? 'normal' : 'neutral';
  $('[data-value]', deviceCard).textContent = state.error || !state.device ? '--' : profile.online ? 'Online' : state.device.connectivity === 'offline' ? 'Offline' : 'Chưa rõ';
  const deviceBadge = $('.status-badge', deviceCard);
  deviceBadge.className = `status-badge status-badge--${profile.online ? 'normal' : 'neutral'}`;
  deviceBadge.textContent = profile.online ? '● Kết nối tốt' : '— Mất kết nối';
  $('.device-status-line .status-dot', deviceCard).style.background = profile.online ? 'var(--success)' : 'var(--neutral)';
  $('#rssi-value').textContent = profile.rssi == null ? '-- dBm' : `${profile.rssi} dBm`;
  $('#last-seen').textContent = age(state.device?.last_seen_at);
  $('.signal').setAttribute('aria-label', profile.rssi == null ? 'Chưa có RSSI' : `RSSI ${profile.rssi} dBm`);
  const signalBars = $$('.signal-bars i');
  const activeBars = profile.rssi == null ? 0 : profile.rssi > -60 ? 4 : profile.rssi > -70 ? 3 : profile.rssi > -80 ? 2 : 1;
  signalBars.forEach((bar, index) => { bar.style.background = index < activeBars ? 'var(--accent)' : 'var(--border)'; });
}

class HistoryChart {
  constructor(canvas) {
    this.canvas = canvas; this.ctx = canvas.getContext('2d'); this.hoverIndex = null;
    this.resizeObserver = new ResizeObserver(() => this.draw()); this.resizeObserver.observe(canvas.parentElement);
    listen(canvas, 'pointermove', (event) => this.onPointer(event));
    listen(canvas, 'pointerleave', () => { this.hoverIndex = null; $('#chart-tooltip').setAttribute('aria-hidden', 'true'); this.draw(); });
  }

  dimensions() {
    const rect = this.canvas.getBoundingClientRect(); const dpr = window.devicePixelRatio || 1;
    if (this.canvas.width !== Math.round(rect.width * dpr) || this.canvas.height !== Math.round(rect.height * dpr)) {
      this.canvas.width = Math.round(rect.width * dpr); this.canvas.height = Math.round(rect.height * dpr);
    }
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0); return { width: rect.width, height: rect.height, dpr };
  }

  getScale(data, metric) {
    const threshold = getMetricThreshold(metric); const values = data.map((item) => item[metric]).filter(Number.isFinite);
    const anchors = metric === 'turbidity' ? [threshold.max, threshold.danger] : [threshold.min, threshold.max];
    const rawMin = Math.min(...values, ...anchors); const rawMax = Math.max(...values, ...anchors); const padding = Math.max((rawMax - rawMin) * .16, metric === 'ph' ? .25 : 1);
    return { min: metric === 'turbidity' ? Math.max(0, rawMin - padding) : rawMin - padding, max: rawMax + padding };
  }

  draw() {
    const data = currentData(); const metric = state.metric; const { width, height } = this.dimensions(); const ctx = this.ctx;
    ctx.clearRect(0, 0, width, height); this.geometry = null; if (!data.length) return;
    const pad = { left: 50, right: 18, top: 18, bottom: 34 }; const plotW = width - pad.left - pad.right; const plotH = height - pad.top - pad.bottom;
    const scale = this.getScale(data, metric); const threshold = getMetricThreshold(metric); const config = METRICS[metric];
    const x = (i) => pad.left + ((data[i].time - data[0].time) / Math.max(1, data.at(-1).time - data[0].time)) * plotW;
    const y = (value) => pad.top + (1 - (value - scale.min) / (scale.max - scale.min)) * plotH;

    const safeTop = clamp(y(threshold.max), pad.top, pad.top + plotH); const safeBottom = clamp(y(threshold.min), pad.top, pad.top + plotH);
    ctx.fillStyle = 'rgba(96,165,250,.065)'; ctx.fillRect(pad.left, safeTop, plotW, safeBottom - safeTop);
    ctx.fillStyle = 'rgba(255,107,114,.035)'; ctx.fillRect(pad.left, pad.top, plotW, Math.max(0, safeTop - pad.top));
    if (metric !== 'turbidity') ctx.fillRect(pad.left, safeBottom, plotW, pad.top + plotH - safeBottom);
    if (metric === 'turbidity' && threshold.danger < scale.max) { ctx.fillStyle = 'rgba(255,107,114,.06)'; ctx.fillRect(pad.left, pad.top, plotW, y(threshold.danger) - pad.top); }

    ctx.font = '9px "Be Vietnam Pro"'; ctx.textBaseline = 'middle';
    for (let i = 0; i < 5; i++) {
      const value = scale.max - i * (scale.max - scale.min) / 4; const py = pad.top + i * plotH / 4;
      ctx.beginPath(); ctx.moveTo(pad.left, py); ctx.lineTo(width - pad.right, py); ctx.strokeStyle = 'rgba(49,87,100,.24)'; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = '#8fa7b0'; ctx.textAlign = 'right'; ctx.fillText(value.toFixed(metric === 'ph' ? 1 : 0), pad.left - 9, py);
    }
    const tickCount = width < 600 ? 4 : 6;
    for (let i = 0; i < tickCount; i++) {
      const index = Math.round(i * (data.length - 1) / (tickCount - 1)); ctx.fillStyle = '#8fa7b0'; ctx.textAlign = i === 0 ? 'left' : i === tickCount - 1 ? 'right' : 'center'; ctx.fillText(vnTime(data[index].time), x(index), height - 13);
    }

    const lines = metric === 'turbidity'
      ? [{ value: threshold.max, label: `Cảnh báo ${threshold.max}%`, color: '#f6b94d' }, { value: threshold.danger, label: `Nguy hiểm ${threshold.danger}%`, color: '#ff6b72' }]
      : [{ value: threshold.min, label: `Min ${threshold.min}`, color: '#f6b94d' }, { value: threshold.max, label: `Max ${threshold.max}`, color: '#f6b94d' }];
    lines.forEach((line) => {
      const py = y(line.value); ctx.setLineDash([5, 5]); ctx.beginPath(); ctx.moveTo(pad.left, py); ctx.lineTo(width - pad.right, py); ctx.strokeStyle = line.color; ctx.lineWidth = 1; ctx.stroke(); ctx.setLineDash([]);
      const labelWidth = ctx.measureText(line.label).width + 12; ctx.fillStyle = '#0d1d24'; ctx.fillRect(width - pad.right - labelWidth, py - 8, labelWidth, 15); ctx.fillStyle = line.color; ctx.textAlign = 'right'; ctx.fillText(line.label, width - pad.right - 5, py);
    });

    let connected = false;
    ctx.beginPath(); data.forEach((item, index) => {
      if (!Number.isFinite(item[metric])) { connected = false; return; }
      if (connected) ctx.lineTo(x(index), y(item[metric])); else ctx.moveTo(x(index), y(item[metric]));
      connected = true;
    }); ctx.strokeStyle = config.color; ctx.lineWidth = 1.75; ctx.stroke();

    data.forEach((item, index) => { if (evaluateMetric(metric, item[metric]) === 'danger') { ctx.beginPath(); ctx.arc(x(index), y(item[metric]), 3, 0, Math.PI * 2); ctx.fillStyle = '#ff6b72'; ctx.fill(); } });
    if (this.hoverIndex != null && Number.isFinite(data[this.hoverIndex]?.[metric])) {
      const item = data[this.hoverIndex]; const px = x(this.hoverIndex); const py = y(item[metric]);
      ctx.beginPath(); ctx.moveTo(px, pad.top); ctx.lineTo(px, pad.top + plotH); ctx.strokeStyle = 'rgba(181,200,207,.45)'; ctx.setLineDash([3,3]); ctx.stroke(); ctx.setLineDash([]);
      ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI * 2); ctx.fillStyle = '#071116'; ctx.fill(); ctx.lineWidth = 2; ctx.strokeStyle = config.color; ctx.stroke();
    }
    this.geometry = { data, pad, plotW, plotH, x, y };
  }

  onPointer(event) {
    if (!this.geometry?.data.length) return;
    const rect = this.canvas.getBoundingClientRect(); const localX = event.clientX - rect.left; const { data, pad, plotW, x, y } = this.geometry;
    this.hoverIndex = data.reduce((best, item, index) => Math.abs(x(index) - localX) < Math.abs(x(best) - localX) ? index : best, 0);
    const item = data[this.hoverIndex]; const metric = state.metric; const config = METRICS[metric]; const status = evaluateMetric(metric, item[metric]); const tooltip = $('#chart-tooltip');
    tooltip.innerHTML = `${vnTime(item.time, true)}<strong>${item[metric] == null ? '--' : item[metric].toFixed(config.decimals).replace('.', ',')} ${config.unit}</strong>${statusLabel(status).replace(/[✓△!—]\s*/, '')}`;
    tooltip.style.left = `${clamp(x(this.hoverIndex), 8, rect.width - 175)}px`; tooltip.style.top = `${clamp(item[metric] == null ? 50 : y(item[metric]), 42, rect.height - 42)}px`; tooltip.setAttribute('aria-hidden', 'false'); this.draw();
  }
}

const chart = new HistoryChart($('#history-chart'));

function updateChart() {
  chart.hoverIndex = null; $('#chart-tooltip').setAttribute('aria-hidden', 'true');
  const config = METRICS[state.metric]; const data = currentData(); const chartState = $('#chart-state');
  $('#metric-legend').textContent = config.label; $('#metric-legend-line').style.background = config.color;
  $('#history-chart').setAttribute('aria-label', `Biểu đồ lịch sử ${config.label.toLowerCase()} trong ${state.range < 60 ? state.range + ' phút' : state.range / 60 + ' giờ'} qua`);
  $('#chart-summary').textContent = data.length ? `${data.length} mẫu · ${vnTime(data[0].time)}–${vnTime(data.at(-1).time)} · tối đa 500 mẫu` : 'Không có mẫu dữ liệu trong khoảng đã chọn';
  if (state.loading && !state.data.length) { chartState.hidden = false; chartState.className = 'chart-state loading'; chartState.innerHTML = '<span class="sr-only">Đang tải dữ liệu</span>'; }
  else if (state.error) { chartState.hidden = false; chartState.className = 'chart-state'; chartState.textContent = state.error; }
  else if (!data.some(row => Number.isFinite(row[state.metric]))) { chartState.hidden = false; chartState.className = 'chart-state'; chartState.innerHTML = '<div><div class="chart-state__icon">∿</div><strong>Chưa có dữ liệu</strong><p>Thiết bị chưa gửi mẫu đo hợp lệ trong khoảng thời gian này.</p></div>'; }
  else { chartState.hidden = true; }
  chart.draw();
}

function getActiveAlerts() {
  return state.alerts.filter(row => !row.ended_at);
}

function renderAlerts() {
  const content = $('#alert-content'); const active = getActiveAlerts(); $('#alert-count').textContent = active.length;
  const rows = [...(state.alertTab === 'active' ? active : state.alerts)].sort((a,b) => new Date(b.started_at) - new Date(a.started_at));
  if (state.error || state.loading && !state.device) { content.textContent = state.error || 'Đang tải cảnh báo…'; return; }
  if (!rows.length) {
    const known = profileForDevice().online && state.latest && ['temperature','ph','turbidity'].every(key => Number.isFinite(state.latest[key])) && Date.now() - state.latest.time < 60000;
    content.innerHTML = `<div class="empty-state"><h3>${state.alertTab === 'recent' ? 'Chưa có lịch sử cảnh báo' : known ? 'Không có cảnh báo đang xảy ra' : 'Chưa đủ dữ liệu để đánh giá'}</h3><p>${known ? 'Theo bản ghi cảnh báo từ máy chủ.' : 'Kiểm tra kết nối và tuổi mẫu đo.'}</p><span class="checked-time">Kiểm tra lúc ${vnTime(state.lastUpdatedAt)}</span></div>`; return;
  }
  const labels = { temperature: 'Nhiệt độ', ph: 'Độ pH', turbidity: 'Độ đục', offline: 'Mất kết nối', sensor_error: 'Lỗi cảm biến' };
  content.innerHTML = `<div class="alert-list">${rows.map(row => {
    const level = row.ended_at ? 'resolved' : row.severity === 'critical' ? 'danger' : 'warning';
    const duration = Math.max(0, Math.floor(((row.ended_at ? new Date(row.ended_at).getTime() : Date.now()) - new Date(row.started_at).getTime()) / 60000));
    return `<article class="alert-item ${level}"><span class="alert-item__icon">${row.ended_at ? '✓' : '!'}</span><div><div class="alert-item__title"><strong>${escapeHtml(labels[row.alert_type] || row.alert_type)}</strong><span>${row.ended_at ? 'Đã khắc phục' : row.severity === 'critical' ? 'Nguy hiểm' : 'Cảnh báo'}</span></div><p>${escapeHtml(row.message)}</p><p>${new Date(row.started_at).toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' })} · ${duration} phút</p>${row.acknowledged_at ? '<p>Đã xác nhận</p>' : `<button type="button" class="button button--secondary" data-ack="${Number(row.id)}">Xác nhận</button>`}</div></article>`;
  }).join('')}</div>`;
}

function populateThresholdForm() {
  const thresholds = getThresholds(); state.draft = { ...thresholds };
  Object.entries(thresholds).forEach(([key, value]) => { const input = $(`[name="${key}"]`); if (input) input.value = state.thresholdsByDevice[state.deviceId] ? value : ''; });
  state.dirty = false; updateFormState(); $('#form-status').textContent = state.thresholdsByDevice[state.deviceId] ? `Ngưỡng đang áp dụng cho ${state.deviceId}` : 'Chưa tải được ngưỡng từ máy chủ.';
}

function validateThresholds(values) {
  const errors = {};
  Object.entries(values).forEach(([key, value]) => { if (!Number.isFinite(value)) errors[key] = 'Vui lòng nhập một số hợp lệ.'; });
  if (values.tempMin < -55 || values.tempMin > 125) errors.tempMin = 'Giá trị phải từ -55 đến 125.';
  if (values.tempMax < -55 || values.tempMax > 125) errors.tempMax = 'Giá trị phải từ -55 đến 125.';
  if (values.tempMin >= values.tempMax) { errors.tempMin = 'Tối thiểu phải nhỏ hơn tối đa.'; errors.tempMax = 'Tối đa phải lớn hơn tối thiểu.'; }
  if (values.phMin < 0 || values.phMin > 14) errors.phMin = 'Giá trị phải từ 0 đến 14.';
  if (values.phMax < 0 || values.phMax > 14) errors.phMax = 'Giá trị phải từ 0 đến 14.';
  if (values.phMin >= values.phMax) { errors.phMin = 'Tối thiểu phải nhỏ hơn tối đa.'; errors.phMax = 'Tối đa phải lớn hơn tối thiểu.'; }
  if (values.turbidityWarn < 0 || values.turbidityWarn > 100) errors.turbidityWarn = 'Giá trị phải từ 0 đến 100.';
  if (values.turbidityDanger < 0 || values.turbidityDanger > 100) errors.turbidityDanger = 'Giá trị phải từ 0 đến 100.';
  if (values.turbidityWarn >= values.turbidityDanger) { errors.turbidityWarn = 'Cảnh báo phải thấp hơn nguy hiểm.'; errors.turbidityDanger = 'Nguy hiểm phải cao hơn cảnh báo.'; }
  return errors;
}

function updateFormState() {
  const errors = validateThresholds(state.draft);
  $$('#threshold-settings input').forEach((input) => {
    const field = input.closest('.field'); const error = errors[input.name]; field.classList.toggle('is-invalid', Boolean(error)); $('.field-error', field).textContent = error || ''; input.setAttribute('aria-invalid', String(Boolean(error)));
  });
  $('#save-thresholds').disabled = state.saving || !state.thresholdsByDevice[state.deviceId] || !state.dirty || Object.keys(errors).length > 0;
  $$('#threshold-settings input').forEach(input => { input.disabled = state.saving || !state.thresholdsByDevice[state.deviceId]; });
  $('#unsaved-badge').hidden = !state.dirty;
  return Object.keys(errors).length === 0;
}

function showToast(title, message, type = 'success') {
  const toast = document.createElement('div'); toast.className = `toast ${type === 'error' ? 'toast--error' : ''}`; toast.setAttribute('role', 'status'); toast.innerHTML = `<span class="toast__icon">${type === 'error' ? '!' : '✓'}</span><div><strong>${title}</strong><small>${message}</small></div>`; $('#toast-region').append(toast); setTimeout(() => toast.remove(), 4000);
}

function renderAll() { updateHeader(); updateKpis(); updateChart(); renderAlerts(); }

let refreshController;
async function refreshData(quiet = false) {
  if (state.saving || quiet && state.loading) return;
  refreshController?.abort();
  const controller = new AbortController(); refreshController = controller;
  const deviceId = state.deviceId;
  state.loading = true;
  const button = $('#refresh-button'); button.classList.add('is-loading'); button.disabled = true; updateChart();
  try {
    const result = await snapshot(deviceId, state.range, controller.signal);
    if (controller.signal.aborted || deviceId !== state.deviceId) return;
    state.device = result.device; state.latest = result.latest; state.data = result.history; state.alerts = result.alerts;
    state.thresholdsByDevice[deviceId] = result.thresholds; state.error = ''; state.lastUpdatedAt = new Date();
    if (!state.dirty) populateThresholdForm();
  } catch (error) {
    if (controller.signal.aborted) return;
    state.error = error.message || 'Không tải được dữ liệu. Nhấn Làm mới để thử lại.';
  } finally {
    if (refreshController === controller) { state.loading = false; button.classList.remove('is-loading'); button.disabled = false; renderAll(); }
  }
}

listen($('#device-select'), 'change', async (event) => {
  if (state.dirty && !window.confirm('Bạn có thay đổi ngưỡng chưa lưu. Chuyển thiết bị và bỏ các thay đổi này?')) { event.target.value = state.deviceId; return; }
  state.deviceId = event.target.value; onDeviceChange(state.deviceId); const url = new URL(location.href); url.searchParams.set('device_id', state.deviceId); history.replaceState(null, '', url); state.device = null; state.latest = null; state.alerts = []; state.data = []; state.error = ''; populateThresholdForm(); renderAll(); await refreshData();
});

listen($('#refresh-button'), 'click', () => refreshData());
listen($('#metric-select'), 'change', (event) => { state.metric = event.target.value; updateChart(); });
$$('[data-range]').forEach((button) => listen(button, 'click', () => {
  $$('[data-range]').forEach((item) => { const active = item === button; item.classList.toggle('is-active', active); item.setAttribute('aria-pressed', String(active)); });
  state.range = Number(button.dataset.range); updateChart(); refreshData();
}));
$$('[data-tab]').forEach((button) => listen(button, 'click', () => {
  state.alertTab = button.dataset.tab; $$('[data-tab]').forEach((item) => item.setAttribute('aria-selected', String(item === button))); renderAlerts();
}));

listen($('#threshold-settings'), 'input', (event) => {
  if (!(event.target instanceof HTMLInputElement)) return; state.draft[event.target.name] = event.target.value.trim() ? Number(event.target.value) : NaN; state.dirty = JSON.stringify(state.draft) !== JSON.stringify(getThresholds()); updateFormState();
});
listen($('#threshold-settings'), 'submit', async (event) => {
  event.preventDefault(); if (state.saving || !state.dirty || !state.thresholdsByDevice[state.deviceId] || !updateFormState()) return;
  const deviceId = state.deviceId; const button = $('#save-thresholds');
  refreshController?.abort(); state.saving = true; state.loading = false; button.textContent = 'Đang lưu…'; $('#device-select').disabled = true; $('#reload-thresholds').disabled = true; updateFormState();
  try {
    const saved = await request(deviceId, '/thresholds', { method: 'PUT', body: JSON.stringify(encodeThresholds(state.draft)) });
    state.thresholdsByDevice[deviceId] = decodeThresholds(saved); populateThresholdForm();
    showToast('Đã lưu ngưỡng', `Máy chủ đã lưu cấu hình ${escapeHtml(deviceId)}.`);
  } catch (error) { showToast('Không lưu được ngưỡng', escapeHtml(error.message), 'error'); }
  finally { state.saving = false; button.textContent = 'Lưu ngưỡng'; $('#device-select').disabled = false; $('#reload-thresholds').disabled = false; updateFormState(); await refreshData(true); }
});
listen($('#reload-thresholds'), 'click', () => {
  if (state.dirty && !confirm('Tải lại và bỏ thay đổi chưa lưu?')) return;
  state.dirty = false; refreshData();
});
listen($('#alert-content'), 'click', async event => {
  const button = event.target.closest('[data-ack]'); if (!button) return;
  const deviceId = state.deviceId; button.disabled = true;
  try { await request(deviceId, `/alerts/${button.dataset.ack}/acknowledge`, { method: 'POST' }); if (deviceId === state.deviceId) await refreshData(); }
  catch (error) { showToast('Không xác nhận được', escapeHtml(error.message), 'error'); button.disabled = false; }
});
listen(window, 'beforeunload', (event) => { if (!state.dirty) return; event.preventDefault(); event.returnValue = ''; });
listen(window, 'resize', () => { updateKpis(); chart.draw(); });

const requestedDevice = new URLSearchParams(location.search).get('device_id');
const validId = value => /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(value);
if (requestedDevice && validId(requestedDevice)) state.deviceId = requestedDevice;
$('#device-select').replaceChildren(...[...new Set([state.deviceId, 'tank-demo-001', 'tank-preview-001'])].map(id => new Option(id, id)));
$('#device-select').value = state.deviceId;
listen($('#add-device'), 'click', () => {
  if (state.saving) return;
  const id = prompt('Nhập mã thiết bị đã đăng ký (tối đa 64 ký tự):');
  if (!id) return;
  if (!validId(id)) { showToast('Mã không hợp lệ', 'Chỉ dùng chữ, số, dấu gạch ngang hoặc gạch dưới.', 'error'); return; }
  const select = $('#device-select'); if (![...select.options].some(option => option.value === id)) select.add(new Option(id, id));
  select.value = id; select.dispatchEvent(new Event('change'));
});
onDeviceChange(state.deviceId);
populateThresholdForm(); renderAll(); refreshData();
const pollTimer = setInterval(() => { if (!document.hidden && realtimeLabel() !== 'Live') refreshData(true); }, 5000);
const ageTimer = setInterval(() => { updateHeader(); updateKpis(); }, 1000);

return { refresh: () => refreshData(true), dispose() {
  lifetime.abort(); refreshController?.abort(); clearInterval(pollTimer); clearInterval(ageTimer);
  chart.resizeObserver.disconnect(); listeners.forEach(remove => remove());
} };
}
