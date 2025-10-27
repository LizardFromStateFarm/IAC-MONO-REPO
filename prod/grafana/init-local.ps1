# Initialize Pulumi with local state for prod grafana
Write-Host "Initializing Pulumi with local state for prod grafana..." -ForegroundColor Green

# Ensure we're using local state
pulumi login --local

# Create a unique state file for this tool/environment
$stateFile = ".\state\prod-grafana.json"
New-Item -ItemType Directory -Force -Path ".\state" | Out-Null

# Initialize the stack with local state
pulumi stack init prod

# Set the state file location
pulumi config set --path backend.url "file://$((Get-Location).Path)\state\prod-grafana.json"

Write-Host "Local state initialized for prod grafana" -ForegroundColor Green
Write-Host "State file: $stateFile" -ForegroundColor Yellow
