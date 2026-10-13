<template>
  <article class="panel chart-panel" aria-labelledby="water-chart-title">
    <div class="panel-heading">
      <h2 id="water-chart-title">Mực nước</h2>
      <span class="panel-unit">cm</span>
    </div>
    <div class="chart-legend" title="Đường ngưỡng minh họa; chưa tải cấu hình ngưỡng">
      <span><i class="legend-line threshold-warning" aria-hidden="true"></i>Cảnh báo</span>
      <span><i class="legend-line threshold-danger" aria-hidden="true"></i>Nguy hiểm</span>
      <span class="threshold-note">Ngưỡng minh họa</span>
    </div>
    <div class="chart-area">
      <svg class="water-chart" viewBox="0 0 720 240" preserveAspectRatio="none" aria-hidden="true">
        <path class="chart-grid" d="M0 12H720 M0 84H720 M0 156H720 M0 228H720" />
        <path class="chart-threshold chart-threshold-danger" d="M0 60H720" />
        <path class="chart-threshold chart-threshold-warning" d="M0 132H720" />
      </svg>
      <p class="chart-empty">Chưa có dữ liệu</p>
    </div>
    <div class="chart-axis" aria-hidden="true"><span>Thời gian</span></div>
  </article>
</template>
