# Pulumi Infrastructure Examples

This directory contains Pulumi infrastructure-as-code examples for different environments and cloud providers.

## Structure

```
pulumi/
├── local/
│   ├── kind/           # Local Kind cluster examples
│   └── k3s/            # Local K3s cluster examples (Podman)
├── aws/eks/            # AWS EKS cluster examples
├── gcp/gke/            # GCP GKE cluster examples
├── packages/           # Reusable Pulumi packages
├── utilities/          # Common utilities and scripts
└── examples/           # Additional examples
```

## Local Development

### K3s with Podman (Recommended)

The `local/k3s/` directory contains examples for local Kubernetes development using K3s with Podman as the container runtime.

**Features:**
- K3s cluster management with Podman
- Better performance than Docker Desktop
- Environment-specific configurations (nonprod/prod)
- Configurable resource allocation
- Port mapping for host access

**Quick Start:**
```bash
# Deploy nonprod environment
cd local/k3s/nonprod
pip install -r requirements.txt
pulumi stack init nonprod
pulumi up

# Deploy prod environment
cd local/k3s/prod
pip install -r requirements.txt
pulumi stack init prod
pulumi up
```

### Kind with Docker

The `local/kind/` directory contains examples for local Kubernetes development using Kind (Kubernetes in Docker).

**Features:**
- Kind cluster management
- Grafana monitoring
- Metrics server deployment
- Environment-specific configurations (nonprod/prod)

**Quick Start:**
```bash
# Install dependencies
python utilities/scripts/install-dependencies.py

# Deploy nonprod environment
cd local/kind/nonprod
pulumi stack init nonprod
pulumi up

# Deploy prod environment
cd local/kind/prod
pulumi stack init prod
pulumi up
```

## Cloud Providers

### AWS EKS

The `aws/eks/` directory contains examples for deploying Kubernetes clusters on AWS using EKS.

**Features:**
- VPC and networking setup
- EKS cluster creation
- Node group management
- Security groups and IAM roles

**Usage:**
```bash
cd aws/eks
pulumi stack init dev
pulumi config set aws:region us-west-2
pulumi up
```

### GCP GKE

The `gcp/gke/` directory contains examples for deploying Kubernetes clusters on GCP using GKE.

**Features:**
- VPC network creation
- GKE cluster setup
- Node pool configuration
- Private cluster options

**Usage:**
```bash
cd gcp/gke
pulumi stack init dev
pulumi config set gcp:project your-project-id
pulumi up
```

## Packages

The `packages/` directory contains reusable Pulumi components:

- **k3s-cluster**: K3s cluster management with Podman support
- **kind-cluster**: Kind cluster management
- **grafana-helm**: Grafana deployment via Helm
- **metrics-server-helm**: Metrics server deployment via Helm
- **metrics-server-simple**: Simple metrics server deployment

## Utilities

The `utilities/` directory contains helper scripts and common utilities:

- **common_utilities.py**: Shared utility functions
- **helm_utilities.py**: Helm-specific utilities
- **scripts/**: Helper scripts for dependency management

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
- [Python](https://www.python.org/) (3.8 or later)
- [Podman](https://podman.io/) (for K3s clusters - recommended)
- [Docker](https://www.docker.com/) (for Kind clusters - fallback)
- [K3s](https://k3s.io/) (for local K3s development)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) (for local Kind development)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Cloud provider CLI tools (AWS CLI, gcloud CLI)

## Configuration

Each environment and cloud provider has its own configuration files:

- **Local**: `Pulumi.{env}.yaml` files
- **AWS**: Requires AWS credentials and region configuration
- **GCP**: Requires GCP project ID and credentials

## Examples

The `examples/` directory contains additional examples and templates for common use cases.
