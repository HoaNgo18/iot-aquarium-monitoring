$ErrorActionPreference = "Stop"

$backendPort = if ($env:BACKEND_HOST_PORT) { $env:BACKEND_HOST_PORT } else { "8000" }
$baseUrl = "http://127.0.0.1:$backendPort"
$deviceId = "node-backend-smoke"

$health = Invoke-RestMethod "$baseUrl/health"
if ($health.database -ne "up") {
    throw "Backend không kết nối được PostgreSQL."
}

docker compose --profile simulator run --rm `
    -e "DEVICE_ID=$deviceId" `
    -e "SIMULATOR_SCENARIO=normal" `
    -e "SIMULATOR_MESSAGE_COUNT=3" `
    -e "PUBLISH_INTERVAL_SECONDS=0.2" `
    simulator

if ($LASTEXITCODE -ne 0) {
    throw "Telemetry simulator chạy không thành công."
}

Start-Sleep -Seconds 1
$latest = Invoke-RestMethod "$baseUrl/api/v1/devices/$deviceId/telemetry/latest"
$history = Invoke-RestMethod "$baseUrl/api/v1/devices/$deviceId/telemetry?limit=10"

if ($latest.device_id -ne $deviceId) {
    throw "API latest trả về sai device_id."
}
if ($history.Count -ne 3) {
    throw "API history phải có 3 bản ghi nhưng nhận được $($history.Count)."
}

Write-Host "PASS: simulator -> MQTT -> backend -> PostgreSQL -> REST API hoạt động." -ForegroundColor Green
