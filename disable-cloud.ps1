# Disable Pulumi Cloud completely and force local state
Write-Host "Disabling Pulumi Cloud and configuring local state only..." -ForegroundColor Red

# Set environment variable to disable cloud
$env:PULUMI_BACKEND_URL = "file://~/.pulumi/state"

# Login to local state
pulumi login --local

Write-Host "Pulumi Cloud disabled. All state will be stored locally." -ForegroundColor Green
Write-Host "State location: ~/.pulumi/state" -ForegroundColor Yellow
