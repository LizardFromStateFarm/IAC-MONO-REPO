# K3s Production Environment Deployment Script (Terraform)
# This script deploys both the cluster and metrics server stacks

Write-Host "🚀 Starting K3s Production Environment Deployment (Terraform)" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan

# Function to run commands and check results
function Invoke-Command {
    param(
        [string]$Command,
        [string]$WorkingDirectory,
        [string]$Description
    )
    
    Write-Host "📋 $Description" -ForegroundColor Yellow
    Write-Host "Working Directory: $WorkingDirectory" -ForegroundColor Gray
    Write-Host "Command: $Command" -ForegroundColor Gray
    
    Push-Location $WorkingDirectory
    try {
        $result = Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $Description completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $Description failed with exit code $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ $Description failed with error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        Pop-Location
    }
}

# Step 1: Deploy Cluster
Write-Host "`n🏗️  Step 1: Deploying K3s Cluster" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

$clusterSuccess = $true
$clusterSuccess = $clusterSuccess -and (Invoke-Command "terraform init" "cluster" "Initializing cluster Terraform")
$clusterSuccess = $clusterSuccess -and (Invoke-Command "terraform plan" "cluster" "Planning cluster deployment")
$clusterSuccess = $clusterSuccess -and (Invoke-Command "terraform apply -auto-approve" "cluster" "Deploying cluster")

if (-not $clusterSuccess) {
    Write-Host "❌ Cluster deployment failed. Stopping deployment." -ForegroundColor Red
    exit 1
}

# Step 2: Deploy Metrics Server
Write-Host "`n📊 Step 2: Deploying Metrics Server" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

$metricsSuccess = $true
$metricsSuccess = $metricsSuccess -and (Invoke-Command "terraform init" "metrics-server" "metrics-server" "Initializing metrics server Terraform")
$metricsSuccess = $metricsSuccess -and (Invoke-Command "terraform plan" "metrics-server" "Planning metrics server deployment")
$metricsSuccess = $metricsSuccess -and (Invoke-Command "terraform apply -auto-approve" "metrics-server" "Deploying metrics server")

if (-not $metricsSuccess) {
    Write-Host "❌ Metrics server deployment failed." -ForegroundColor Red
    exit 1
}

# Step 3: Verification
Write-Host "`n🔍 Step 3: Verifying Deployment" -ForegroundColor Cyan
Write-Host "-" * 40 -ForegroundColor Cyan

Write-Host "📋 Checking cluster status..." -ForegroundColor Yellow
try {
    $nodes = kubectl get nodes --no-headers 2>$null
    if ($nodes) {
        Write-Host "✅ Cluster nodes found:" -ForegroundColor Green
        $nodes | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠️  No nodes found. Cluster may still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not check cluster status. Make sure kubectl is configured." -ForegroundColor Yellow
}

Write-Host "`n📋 Checking metrics server..." -ForegroundColor Yellow
try {
    $metricsPods = kubectl get pods -n kube-system --no-headers | Select-String "metrics-server"
    if ($metricsPods) {
        Write-Host "✅ Metrics server pods found:" -ForegroundColor Green
        $metricsPods | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠️  No metrics server pods found. May still be starting..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not check metrics server status." -ForegroundColor Yellow
}

# Summary
Write-Host "`n🎉 Deployment Summary" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ K3s Production Environment deployed successfully!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Wait a few minutes for all pods to be ready" -ForegroundColor Gray
Write-Host "  2. Run: kubectl get pods --all-namespaces" -ForegroundColor Gray
Write-Host "  3. Test metrics: kubectl top nodes" -ForegroundColor Gray
Write-Host "  4. Test metrics: kubectl top pods --all-namespaces" -ForegroundColor Gray
Write-Host "`n🔧 Management Commands:" -ForegroundColor Yellow
Write-Host "  • Update cluster: cd cluster && terraform apply" -ForegroundColor Gray
Write-Host "  • Update metrics: cd metrics-server && terraform apply" -ForegroundColor Gray
Write-Host "  • Destroy all: cd metrics-server && terraform destroy && cd ../cluster && terraform destroy" -ForegroundColor Gray
Write-Host "`n⚠️  Production Environment:" -ForegroundColor Yellow
Write-Host "  • Higher resource allocation (4Gi memory per node, 2 worker nodes)" -ForegroundColor Gray
Write-Host "  • Consider using remote state backends for production" -ForegroundColor Gray
