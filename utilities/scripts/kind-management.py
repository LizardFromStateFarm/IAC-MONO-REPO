#!/usr/bin/env python3
"""
Kind cluster management script
Usage: python kind-management.py [create|delete|list] [cluster-name]
"""

import subprocess
import sys
import json
from typing import List, Dict, Any


def run_command(command: str) -> tuple[bool, str, str]:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def list_clusters() -> List[Dict[str, Any]]:
    """List all Kind clusters."""
    success, stdout, stderr = run_command("kind get clusters")
    if not success:
        print(f"Error listing clusters: {stderr}")
        return []
    
    clusters = []
    for cluster_name in stdout.strip().split('\n'):
        if cluster_name:
            # Get cluster info
            success, info_stdout, info_stderr = run_command(f"kind get kubeconfig --name {cluster_name}")
            if success:
                clusters.append({
                    "name": cluster_name,
                    "kubeconfig": info_stdout.strip()
                })
    
    return clusters


def create_cluster(name: str, config: Dict[str, Any] = None) -> bool:
    """Create a Kind cluster."""
    if config:
        # Create config file
        config_file = f"/tmp/kind-config-{name}.yaml"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        command = f"kind create cluster --name {name} --config {config_file}"
    else:
        command = f"kind create cluster --name {name}"
    
    success, stdout, stderr = run_command(command)
    if success:
        print(f"✓ Created cluster: {name}")
        return True
    else:
        print(f"✗ Failed to create cluster: {stderr}")
        return False


def delete_cluster(name: str) -> bool:
    """Delete a Kind cluster."""
    success, stdout, stderr = run_command(f"kind delete cluster --name {name}")
    if success:
        print(f"✓ Deleted cluster: {name}")
        return True
    else:
        print(f"✗ Failed to delete cluster: {stderr}")
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python kind-management.py [create|delete|list] [cluster-name]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "list":
        clusters = list_clusters()
        if clusters:
            print("Available Kind clusters:")
            for cluster in clusters:
                print(f"  - {cluster['name']}")
        else:
            print("No Kind clusters found")
    
    elif action == "create":
        if len(sys.argv) < 3:
            print("Usage: python kind-management.py create <cluster-name>")
            sys.exit(1)
        
        cluster_name = sys.argv[2]
        
        # Default configuration
        config = {
            "kind": "Cluster",
            "apiVersion": "kind.x-k8s.io/v1alpha4",
            "name": cluster_name,
            "nodes": [
                {
                    "role": "control-plane",
                    "image": "kindest/node:v1.28.0",
                    "extraPortMappings": [
                        {"containerPort": 30000, "hostPort": 30000, "protocol": "TCP"},
                        {"containerPort": 30001, "hostPort": 30001, "protocol": "TCP"},
                    ]
                }
            ]
        }
        
        create_cluster(cluster_name, config)
    
    elif action == "delete":
        if len(sys.argv) < 3:
            print("Usage: python kind-management.py delete <cluster-name>")
            sys.exit(1)
        
        cluster_name = sys.argv[2]
        delete_cluster(cluster_name)
    
    else:
        print(f"Unknown action: {action}")
        print("Available actions: create, delete, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
