# K3s Local Cluster with Podman (Terraform)

This directory contains Terraform infrastructure-as-code for local Kubernetes clusters using K3s with Podman as the container runtime.

## Structure

```
terraform/local/k3s/
├── modules/              # Reusable Terraform modules
│   ├── k3s-cluster/     # K3s cluster module
│   └── metrics-server/  # Metrics server module
├── nonprod/             # Non-production environment
│   ├── cluster/         # K3s cluster management
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── metrics-server/  # Metrics server deployment
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── deploy.ps1       # Deployment script
│   └── README.md
├── prod/                # Production environment
│   ├── cluster/         # K3s cluster management
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── metrics-server/  # Metrics server deployment
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── deploy.ps1       # Deployment script
│   └── README.md
└── README.md
```

## Prerequisites

1. **Podman**: Install Podman Desktop or Podman CLI
   - Windows: Download from [Podman Desktop](https://podman-desktop.io/)
   - Linux: `sudo dnf install podman` or `sudo apt install podman`
   - macOS: `brew install podman`

2. **K3s**: Install K3s CLI
   - Download from [K3s releases](https://github.com/k3s-io/k3s/releases)
   - Or use: `curl -sfL https://get.k3s.io | sh -`

3. **Terraform**: Install Terraform CLI
   - Follow [Terraform installation guide](https://www.terraform.io/downloads)

4. **kubectl**: Install kubectl
   - Follow [kubectl installation guide](https://kubernetes.io/docs/tasks/tools/)

## Quick Start

### Option 1: Using Deployment Scripts (Recommended)

```powershell
# Deploy nonprod environment
cd terraform/local/k3s/nonprod
.\deploy.ps1

# Deploy prod environment
cd terraform/local/k3s/prod
.\deploy.ps1
```

### Option 2: Manual Deployment

```bash
# Nonprod - Deploy cluster first
cd terraform/local/k3s/nonprod/cluster
terraform init
terraform plan
terraform apply

# Nonprod - Deploy metrics server second
cd ../metrics-server
terraform init
terraform plan
terraform apply
```

## Key Differences from Pulumi

| Feature | Pulumi | Terraform |
|---------|--------|-----------|
| **State Management** | Pulumi Service/File | Local state files |
| **Dependencies** | Stack references | Remote state data sources |
| **Modules** | Python packages | Terraform modules |
| **Execution** | Python runtime | Terraform binary |
| **Configuration** | YAML + Python | HCL + variables |

## Module Structure

### K3s Cluster Module

- **Location**: `modules/k3s-cluster/`
- **Purpose**: Creates and manages K3s cluster
- **Features**: Podman detection, port mapping, resource configuration

### Metrics Server Module

- **Location**: `modules/metrics-server/`
- **Purpose**: Deploys metrics server to existing cluster
- **Features**: RBAC, service, deployment, API service

## Configuration

### Nonprod vs Prod Differences

| Setting | Nonprod | Prod |
|---------|---------|------|
| Control Plane | 1 node | 1 node |
| Worker Nodes | 1 node | 2 nodes |
| Memory per Node | 2Gi | 4Gi |
| Total Memory | 4Gi | 8Gi |

## State Management

- **Local State**: Each component uses local state files
- **Dependencies**: Metrics server reads cluster state via `terraform_remote_state`
- **Isolation**: Separate state per component and environment

## Verification

After deployment:

```bash
# Check cluster status
kubectl get nodes

# Check metrics server
kubectl get pods -n kube-system | grep metrics-server

# Test metrics
kubectl top nodes
kubectl top pods --all-namespaces
```

## Management Commands

```bash
# Update individual components
cd cluster && terraform apply
cd metrics-server && terraform apply

# Check state
terraform show
terraform output

# Destroy components (in reverse order)
cd metrics-server && terraform destroy
cd cluster && terraform destroy
```

## Benefits of This Structure

- **Separate State**: Each component has isolated Terraform state
- **Independent Management**: Update components independently
- **Clear Dependencies**: Explicit state references between components
- **Reusable Modules**: Modules can be used across environments
- **Terraform Native**: Uses standard Terraform patterns and practices

## Troubleshooting

### Common Issues

1. **Podman not detected**: Ensure Podman is in PATH
2. **K3s not found**: Install K3s CLI
3. **State conflicts**: Ensure proper deployment order
4. **kubectl not configured**: Check kubeconfig path

### Debug Commands

```bash
# Check Terraform state
terraform state list
terraform state show <resource>

# Check K3s status
k3s server --help
k3s kubectl get nodes

# Check Podman
podman --version
podman ps
```

## Comparison with Pulumi

This Terraform structure provides similar functionality to the Pulumi version but with some key differences:

**Advantages:**
- More familiar to Terraform users
- Standard Terraform patterns
- No Python runtime dependency
- Simpler module system

**Limitations:**
- Less flexible than Pulumi's Python integration
- More verbose configuration
- Limited programmatic capabilities
- State management is more manual

Both approaches achieve the same goal of separate state management and independent component deployment!
