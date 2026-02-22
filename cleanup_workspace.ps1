# Script untuk Rapihkan Folder
# Akan membuat struktur folder yang lebih bersih

Write-Host "=== Cleaning up workspace ===" -ForegroundColor Cyan
Write-Host ""

# 1. Create folders for organization
Write-Host "1. Creating organization folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "_casaos_deploy" | Out-Null
New-Item -ItemType Directory -Force -Path "_dev" | Out-Null

# 2. Move CasaOS deployment scripts
Write-Host "2. Moving CasaOS deployment scripts..." -ForegroundColor Yellow
$casaos_files = @(
    "deploy-to-casaos.ps1",
    "deploy_license_server_casaos.py",
    "deploy_license_server_now.ps1",
    "deploy_quick.ps1",
    "deploy_license_ui_hotfix.py",
    "check_license_server_casaos.py",
    "check_license_server_container.py",
    "create_license_on_casaos.py",
    "generate_customer_license.ps1",
    "get_license_server_logs.py",
    "get_server_logs.py",
    "restart_license_server_casaos.py",
    "generate_license_keys.py",
    "GENERATE_LICENSE_GUIDE.md",
    "casaos-config.json"
)
foreach ($file in $casaos_files) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "_casaos_deploy/" -Force
        Write-Host "  + $file" -ForegroundColor Green
    }
}

# 3. Move dev/test files
Write-Host "3. Moving development/test files..." -ForegroundColor Yellow
$dev_files = @(
    "analyze_auth_issue.py",
    "app_simple.py",
    "check_all_tables.py",
    "check_and_fix_template.py",
    "check_db_schema.py",
    "check_docker_logs.py",
    "check_scheduler_logs.py",
    "check_scheduler_status.py",
    "check_server_response.py",
    "check_sync.py",
    "check_template_updated.py",
    "check_users.py",
    "check_users_docker.py",
    "cleanup_kas_templates.py",
    "clear_cache_and_restart.py",
    "debug_endpoints.py",
    "debug_login.py",
    "debug_remote_template.py",
    "debug_server.py",
    "debug_session_cookies.py",
    "deploy_remove_kas.py",
    "deploy_scheduler.py",
    "deploy_template_fix.py",
    "deploy_updated_template.py",
    "direct_migration.py",
    "extract_login_page.py",
    "final_export_test.py",
    "final_verification.py",
    "force_restart_and_check.py",
    "get_logs.py",
    "quick_check.py",
    "quick_export_test.py",
    "quick_server_status.py",
    "recovery_deploy_scheduler.py",
    "remote_check_telegram_status.py",
    "remote_docker_inspect_5000.py",
    "remote_find_kasir_compose.py",
    "remote_verify_export_excel.py",
    "restart_docker.py",
    "simple_scheduler_check.py",
    "simple_test.py",
    "telegram_bot.py",
    "test_app_methods.py",
    "test_auto_report.py",
    "test_export_after_fix.py",
    "test_export_correct_credentials.py",
    "test_export_debug.py",
    "test_export_debug_v2.py",
    "test_export_detailed.py",
    "test_export_fix.py",
    "test_export_modal_final.py",
    "test_kas_endpoint.py",
    "test_kas_route.py",
    "verify_api_endpoints.py",
    "verify_deployment.py",
    "verify_remote.py",
    "verify_scheduler_working.py",
    "verify_template_deployment.py",
    "wait_and_verify_live.py",
    "wait_for_server_final.py"
)
foreach ($file in $dev_files) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "_dev/" -Force
    }
}
Write-Host "  + Moved $(($dev_files | Where-Object {Test-Path "_dev/$_"}).Count) files" -ForegroundColor Green

# 4. Remove temporary/backup files
Write-Host "4. Removing temporary files..." -ForegroundColor Yellow
$temp_files = @(
    "BACKUP_QUICK_START.txt",
    "BACKUP_README.md",
    "deployment_log.txt",
    "DEPLOYMENT_SUMMARY_2026-02-20.md",
    "server_docker_logs.txt",
    "login_page.html",
    "server_response_laporan.html",
    "app_simple_b64.txt",
    "export_modal_test_result.xlsx"
)
foreach ($file in $temp_files) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "  - $file" -ForegroundColor Red
    }
}

# 5. Remove unnecessary folders
Write-Host "5. Removing unnecessary folders..." -ForegroundColor Yellow
$temp_folders = @(
    "Connect to Telegram Fitur Komplit - Copy",
    "antigravity-redirect",
    "sale_package",
    "backups",
    "img",
    "venv",
    "__pycache__"
)
foreach ($folder in $temp_folders) {
    if (Test-Path $folder) {
        Remove-Item -Path $folder -Recurse -Force
        Write-Host "  - $folder/" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Cleanup complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "New structure:" -ForegroundColor Cyan
Write-Host "  app/                    (Main application)" -ForegroundColor White
Write-Host "  customer_packages/      (Paket untuk customer)" -ForegroundColor White
Write-Host "  license_server/         (License server)" -ForegroundColor White
Write-Host "  _casaos_deploy/         (Script deploy ke CasaOS)" -ForegroundColor Yellow
Write-Host "  _dev/                   (Dev/test scripts)" -ForegroundColor Gray
Write-Host "  migrations/             (Database migrations)" -ForegroundColor White
Write-Host "  scripts/                (Utility scripts)" -ForegroundColor White
Write-Host "  tools/                  (Additional tools)" -ForegroundColor White
Write-Host "  tests/                  (Unit tests)" -ForegroundColor White
Write-Host "  docs/                   (Documentation)" -ForegroundColor White
Write-Host "  .github/                (GitHub workflows)" -ForegroundColor White
Write-Host "  Core files              (Dockerfile, docker-compose.yml, etc.)" -ForegroundColor White
