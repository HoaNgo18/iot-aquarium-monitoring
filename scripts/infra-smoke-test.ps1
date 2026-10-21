$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    $runningServices = docker compose ps --services --status running
    if ($LASTEXITCODE -ne 0) {
        throw "Không đọc được trạng thái Docker Compose. Hãy kiểm tra Docker Desktop."
    }

    if ($runningServices -notcontains "mqtt" -or $runningServices -notcontains "db") {
        throw "Mosquitto và PostgreSQL chưa cùng chạy. Dùng: docker compose up -d"
    }

    docker compose exec -T db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL chưa sẵn sàng."
    }

    # A broker-only topic avoids replaying an old retained measurement into ingestion.
    $topic = "aquarium-monitoring/diagnostics/smoke-test"
    $payload = '{"device_id":"smoke-test","message":"broker-check"}'

    docker compose exec -T mqtt mosquitto_pub `
        -h 127.0.0.1 `
        -p 1883 `
        -t $topic `
        -m $payload `
        -q 1 `
        -r
    if ($LASTEXITCODE -ne 0) {
        throw "Không publish được bản tin MQTT kiểm thử."
    }

    $received = docker compose exec -T mqtt mosquitto_sub `
        -h 127.0.0.1 `
        -p 1883 `
        -t $topic `
        -C 1 `
        -W 5
    if ($LASTEXITCODE -ne 0) {
        throw "Không subscribe được bản tin MQTT kiểm thử."
    }

    if ($received -notmatch '"device_id":"smoke-test"') {
        throw "Payload MQTT nhận được không đúng: $received"
    }

    docker compose exec -T mqtt mosquitto_pub `
        -h 127.0.0.1 `
        -p 1883 `
        -t $topic `
        -n `
        -r

    Write-Host "PASS: PostgreSQL sẵn sàng và Mosquitto publish/subscribe thành công."
}
finally {
    Pop-Location
}

