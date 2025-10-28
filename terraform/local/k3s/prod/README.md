# K3s Production Environment (Terraform)

This directory contains separate Terraform configurations for each component in the production environment.

## Structure

```
prod/
├── cluster/              # K3s cluster management
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── metrics-server/       # Metrics server deployment
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── deploy.ps1           # Deployment script
└── README.md
```

## Deployment Order

**Important**: Deploy the configurations in the correct order:

1. **Cluster First**: Deploy the cluster configuration to create the K3s cluster
2. **Metrics Server Second**: Deploy the metrics server configuration to add monitoring

## Quick Start

### 1. Deploy K3s Cluster

```bash
cd cluster

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy cluster
terraform apply
```

### 2. Deploy Metrics Server

```bash
cd ../metrics-server

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy metrics server
terraform apply
```

## Configuration Dependencies

- **metrics-server** depends on **cluster** (needs kubeconfig via remote state)
- **cluster** is independent and can be deployed first

## State Management

- **Local State**: Each component uses local state files
- **Remote State**: Metrics server reads cluster state via `terraform_remote_state`
- **Isolation**: Separate state per component

## Production Considerations

- **Higher Resources**: 4Gi memory per node, 2 worker nodes
- **Remote State**: Consider using remote state backends (S3, GCS) for production
- **State Locking**: Use state locking to prevent concurrent modifications
- **Backup**: Regular state file backups

## Verification

After both configurations are deployed:

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

## Configuration Options

### Cluster Configuration

- `cluster_name`: Name of the K3s cluster (default: k3s-prod)
- `kubernetes_version`: Kubernetes version (default: v1.28.0)
- `nodes`: Number of control plane nodes (default: 1)
- `worker_nodes`: Number of worker nodes (default: 2)
- `node_memory`: Memory per node (default: 4Gi)
- `total_memory_limit`: Total cluster memory (default: 8Gi)

### Metrics Server Configuration

- `namespace`: Namespace for deployment (default: kube-system)
- `replicas`: Number of replicas (default: 1)
- `image`: Metrics server image (default: registry.k8s.io/metrics-server/metrics-server:v0.6.4)
- `kubelet_insecure_tls`: Use insecure TLS for kubelet (default: true)

## Production Best Practices

1. **Remote State**: Use S3, GCS, or Terraform Cloud for state storage
2. **State Locking**: Enable state locking to prevent conflicts
3. **Backup**: Regular state file backups
4. **Monitoring**: Set up monitoring and alerting
5. **Security**: Use least privilege access patterns

## Benefits of This Structure

- **Separate State**: Each component has its own Terraform state
- **Independent Management**: Deploy/update components independently
- **Clear Dependencies**: Explicit state references between components
- **Production Ready**: Higher resource allocation and best practices
- **Scalable**: Easy to add more components (ingress, monitoring, etc.)

## Troubleshooting

### Common Issues

1. **State not found**: Ensure cluster is deployed before metrics server
2. **Podman not detected**: Check Podman installation and PATH
3. **K3s not found**: Install K3s CLI
4. **kubectl not configured**: Check kubeconfig path
5. **State conflicts**: Use state locking in production

### Debug Commands

```bash
# Check Terraform state
terraform state list
terraform state show <resource>

# Check cluster status
k3s kubectl get nodes

# Check metrics server
kubectl get pods -n kube-system | grep metrics-server
```
