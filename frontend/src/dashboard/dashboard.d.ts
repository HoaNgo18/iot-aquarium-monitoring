export function mountDashboard(root: HTMLElement, onDeviceChange: (id: string) => void, realtimeLabel: () => string): { refresh: () => Promise<void>; dispose: () => void };
