# Terraform Infrastructure Examples

This directory contains Terraform infrastructure-as-code examples for different environments and cloud providers.

## Structure

```
terraform/
├── local/
│   └── k3s/            # Local K3s cluster examples (Podman)
├── aws/eks/            # AWS EKS cluster examples
└── gcp/gke/            # GCP GKE cluster examples
```

## Local Development

### K3s with Podman (Recommended)

The `local/k3s/` directory contains examples for local Kubernetes development using K3s with Podman as the container runtime.

**Features:**
- K3s cluster management with Podman
- Better performance than Docker Desktop
- Separate state management per component
- Metrics server integration
- Environment-specific configurations (nonprod/prod)

**Quick Start:**
```bash
# Deploy nonprod environment
cd local/k3s/nonprod
.\deploy.ps1

# Deploy prod environment
cd local/k3s/prod
.\deploy.ps1
```

### Kind with Docker (Legacy)

The `local/kind/` directory contains examples for local Kubernetes development using Kind (Kubernetes in Docker).

**Features:**
- Kind cluster creation and management
- Configurable node counts and resources
- Port mapping for service access
- Template-based configuration

**Quick Start:**
```bash
cd local/kind
terraform init
terraform plan
terraform apply
```

## Cloud Providers

### AWS EKS

The `aws/eks/` directory contains examples for deploying Kubernetes clusters on AWS using EKS.

**Features:**
- VPC and networking setup
- EKS cluster creation
- Node group management
- Security groups and IAM roles
- Public subnet configuration

**Usage:**
```bash
cd aws/eks
terraform init
terraform plan
terraform apply
```

**Configuration:**
- Set AWS region: `export AWS_DEFAULT_REGION=us-west-2`
- Configure AWS credentials via AWS CLI or environment variables

### GCP GKE

The `gcp/gke/` directory contains examples for deploying Kubernetes clusters on GCP using GKE.

**Features:**
- VPC network creation
- GKE cluster setup
- Node pool configuration
- Private cluster options
- Firewall rules

**Usage:**
```bash
cd gcp/gke
terraform init
terraform plan
terraform apply
```

**Configuration:**
- Set project ID: `export GOOGLE_PROJECT_ID=your-project-id`
- Configure GCP credentials via gcloud CLI or service account

## Prerequisites

### Common
- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

### Local Development
- [Podman](https://podman.io/) (for K3s clusters - recommended)
- [K3s](https://k3s.io/) (for local K3s development)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) (for local Kind development)
- [Docker](https://www.docker.com/) (for Kind clusters - fallback)

### AWS
- [AWS CLI](https://aws.amazon.com/cli/)
- AWS credentials configured

### GCP
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- GCP project and credentials configured

## Configuration

### Variables

Each directory contains a `variables.tf` file with configurable options:

- **Cluster name**: Customize cluster names
- **Node count**: Number of worker nodes
- **Instance types**: Machine types for worker nodes
- **Regions**: Cloud provider regions

### Environment Variables

- **AWS**: `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **GCP**: `GOOGLE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`

## Best Practices

1. **State Management**: Use remote state backends (S3, GCS) for production
2. **Secrets**: Use Terraform Cloud or external secret management
3. **Modules**: Consider using Terraform modules for reusable components
4. **Versioning**: Pin provider versions in `required_providers`
5. **Security**: Follow least privilege principles for IAM roles

## Examples

Each directory contains complete, working examples that can be customized for your specific needs. Start with the basic configurations and modify as required.
