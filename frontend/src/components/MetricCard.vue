<script setup lang="ts">
import type { MetricSummary } from '../types/monitoring'

defineProps<{
  metric: MetricSummary
}>()
</script>

<template>
  <article class="metric-card">
    <p class="metric-title">{{ metric.title }}</p>
    <p class="metric-value">
      <span class="metric-number">{{ metric.value.replace(/\s(?:cm|mm)$/, '') }}</span>
      <span v-if="metric.value.endsWith(' cm') || metric.value.endsWith(' mm')" class="metric-unit">
        {{ metric.value.endsWith(' cm') ? 'cm' : 'mm' }}
      </span>
    </p>
    <p class="metric-description">
      {{ metric.description.includes('Cảm biến lỗi') ? 'Cảm biến lỗi'
        : metric.title === 'Lượng mưa' ? 'Theo chu kỳ đo'
          : metric.value.startsWith('--') ? 'Chưa có dữ liệu' : 'Mẫu gần nhất' }}
    </p>
  </article>
</template>
