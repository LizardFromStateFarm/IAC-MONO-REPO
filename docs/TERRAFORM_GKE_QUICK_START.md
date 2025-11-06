# Terraform GKE Quick Start Guide

## 🚀 **Getting Started Checklist**

### **1. Prerequisites Setup**
```bash
# Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable iam.googleapis.com
```

### **2. Create Directory Structure**
```bash
mkdir -p terraform/gcp/gke/{modules/{gke-cluster,metrics-server,networking},nonprod/{cluster,metrics-server},prod/{cluster,metrics-server}}
```

### **3. Start with Networking Module**
Create `terraform/gcp/gke/modules/networking/main.tf`:
```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

resource "google_compute_network" "vpc" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
  routing_mode           = "REGIONAL"
}

resource "google_compute_subnetwork" "private" {
  name          = "${var.vpc_name}-private"
  ip_cidr_range = var.private_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_compute_subnetwork" "public" {
  name          = "${var.vpc_name}-public"
  ip_cidr_range = var.public_subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
}
```

### **4. Key GCP Resources to Learn**

| Resource | Purpose | Key Attributes |
|----------|---------|----------------|
| `google_compute_network` | VPC Network | `name`, `auto_create_subnetworks` |
| `google_compute_subnetwork` | Subnets | `ip_cidr_range`, `region` |
| `google_container_cluster` | GKE Cluster | `name`, `location`, `node_config` |
| `google_container_node_pool` | Node Pools | `cluster`, `node_config` |
| `google_compute_router` | NAT Gateway | `name`, `region`, `network` |

### **5. Essential Variables Pattern**
```hcl
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["nonprod", "prod"], var.environment)
    error_message = "Environment must be 'nonprod' or 'prod'."
  }
}
```

### **6. State Management Pattern**
```hcl
# In metrics-server/main.tf
data "terraform_remote_state" "cluster" {
  backend = "local"
  config = {
    path = "../cluster/terraform.tfstate"
  }
}

# Use the cluster's kubeconfig
provider "kubernetes" {
  config_path = data.terraform_remote_state.cluster.outputs.kubeconfig_path
}
```

### **7. Deployment Order**
1. **Networking** (if separate)
2. **Cluster** (depends on networking)
3. **Metrics Server** (depends on cluster)

### **8. Testing Commands**
```bash
# Validate Terraform
terraform validate

# Plan deployment
terraform plan

# Apply changes
terraform apply

# Check GKE cluster
gcloud container clusters list

# Get kubeconfig
gcloud container clusters get-credentials CLUSTER_NAME --region REGION
```

### **9. Cost Management**
- Use `e2-medium` instances for nonprod
- Use `e2-standard-2` for prod
- Enable cluster autoscaling
- Set up billing alerts

### **10. Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| "Project not found" | Check `gcloud config get-value project` |
| "Permission denied" | Run `gcloud auth application-default login` |
| "API not enabled" | Enable required APIs in GCP Console |
| "Quota exceeded" | Check GCP quotas and limits |

## 📚 **Reference Links**

- [GKE Terraform Examples](https://github.com/terraform-google-modules/terraform-google-kubernetes-engine)
- [GCP Terraform Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

## 🎯 **Success Milestones**

- [ ] Can create VPC and subnets
- [ ] Can deploy GKE cluster
- [ ] Can deploy metrics server
- [ ] Can access cluster with kubectl
- [ ] Can destroy all resources cleanly

Remember: Start simple, test frequently, and build up complexity gradually!
