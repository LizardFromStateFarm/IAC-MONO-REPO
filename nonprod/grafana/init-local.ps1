# Initialize Pulumi with local state for nonprod grafana
Write-Host "Initializing Pulumi with local state for nonprod grafana..." -ForegroundColor Green

# Ensure we're using local state
pulumi login --local

# Create a unique state file for this tool/environment
$stateFile = ".\state\nonprod-grafana.json"
New-Item -ItemType Directory -Force -Path ".\state" | Out-Null

# Initialize the stack with local state
pulumi stack init nonprod

# Set the state file location
pulumi config set --path backend.url "file://$((Get-Location).Path)\state\nonprod-grafana.json"

Write-Host "Local state initialized for nonprod grafana" -ForegroundColor Green
Write-Host "State file: $stateFile" -ForegroundColor Yellow
