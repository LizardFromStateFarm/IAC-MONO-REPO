#!/usr/bin/env python3
"""
Install dependencies for the Pulumi monorepo
This script installs dependencies for all packages and environments
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: str = None) -> bool:
    """Run a command and return True if successful."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False


def check_prerequisites():
    """Check if required tools are installed."""
    print("Checking prerequisites...")
    
    required_tools = {
        "docker": "Docker is required for Kind clusters",
        "kubectl": "kubectl is required for Kubernetes management",
        "kind": "Kind is required for local Kubernetes clusters",
        "pulumi": "Pulumi CLI is required for infrastructure management"
    }
    
    missing_tools = []
    for tool, description in required_tools.items():
        if not run_command(f"which {tool}"):
            missing_tools.append(f"{tool} - {description}")
    
    if missing_tools:
        print("\nMissing required tools:")
        for tool in missing_tools:
            print(f"  - {tool}")
        print("\nPlease install the missing tools before continuing.")
        return False
    
    print("✓ All prerequisites are installed")
    return True


def main():
    """Main function to install all dependencies."""
    print("Installing dependencies for Pulumi monorepo...")
    
    # Check prerequisites first
    if not check_prerequisites():
        sys.exit(1)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    # Install package dependencies
    packages = [
        "packages/kind-cluster",
        "packages/grafana-helm", 
        "packages/metrics-server-helm",
        "utilities"
    ]
    
    for package in packages:
        print(f"\nInstalling {package} package dependencies...")
        if not run_command("pip install -e .", cwd=package):
            print(f"Failed to install dependencies for {package}")
            sys.exit(1)
    
    # Install environment dependencies
    environments = ["nonprod", "prod"]
    
    for env in environments:
        print(f"\nInstalling {env} environment dependencies...")
        if not run_command("pip install -r requirements.txt", cwd=env):
            print(f"Failed to install dependencies for {env}")
            sys.exit(1)
    
    print("\nAll dependencies installed successfully!")
    print("\nNext steps:")
    print("1. MANUALLY run: cd nonprod && pulumi up")
    print("2. MANUALLY run: cd prod && pulumi up")
    print("3. Access Grafana at http://localhost:30000 (admin/admin123 for nonprod)")
    print("\nIMPORTANT: Project deployment must be done MANUALLY!")


if __name__ == "__main__":
    main()