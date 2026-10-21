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
      <span class="metric-number">{{ metric.value }}</span>
      <span v-if="metric.unit && metric.value !== 'Đang tải…'" class="metric-unit">
        {{ metric.unit }}
      </span>
    </p>
    <p class="metric-description">
      {{ metric.description }}
    </p>
  </article>
</template>
