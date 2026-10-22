<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import template from '../dashboard/template.html?raw'
import { mountDashboard } from '../dashboard/dashboard.js'
import { useRealtime } from '../composables/useRealtime'

const root = ref<HTMLElement | null>(null)
const queryId = new URLSearchParams(location.search).get('device_id')
const deviceId = ref(queryId && /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(queryId) ? queryId : 'tank-demo-001')
let dashboard: ReturnType<typeof mountDashboard> | undefined
const { state: realtime } = useRealtime(deviceId, async () => { await dashboard?.refresh() })
const label = () => realtime.value === 'connected' ? 'Live' : 'Đang kết nối lại'
onMounted(() => {
  dashboard = mountDashboard(root.value!, id => { deviceId.value = id }, label)
})
onBeforeUnmount(() => dashboard?.dispose())
</script>

<template>
  <!-- Trusted bundled markup. All server text is escaped by the dashboard renderer. -->
  <div ref="root" v-html="template"></div>
</template>
