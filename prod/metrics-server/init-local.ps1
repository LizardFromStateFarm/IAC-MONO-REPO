# Initialize Pulumi with local state for prod metrics-server
Write-Host "Initializing Pulumi with local state for prod metrics-server..." -ForegroundColor Green

# Ensure we're using local state
pulumi login --local

# Create a unique state file for this tool/environment
$stateFile = ".\state\prod-metrics-server.json"
New-Item -ItemType Directory -Force -Path ".\state" | Out-Null

# Initialize the stack with local state
pulumi stack init prod

# Set the state file location
pulumi config set --path backend.url "file://$((Get-Location).Path)\state\prod-metrics-server.json"

Write-Host "Local state initialized for prod metrics-server" -ForegroundColor Green
Write-Host "State file: $stateFile" -ForegroundColor Yellow
