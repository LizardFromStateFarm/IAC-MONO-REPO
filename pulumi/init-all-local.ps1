# Master script to initialize all tools with separate local state files
Write-Host "Initializing all Pulumi tools with separate local state files..." -ForegroundColor Green

# First, disable cloud completely
Write-Host "Step 1: Disabling Pulumi Cloud..." -ForegroundColor Yellow
.\disable-cloud.ps1

# Initialize all prod tools
Write-Host "`nStep 2: Initializing PROD tools..." -ForegroundColor Yellow
Write-Host "Initializing prod/kind-cluster..." -ForegroundColor Cyan
cd prod\kind-cluster
.\init-local.ps1
cd ..\..

Write-Host "Initializing prod/grafana..." -ForegroundColor Cyan
cd prod\grafana
.\init-local.ps1
cd ..\..

Write-Host "Initializing prod/metrics-server..." -ForegroundColor Cyan
cd prod\metrics-server
.\init-local.ps1
cd ..\..

# Initialize all nonprod tools
Write-Host "`nStep 3: Initializing NONPROD tools..." -ForegroundColor Yellow
Write-Host "Initializing nonprod/kind-cluster..." -ForegroundColor Cyan
cd nonprod\kind-cluster
.\init-local.ps1
cd ..\..

Write-Host "Initializing nonprod/grafana..." -ForegroundColor Cyan
cd nonprod\grafana
.\init-local.ps1
cd ..\..

Write-Host "Initializing nonprod/metrics-server..." -ForegroundColor Cyan
cd nonprod\metrics-server
.\init-local.ps1
cd ..\..

Write-Host "`n✅ All tools initialized with separate local state files!" -ForegroundColor Green
Write-Host "`nState file locations:" -ForegroundColor Yellow
Write-Host "  prod/kind-cluster/state/prod-kind-cluster.json" -ForegroundColor White
Write-Host "  prod/grafana/state/prod-grafana.json" -ForegroundColor White
Write-Host "  prod/metrics-server/state/prod-metrics-server.json" -ForegroundColor White
Write-Host "  nonprod/kind-cluster/state/nonprod-kind-cluster.json" -ForegroundColor White
Write-Host "  nonprod/grafana/state/nonprod-grafana.json" -ForegroundColor White
Write-Host "  nonprod/metrics-server/state/nonprod-metrics-server.json" -ForegroundColor White
