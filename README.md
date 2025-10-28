# Infrastructure as Code Monorepo

This repository contains infrastructure-as-code examples and templates for both **Pulumi** and **Terraform**, supporting local development with Kind clusters and cloud providers (AWS EKS, GCP GKE).

## Repository Structure

```
├── pulumi/                    # Pulumi infrastructure examples
│   ├── local/kind/           # Local Kind cluster (nonprod/prod)
│   ├── aws/eks/              # AWS EKS cluster examples
│   ├── gcp/gke/              # GCP GKE cluster examples
│   ├── packages/             # Reusable Pulumi packages
│   ├── utilities/            # Common utilities and scripts
│   └── examples/             # Additional examples
├── terraform/                 # Terraform infrastructure examples
│   ├── local/kind/           # Local Kind cluster
│   ├── aws/eks/              # AWS EKS cluster examples
│   └── gcp/gke/              # GCP GKE cluster examples
└── docs/                     # Documentation
```

## Quick Start

### Local Development (Kind)

Both Pulumi and Terraform support local Kubernetes development using Kind clusters.

#### Pulumi (Python)
```bash
cd pulumi/local/kind/nonprod
pulumi stack init nonprod
pulumi up
```

#### Terraform
```bash
cd terraform/local/kind
terraform init
terraform apply
```

### Cloud Providers

#### AWS EKS
```bash
# Pulumi
cd pulumi/aws/eks
pulumi stack init dev
pulumi config set aws:region us-west-2
pulumi up

# Terraform
cd terraform/aws/eks
terraform init
terraform apply
```

#### GCP GKE
```bash
# Pulumi
cd pulumi/gcp/gke
pulumi stack init dev
pulumi config set gcp:project your-project-id
pulumi up

# Terraform
cd terraform/gcp/gke
terraform init
terraform apply
```

## Features

### Local Development
- **Kind Clusters**: Fast, Docker-based Kubernetes for local development
- **Grafana Monitoring**: Pre-configured Grafana dashboards
- **Metrics Server**: Kubernetes metrics collection
- **Environment Management**: Separate nonprod/prod configurations

### Cloud Providers
- **AWS EKS**: Managed Kubernetes on AWS
- **GCP GKE**: Managed Kubernetes on Google Cloud
- **Networking**: VPC, subnets, security groups
- **IAM/Security**: Proper role-based access control

### Infrastructure as Code
- **Pulumi**: Python-based, supports multiple languages
- **Terraform**: HCL-based, industry standard
- **Reusable Components**: Modular packages and modules
- **Best Practices**: Security, networking, and operational considerations

## Prerequisites

### Common
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker](https://www.docker.com/)

### Pulumi
- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
- [Python](https://www.python.org/) (3.8 or later)

### Terraform
- [Terraform](https://www.terraform.io/downloads.html) >= 1.0

### Local Development
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)

### Cloud Providers
- **AWS**: [AWS CLI](https://aws.amazon.com/cli/)
- **GCP**: [gcloud CLI](https://cloud.google.com/sdk/docs/install)

## Why This Structure?

### Monorepo Benefits
- **Single Source of Truth**: All infrastructure code in one place
- **Consistency**: Shared patterns and best practices
- **Easy Comparison**: Side-by-side Pulumi vs Terraform examples
- **Template Generation**: Easy to copy and customize for new projects

### Tool Comparison
- **Pulumi**: Better for complex logic, multiple languages, state management
- **Terraform**: Industry standard, extensive provider ecosystem, HCL simplicity

### Environment Separation
- **Local**: Kind clusters for development and testing
- **Cloud**: Production-ready managed Kubernetes services
- **Provider Agnostic**: Examples for both AWS and GCP

## Getting Started

1. **Choose your tool**: Pulumi or Terraform
2. **Select environment**: Local (Kind) or Cloud (AWS/GCP)
3. **Follow the README**: Each directory has detailed instructions
4. **Customize**: Modify configurations for your needs
5. **Deploy**: Follow the deployment instructions

## Documentation

- [Pulumi Examples](pulumi/README.md) - Detailed Pulumi documentation
- [Terraform Examples](terraform/README.md) - Detailed Terraform documentation
- [Local State Setup](LOCAL_STATE_SETUP.md) - Pulumi local state configuration
- [Stack Structure](STACK_STRUCTURE.md) - Understanding the stack architecture

## Contributing

This repository serves as a template and example collection. Feel free to:

1. **Fork** the repository
2. **Customize** for your specific needs
3. **Add** new examples or providers
4. **Improve** existing configurations
5. **Share** your improvements

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Documentation**: Check the README files in each directory for detailed instructions