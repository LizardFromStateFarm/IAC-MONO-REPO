# Pulumi Infrastructure Repository Summary
**AI AGENT REFERENCE DOCUMENT**

## Overview
This repository contains Pulumi infrastructure-as-code configurations for deploying Kubernetes clusters using Kind (Kubernetes in Docker) and associated services including metrics-server and Grafana monitoring. This document is specifically designed for AI agents to understand the codebase structure, patterns, and troubleshooting approaches.

## Repository Structure

### Root Directory
- **Configuration Scripts**: `init-all-local.bat/ps1`, `disable-cloud.bat/ps1`
- **Documentation**: `README.md`, `LOCAL_STATE_SETUP.md`, `STACK_STRUCTURE.md`
- **Examples**: `examples/stack_creation_example.py`

### Packages Directory (`packages/`)
Reusable Pulumi components for different services:

#### `kind-cluster/`
- **Purpose**: Creates and manages Kind Kubernetes clusters
- **Key Files**:
  - `kind_cluster.py`: Main KindCluster class implementation
  - `configs/nonprod.yaml`, `configs/prod.yaml`: Environment-specific configurations
- **Configuration**:
  - Default: 1 control plane + 1 worker node (2 total)
  - Memory: 2Gi per node, 4Gi total cluster limit
  - Kubernetes version: v1.28.0
  - Port mappings: 30000, 30001 (TCP)

#### `metrics-server-simple/`
- **Purpose**: Deploys metrics-server using native Kubernetes manifests
- **Key Files**:
  - `metrics_server_simple.py`: MetricsServerSimple class implementation
- **Features**:
  - Self-signed certificates with writable /tmp directory
  - Kind-optimized configuration with `--kubelet-insecure-tls`
  - HTTP health checks (not HTTPS) for Kind compatibility
  - RBAC permissions for metrics.k8s.io API group
  - Resource limits: 100m CPU, 100Mi memory (requests), 200m CPU, 200Mi memory (limits)

#### `metrics-server-helm/`
- **Purpose**: Alternative metrics-server deployment using Helm charts
- **Key Files**:
  - `metrics_server_helm.py`: MetricsServerHelm class implementation
  - `configs/nonprod.yaml`, `configs/prod.yaml`: Helm-specific configurations
- **Configuration**:
  - Chart version: 3.10.0
  - Kind-optimized with insecure TLS settings

#### `grafana-helm/`
- **Purpose**: Grafana monitoring deployment using Helm
- **Key Files**:
  - `grafana_helm.py`: GrafanaHelm class implementation
  - `configs/nonprod.yaml`, `configs/prod.yaml`: Grafana configurations

### Environment Directories

#### `nonprod/` and `prod/`
Each environment contains:
- **`kind-cluster/`**: Kind cluster deployment
- **`metrics-server/`**: Metrics server deployment
- **`grafana/`**: Grafana monitoring deployment
- **`venv/`**: Python virtual environment
- **`__main__.py`**: Main deployment scripts for each service
- **`init-local.bat/ps1`**: Local initialization scripts
- **`Pulumi.yaml`**: Pulumi project configuration
- **`Pulumi.{env}.yaml`**: Environment-specific configuration

### Utilities Directory (`utilities/`)
- **`common_utilities.py`**: Shared utility functions
- **`helm_utilities.py`**: Helm-specific utilities
- **`minikube_utilities.py`**: Minikube utilities
- **`scripts/`**: Helper scripts for dependency management and cluster operations

## Key Configuration Details

### Kind Cluster Configuration
```yaml
cluster_name: "nonprod-kind" / "prod-kind"
kubernetes_version: "v1.28.0"
worker_nodes: 1
nodes: 1
node_memory: "2Gi"
total_memory_limit: "4Gi"
port_mappings:
  - containerPort: 30000, hostPort: 30000
  - containerPort: 30001, hostPort: 30001
```

### Metrics Server Configuration
- **Image**: `registry.k8s.io/metrics-server/metrics-server:v0.6.4`
- **Namespace**: `kube-system`
- **Health Checks**: HTTP scheme (not HTTPS) for Kind compatibility
- **Key Arguments**:
  - `--kubelet-insecure-tls`: Required for Kind clusters
  - `--cert-dir=/tmp`: Self-signed certificates
  - `--metric-resolution=15s`: Metrics collection interval
- **RBAC**: Full permissions for metrics.k8s.io API group

### Recent Fixes Applied
1. **Metrics Server Rewrite**: Completely rewrote metrics-server-simple package to use official Kubernetes approach
2. **Kind-Specific Configuration**: Added --kubelet-insecure-tls flag and proper Kind cluster settings
3. **Helm Package Update**: Updated metrics-server-helm to use working approach by default
4. **RBAC Permissions**: Implemented comprehensive RBAC permissions for metrics collection
5. **Memory Configuration**: Added explicit memory limits to Kind cluster configs
6. **Deployment Simplification**: Simplified both nonprod and prod deployments for better reliability

## Deployment Workflow

### Local Development Setup
1. Run `init-all-local.bat/ps1` to initialize all local stacks
2. Deploy Kind cluster: `pulumi up` in `nonprod/kind-cluster/`
3. Deploy metrics server: `pulumi up` in `nonprod/metrics-server/`
4. Deploy Grafana: `pulumi up` in `nonprod/grafana/`

### Stack Dependencies
- Metrics server depends on Kind cluster (uses kubeconfig)
- Grafana depends on Kind cluster (uses kubeconfig)
- All stacks use local state management

## Common Issues and Solutions

### Metrics Server Issues
- **Health Check Failures**: Ensure HTTP scheme is used (not HTTPS)
- **RBAC Errors**: Verify metrics.k8s.io permissions are granted
- **Certificate Issues**: Ensure /tmp directory is writable
- **Kind Compatibility**: Use `--kubelet-insecure-tls` flag

### Kind Cluster Issues
- **Memory Constraints**: Check Docker Desktop resource limits
- **Port Conflicts**: Verify port mappings don't conflict with host
- **Node Startup**: Ensure sufficient resources for 2-node cluster

### General Troubleshooting
- Check Pulumi stack references are correct
- Verify kubeconfig is properly passed between stacks
- Ensure all dependencies are installed in virtual environments
- Check local state files are not corrupted

## Development Notes

### Adding New Services
1. Create package in `packages/` directory
2. Add environment-specific configs
3. Create deployment scripts in `nonprod/` and `prod/`
4. Update initialization scripts

### Configuration Management
- Environment-specific configs in `configs/` directories
- Use `from_environment()` class methods for loading configs
- Maintain consistency between nonprod and prod configurations

### State Management
- All stacks use local state (no cloud backend)
- Stack references use local stack names
- State files stored in `.pulumi/` directory

## File Locations Reference

### Critical Files
- **Kind Cluster**: `packages/kind-cluster/kind_cluster.py`
- **Metrics Server**: `packages/metrics-server-simple/metrics_server_simple.py`
- **Grafana**: `packages/grafana-helm/grafana_helm.py`
- **Nonprod Deployments**: `nonprod/*/__main__.py`
- **Prod Deployments**: `prod/*/__main__.py`

### Configuration Files
- **Kind Configs**: `packages/kind-cluster/configs/`
- **Metrics Configs**: `packages/metrics-server-helm/configs/`
- **Grafana Configs**: `packages/grafana-helm/configs/`

## AI Agent Specific Information

### Key Classes and Methods Reference

#### Core Component Classes
- **`KindCluster`** (`packages/kind-cluster/kind_cluster.py`):
  - `__init__(name, config, opts)`: Creates Kind cluster
  - `_create_kind_config(config)`: Generates Kind YAML config
  - `delete_cluster()`: Deletes cluster
  - `get_kubeconfig()`: Returns kubeconfig as Pulumi Output

- **`MetricsServerSimple`** (`packages/metrics-server-simple/metrics_server_simple.py`):
  - `__init__(name, config, opts)`: Deploys metrics server
  - `is_ready()`: Returns Pulumi Output[bool] for readiness check
  - Creates: ServiceAccount, ClusterRole, ClusterRoleBinding, Service, Deployment

- **`MetricsServerHelm`** (`packages/metrics-server-helm/metrics_server_helm.py`):
  - `__init__(name, config, opts)`: Deploys via Helm
  - Uses Helm chart version 3.10.0

- **`GrafanaHelm`** (`packages/grafana-helm/grafana_helm.py`):
  - `__init__(name, config, opts)`: Deploys Grafana via Helm

#### Configuration Classes
- **`KindClusterConfig`**: Dataclass with `from_environment(env)` method
- **`MetricsServerSimpleConfig`**: Basic metrics server configuration
- **`MetricsServerHelmConfig`**: Helm-specific configuration
- **`GrafanaHelmConfig`**: Grafana-specific configuration

#### Utility Classes
- **`CommonUtilities`** (`utilities/common_utilities.py`):
  - `get_common_labels(environment, component)`: Standard K8s labels
  - `get_environment_config(environment)`: Environment-specific configs
  - `create_namespace(name, namespace, labels, opts)`: Namespace creation
  - `get_resource_quota(...)`: Resource quota creation
  - `get_limit_range(...)`: Limit range creation

- **`HelmUtilities`** (`utilities/helm_utilities.py`):
  - `get_grafana_values(environment)`: Environment-specific Grafana values
  - `get_metrics_server_values(environment)`: Metrics server Helm values

### Common Patterns and Conventions

#### 1. Configuration Loading Pattern
```python
# All packages follow this pattern:
@classmethod
def from_environment(cls, environment: str) -> 'ConfigClass':
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(package_dir, 'package-name', 'configs', f'{environment}.yaml')
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    return cls(**config_data)
```

#### 2. Pulumi Component Resource Pattern
```python
class ComponentName(pulumi.ComponentResource):
    def __init__(self, name: str, config: ConfigClass, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("component-type", name, {}, opts)
        # Resource creation with parent=self
        # Export important outputs
```

#### 3. Stack Reference Pattern
```python
# Environment stacks reference kind-cluster
kind_stack = pulumi.StackReference("kind-cluster", stack_name="nonprod")
kubeconfig = kind_stack.get_output("kubeconfig")
k8s_provider = k8s.Provider("provider-name", kubeconfig=kubeconfig)
```

#### 4. Label Convention
```python
labels = {
    "app.kubernetes.io/name": component_name,
    "app.kubernetes.io/instance": f"{environment}-{component_name}",
    "app.kubernetes.io/version": "1.0.0",
    "app.kubernetes.io/component": component_name,
    "app.kubernetes.io/part-of": "minikube-stack",  # Note: Still references minikube
    "environment": environment,
}
```

### Dependencies and Requirements

#### Python Dependencies (All Packages)
- `pulumi>=3.0.0`
- `pulumi-kubernetes>=4.0.0`
- `pulumi-command>=0.0.0` (kind-cluster only)

#### System Prerequisites
- Python 3.8+
- Pulumi CLI
- Docker (for Kind)
- Kind CLI
- kubectl

### Critical Configuration Details for AI Agents

#### Kind Cluster Configuration
- **API Version**: `kind.x-k8s.io/v1alpha4`
- **Node Images**: `kindest/node:v1.28.0`
- **Memory Management**: Handled by Docker Desktop, not Kind config
- **Port Mappings**: 30000, 30001 (TCP) for service access
- **Health Checks**: Uses `kubectl wait --for=condition=Ready nodes`

#### Metrics Server Critical Settings
- **Image**: `registry.k8s.io/metrics-server/metrics-server:v0.6.4`
- **Health Checks**: HTTP scheme (NOT HTTPS) for Kind compatibility
- **Key Arguments**:
  - `--kubelet-insecure-tls`: Required for Kind
  - `--cert-dir=/tmp`: Self-signed certificates
  - `--metric-resolution=15s`
- **RBAC**: Must include `metrics.k8s.io` API group permissions
- **Security Context**: `read_only_root_filesystem=False` for certificate writing

#### Grafana Configuration
- **Nonprod**: Single replica, 10Gi storage, admin/admin123
- **Prod**: 2 replicas, 50Gi storage, admin/prod-admin-2024!
- **Service**: NodePort on port 30000
- **Access**: http://localhost:30000

### Common Issues and AI Troubleshooting Guide

#### 1. Metrics Server Health Check Failures
**Symptoms**: Pods stuck in CrashLoopBackOff, health check failures
**Root Causes**:
- HTTPS health checks with self-signed certificates
- Missing RBAC permissions for metrics.k8s.io
- Read-only filesystem preventing certificate generation
**AI Solution**: Check health check scheme is HTTP, verify RBAC includes metrics.k8s.io, ensure read_only_root_filesystem=False

#### 2. Kind Cluster Startup Issues
**Symptoms**: Cluster creation fails, nodes not ready
**Root Causes**:
- Docker Desktop resource limits too low
- Port conflicts with host system
- Kind configuration syntax errors
**AI Solution**: Check Docker Desktop memory/CPU limits, verify port mappings, validate Kind YAML syntax

#### 3. Stack Reference Failures
**Symptoms**: Pulumi stack reference errors, kubeconfig not found
**Root Causes**:
- Stack names don't match between environments
- Local state files corrupted
- Stack not deployed yet
**AI Solution**: Verify stack names match exactly, check .pulumi directory, ensure dependency stack is deployed first

#### 4. RBAC Permission Errors
**Symptoms**: ServiceAccount permission denied errors
**Root Causes**:
- Missing API group permissions
- Incorrect resource names in PolicyRule
- ClusterRoleBinding not properly linked
**AI Solution**: Check ClusterRole includes all required API groups, verify resource names match exactly, ensure ClusterRoleBinding references correct ClusterRole

### File Modification Patterns for AI Agents

#### Adding New RBAC Permissions
```python
# Add to ClusterRole rules list
k8s.rbac.v1.PolicyRuleArgs(
    api_groups=["api-group-name"],
    resources=["resource-name"],
    verbs=["get", "list", "watch"],  # As needed
),
```

#### Modifying Health Checks
```python
# For Kind clusters, always use HTTP
liveness_probe=k8s.core.v1.ProbeArgs(
    http_get=k8s.core.v1.HTTPGetActionArgs(
        path="/livez",
        port=4443,
        scheme="HTTP",  # NOT HTTPS for Kind
    ),
    initial_delay_seconds=20,
    period_seconds=10,
),
```

#### Adding New Environment Configuration
1. Create `configs/{environment}.yaml` in package directory
2. Add environment case to `from_environment()` method
3. Create environment directory structure
4. Add `Pulumi.{environment}.yaml` with environment variable

###  Management for AI Agents

#### Local State Structure
- **Location**: `.pulumi/` directory in project root
- **Stack Names**: `{environment}` (e.g., "nonprod", "prod")
- **Dependencies**: Use `pulumi.StackReference` for cross-stack references
- **State Files**: `.pulumi/stacks/{stack-name}/` contains state data

#### Stack Deployment Order
1. `kind-cluster` (foundation)
2. `metrics-server` (depends on kind-cluster)
3. `grafana` (depends on kind-cluster)

### AI Agent Quick Reference Commands

#### Check Cluster Status
```bash
kubectl get nodes
kubectl get pods -n kube-system
kubectl get svc -A
```

#### Check Metrics Server
```bash
kubectl get pods -n kube-system -l app.kubernetes.io/name=metrics-server
kubectl logs -n kube-system -l app.kubernetes.io/name=metrics-server
kubectl top nodes  # Should work if metrics server is healthy
```

#### Check Grafana
```bash
kubectl get pods -n default -l app.kubernetes.io/name=grafana
kubectl get svc -l app.kubernetes.io/name=grafana
```

#### Pulumi Commands
```bash
pulumi stack ls
pulumi stack select {environment}
pulumi up
pulumi destroy
pulumi refresh
```

This comprehensive reference should enable AI agents to effectively understand, troubleshoot, and modify this Pulumi infrastructure repository.
