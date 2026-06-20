# Backup PostgreSQL - PowerShell version
param(
    [string]$BackupDir = ".\backups",
    [string]$Container = "uniclothes-postgres",
    [string]$PostgresUser = "uniclothes",
    [string]$PostgresDb = "uniclothes"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "uniclothes_$timestamp.sql"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

Write-Host "Backing up $PostgresDb to $backupFile..."
docker exec $Container pg_dump -U $PostgresUser $PostgresDb | Out-File -FilePath $backupFile -Encoding utf8
Write-Host "Backup complete: $backupFile"
