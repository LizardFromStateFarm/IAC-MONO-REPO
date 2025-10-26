# Pulumi Kind Monorepo (Python)

This is a Pulumi monorepo project that manages Kind (Kubernetes in Docker) environments (nonprod and prod) with Grafana and Kubernetes metrics server deployments, all written in Python.

## Why Kind Instead of Minikube?

**Kind (Kubernetes in Docker)** is much better suited for Pulumi workflows because:

- ✅ **Pulumi can manage Kind clusters** - Kind clusters can be created and managed directly through Pulumi using the `pulumi-command` provider
- ✅ **Docker-based** - Uses Docker containers, making it more consistent across platforms
- ✅ **Faster startup** - Kind clusters start much faster than minikube
- ✅ **Better resource usage** - More efficient resource usage compared to minikube
- ✅ **Kubectl contexts** - Works seamlessly with kubectl contexts
- ✅ **Production-like** - More similar to production Kubernetes environments

## Project Structure

```
├── packages/                    # Reusable Pulumi packages (Python)
│   ├── kind-cluster/           # Kind cluster management
│   ├── grafana-helm/           # Grafana Helm chart deployment
│   └── metrics-server-helm/    # Kubernetes metrics server Helm deployment
├── nonprod/                    # Non-production environment
├── prod/                       # Production environment
└── utilities/                  # Common utilities and scripts (Python)
```

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
- [Python](https://www.python.org/) (3.8 or later)
- [Docker](https://www.docker.com/) (for Kind clusters)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) (Kubernetes in Docker)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Quick Start

1. **Install dependencies:**
   ```powershell
   python utilities/scripts/install-dependencies.py
   ```

2. **Deploy environments (MANUALLY):**
   ```powershell
   # Deploy nonprod (creates Kind cluster automatically)
   cd nonprod
   pulumi stack init nonprod
   pulumi up
   
   # Deploy prod (creates Kind cluster automatically)
   cd ../prod
   pulumi stack init prod
   pulumi up
   ```

3. **Access services:**
   - **Grafana:** http://localhost:30000 (admin/admin123 for nonprod, admin/prod-admin-2024! for prod)
   - **Kubectl:** `kubectl config use-context nonprod-kind` or `kubectl config use-context prod-kind`

## Packages

### Kind Cluster Package (`packages/kind-cluster/`)
Manages Kind cluster lifecycle and configuration using Pulumi's command provider.

**Features:**
- Cluster creation and management through Pulumi
- Kubeconfig generation and management
- Port mapping configuration
- Multi-node cluster support
- Python dataclasses for configuration

### Grafana Helm Package (`packages/grafana-helm/`)
Deploys Grafana using Helm charts.

**Features:**
- Grafana deployment with Helm
- Configurable persistence
- NodePort service configuration
- Admin password management
- Python dataclasses for configuration

### Metrics Server Helm Package (`packages/metrics-server-helm/`)
Deploys Kubernetes metrics server using Helm charts.

**Features:**
- Metrics server deployment
- Configurable arguments
- Resource limits and requests
- High availability support
- Python dataclasses for configuration

## Environments

### Nonprod Environment
- **Cluster:** 1 control plane node, 0 worker nodes
- **Grafana:** Single replica, 10Gi storage, accessible at localhost:30000
- **Metrics Server:** Single replica

### Prod Environment
- **Cluster:** 1 control plane node, 1 worker node
- **Grafana:** 2 replicas, 50Gi storage, accessible at localhost:30000
- **Metrics Server:** 2 replicas

## Usage

### Deploying to Nonprod
```powershell
cd nonprod
pulumi stack select nonprod
pulumi up
```

### Deploying to Prod
```powershell
cd prod
pulumi stack select prod
pulumi up
```

### Accessing Services

After deployment, you can access services:

- **Grafana:** http://localhost:30000
- **Admin Password:** Check the exported `grafanaAdminPassword` from Pulumi outputs
- **Kubectl Context:** Use `kubectl config use-context <cluster-name>`

### Managing Kind Clusters

```powershell
# List all Kind clusters
python utilities/scripts/kind-management.py list

# Create a Kind cluster manually
python utilities/scripts/kind-management.py create my-cluster

# Delete a Kind cluster
python utilities/scripts/kind-management.py delete my-cluster

# Switch kubectl context
kubectl config use-context nonprod-kind
kubectl config use-context prod-kind
```

## Configuration

### Environment-specific Configuration

Each environment has its own configuration file:
- `nonprod/Pulumi.nonprod.yaml`
- `prod/Pulumi.prod.yaml`

### Customizing Deployments

You can customize deployments by modifying the configuration in each environment's `__main__.py` file or by updating the Pulumi configuration files.

## Python Packages

All packages are Python packages with `setup.py` files and can be installed using pip:

```powershell
# Install a specific package
pip install -e packages/kind-cluster

# Install all packages
pip install -e packages/kind-cluster
pip install -e packages/grafana-helm
pip install -e packages/metrics-server-helm
pip install -e utilities
```

## Utilities

The `utilities/` directory contains:
- Common utilities and helper functions (Python classes)
- Kind cluster management scripts (Python)
- Environment configuration helpers

### Python Scripts

- `utilities/scripts/install-dependencies.py` - Install all dependencies and check prerequisites
- `utilities/scripts/kind-management.py` - Manage Kind clusters (create, delete, list)

## Troubleshooting

### Common Issues

1. **Kind not starting:** Ensure Docker is running and you have sufficient resources
2. **Helm charts failing:** Check that the cluster is running and accessible
3. **Resource limits:** Adjust memory and CPU settings in the configuration files
4. **Python dependencies:** Ensure all packages are installed with `pip install -e .`
5. **Port conflicts:** Ensure ports 30000-30001 are available

### Useful Commands

```powershell
# Check Kind clusters
kind get clusters

# Check kubectl context
kubectl config current-context

# List all resources in a namespace
kubectl get all -n <namespace>

# Check logs
kubectl logs -n <namespace> <pod-name>

# Install Python dependencies
pip install -r requirements.txt

# Check Docker status
docker ps
```

## Development

### Adding New Packages

1. Create a new directory in `packages/`
2. Add `setup.py`, `__init__.py`, and implementation files
3. Update environment dependencies in `requirements.txt`

### Modifying Existing Packages

1. Make changes to the package
2. Reinstall the package: `pip install -e .`
3. Update the environment that uses the package

### Python Virtual Environments

Each environment uses its own virtual environment:
- `nonprod/venv/`
- `prod/venv/`

## Alternative Local Kubernetes Options

If you prefer other local Kubernetes solutions:

1. **Minikube** - Traditional local Kubernetes (requires manual cluster management)
2. **K3s** - Lightweight Kubernetes (good for edge computing)
3. **MicroK8s** - Ubuntu's lightweight Kubernetes
4. **Docker Desktop Kubernetes** - Built into Docker Desktop

However, **Kind is recommended** for Pulumi workflows because it can be managed directly through Pulumi.

## License

MIT License - see LICENSE file for details.