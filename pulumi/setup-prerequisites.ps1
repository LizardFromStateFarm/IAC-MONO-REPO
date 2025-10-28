# PowerShell script to install prerequisites for Pulumi Kind monorepo
# Run this script as Administrator

Write-Host "Setting up prerequisites for Pulumi Kind monorepo..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to install Pulumi CLI
function Install-Pulumi {
    Write-Host "Installing Pulumi CLI..." -ForegroundColor Yellow
    
    # Download and install Pulumi
    $pulumiUrl = "https://get.pulumi.com/install.ps1"
    try {
        Invoke-WebRequest -Uri $pulumiUrl -OutFile "$env:TEMP\install-pulumi.ps1"
        & "$env:TEMP\install-pulumi.ps1"
        Write-Host "✓ Pulumi CLI installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to install Pulumi CLI: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    return $true
}

# Function to install Kind
function Install-Kind {
    Write-Host "Installing Kind (Kubernetes in Docker)..." -ForegroundColor Yellow
    
    # Download Kind binary
    $kindUrl = "https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64"
    $kindPath = "$env:ProgramFiles\kind\kind.exe"
    
    try {
        # Create directory
        New-Item -ItemType Directory -Force -Path "$env:ProgramFiles\kind"
        
        # Download Kind
        Invoke-WebRequest -Uri $kindUrl -OutFile $kindPath
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($currentPath -notlike "*$env:ProgramFiles\kind*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$env:ProgramFiles\kind", "Machine")
        }
        
        Write-Host "✓ Kind installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to install Kind: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    return $true
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    
    try {
        # Install pip packages
        pip install --upgrade pip
        pip install pulumi pulumi-kubernetes pulumi-command
        
        Write-Host "✓ Python dependencies installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to install Python dependencies: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    return $true
}

# Main installation process
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

# Check Python
if (-not (Test-Command "python")) {
    Write-Host "✗ Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python is installed" -ForegroundColor Green

# Check Docker
if (-not (Test-Command "docker")) {
    Write-Host "✗ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker is installed" -ForegroundColor Green

# Check kubectl
if (-not (Test-Command "kubectl")) {
    Write-Host "✗ kubectl is not installed. Please install kubectl first." -ForegroundColor Red
    exit 1
}
Write-Host "✓ kubectl is installed" -ForegroundColor Green

# Install Pulumi CLI
if (-not (Test-Command "pulumi")) {
    if (-not (Install-Pulumi)) {
        exit 1
    }
} else {
    Write-Host "✓ Pulumi CLI is already installed" -ForegroundColor Green
}

# Install Kind
if (-not (Test-Command "kind")) {
    if (-not (Install-Kind)) {
        exit 1
    }
} else {
    Write-Host "✓ Kind is already installed" -ForegroundColor Green
}

# Install Python dependencies
if (-not (Install-PythonDependencies)) {
    exit 1
}

# Refresh environment variables
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

Write-Host "`nAll prerequisites installed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Restart your PowerShell session to refresh environment variables" -ForegroundColor White
Write-Host "2. Run: python utilities/scripts/install-dependencies.py" -ForegroundColor White
Write-Host "3. MANUALLY run: cd nonprod && pulumi up" -ForegroundColor Yellow
Write-Host "4. MANUALLY run: cd prod && pulumi up" -ForegroundColor Yellow
Write-Host "`nIMPORTANT: Project deployment must be done MANUALLY!" -ForegroundColor Red
