#!/bin/bash
# Bash script to install prerequisites for Pulumi Kind monorepo
# Run this script on macOS/Linux

echo "Setting up prerequisites for Pulumi Kind monorepo..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Pulumi CLI
install_pulumi() {
    echo "Installing Pulumi CLI..."
    
    if command_exists curl; then
        curl -fsSL https://get.pulumi.com | sh
        echo "✓ Pulumi CLI installed successfully"
    else
        echo "✗ curl is not installed. Please install curl first."
        return 1
    fi
}

# Function to install Kind
install_kind() {
    echo "Installing Kind (Kubernetes in Docker)..."
    
    # Detect OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install kind
        else
            echo "✗ Homebrew is not installed. Please install Homebrew first."
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists curl; then
            curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
            chmod +x ./kind
            sudo mv ./kind /usr/local/bin/kind
        else
            echo "✗ curl is not installed. Please install curl first."
            return 1
        fi
    else
        echo "✗ Unsupported OS: $OSTYPE"
        return 1
    fi
    
    echo "✓ Kind installed successfully"
}

# Function to install Python dependencies
install_python_dependencies() {
    echo "Installing Python dependencies..."
    
    if command_exists pip3; then
        pip3 install --upgrade pip
        pip3 install pulumi pulumi-kubernetes pulumi-command
    elif command_exists pip; then
        pip install --upgrade pip
        pip install pulumi pulumi-kubernetes pulumi-command
    else
        echo "✗ pip is not installed. Please install pip first."
        return 1
    fi
    
    echo "✓ Python dependencies installed successfully"
}

# Main installation process
echo "Checking prerequisites..."

# Check Python
if ! command_exists python3 && ! command_exists python; then
    echo "✗ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi
echo "✓ Python is installed"

# Check Docker
if ! command_exists docker; then
    echo "✗ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✓ Docker is installed"

# Check kubectl
if ! command_exists kubectl; then
    echo "✗ kubectl is not installed. Please install kubectl first."
    exit 1
fi
echo "✓ kubectl is installed"

# Install Pulumi CLI
if ! command_exists pulumi; then
    if ! install_pulumi; then
        exit 1
    fi
else
    echo "✓ Pulumi CLI is already installed"
fi

# Install Kind
if ! command_exists kind; then
    if ! install_kind; then
        exit 1
    fi
else
    echo "✓ Kind is already installed"
fi

# Install Python dependencies
if ! install_python_dependencies; then
    exit 1
fi

echo ""
echo "All prerequisites installed successfully!"
echo ""
echo "Next steps:"
echo "1. Run: python utilities/scripts/install-dependencies.py"
echo "2. MANUALLY run: cd nonprod && pulumi up"
echo "3. MANUALLY run: cd prod && pulumi up"
echo ""
echo "IMPORTANT: Project deployment must be done MANUALLY!"
