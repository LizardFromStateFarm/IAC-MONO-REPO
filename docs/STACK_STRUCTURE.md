# Pulumi Stack Structure

This project is organized to allow multiple developers to work on different tools independently while maintaining environment separation. The architecture separates configuration from code, making it CI/CD pipeline friendly.

## Directory Structure

```
├── nonprod/                    # Non-production environment
│   ├── kind-cluster/          # Kind cluster stack (foundation)
│   │   ├── __main__.py        # Simple project file that loads env config
│   │   ├── Pulumi.yaml
│   │   └── Pulumi.nonprod.yaml # Only contains environment variable
│   ├── grafana/               # Grafana stack (depends on kind-cluster)
│   │   ├── __main__.py        # Simple project file that loads env config
│   │   ├── Pulumi.yaml
│   │   └── Pulumi.nonprod.yaml # Only contains environment variable
│   ├── metrics-server/        # Metrics Server stack (depends on kind-cluster)
│   │   ├── __main__.py        # Simple project file that loads env config
│   │   ├── Pulumi.yaml
│   │   └── Pulumi.nonprod.yaml # Only contains environment variable
│   └── venv/                  # Shared virtual environment
├── prod/                      # Production environment
│   ├── kind-cluster/          # Kind cluster stack (foundation)
│   ├── grafana/               # Grafana stack (depends on kind-cluster)
│   ├── metrics-server/        # Metrics Server stack (depends on kind-cluster)
│   └── venv/                  # Shared virtual environment
└── packages/                  # Shared Pulumi packages with environment configs
    ├── kind-cluster/
    │   ├── configs/           # Environment-specific configurations
    │   │   ├── nonprod.yaml
    │   │   └── prod.yaml
    │   └── kind_cluster.py    # Package code with config loading
    ├── grafana-helm/
    │   ├── configs/           # Environment-specific configurations
    │   │   ├── nonprod.yaml
    │   │   └── prod.yaml
    │   └── grafana_helm.py    # Package code with config loading
    └── metrics-server-helm/
        ├── configs/           # Environment-specific configurations
        │   ├── nonprod.yaml
        │   └── prod.yaml
        └── metrics_server_helm.py # Package code with config loading
```

## Deployment Order

### For Non-Production:
1. **Kind Cluster** (must be deployed first)
   ```bash
   cd nonprod/kind-cluster
   pulumi stack select nonprod/kind-cluster
   pulumi up
   ```

2. **Grafana** (depends on kind-cluster)
   ```bash
   cd nonprod/grafana
   pulumi stack select nonprod/grafana
   pulumi up
   ```

3. **Metrics Server** (depends on kind-cluster)
   ```bash
   cd nonprod/metrics-server
   pulumi stack select nonprod/metrics-server
   pulumi up
   ```

### For Production:
1. **Kind Cluster** (must be deployed first)
   ```bash
   cd prod/kind-cluster
   pulumi stack select prod/kind-cluster
   pulumi up
   ```

2. **Grafana** (depends on kind-cluster)
   ```bash
   cd prod/grafana
   pulumi stack select prod/grafana
   pulumi up
   ```

3. **Metrics Server** (depends on kind-cluster)
   ```bash
   cd prod/metrics-server
   pulumi stack select prod/metrics-server
   pulumi up
   ```

## Benefits

- **Independent Development**: Multiple developers can work on different tools simultaneously
- **Environment Separation**: Nonprod and prod environments are completely isolated
- **Dependency Management**: Each tool can reference the kind-cluster stack outputs
- **Scalability**: Easy to add new tools or environments
- **State Isolation**: Each tool has its own Pulumi state
- **CI/CD Friendly**: Environment configs are in packages, projects only specify environment
- **Version Management**: Easy to update package versions through CI/CD pipelines
- **Configuration Separation**: Environment-specific configs are separate from code

## Stack Dependencies

- `grafana` and `metrics-server` stacks depend on `kind-cluster` stack
- Each environment (nonprod/prod) is completely independent
- Tools within the same environment can reference each other's outputs

## Configuration Management

Each package contains environment-specific configuration files in the `configs/` directory:
- `nonprod.yaml` - Non-production environment settings
- `prod.yaml` - Production environment settings

Project files only need to specify the environment:
```yaml
config:
  package-name:environment: nonprod  # or prod
```

The package code automatically loads the appropriate configuration based on the environment variable.

## Adding New Tools

1. Create a new package in `packages/` with:
   - Package code (e.g., `tool_name.py`)
   - `configs/` directory with `nonprod.yaml` and `prod.yaml`
   - `from_environment()` class method in the config class
2. Create project directories under each environment folder
3. Create simple `__main__.py` that loads config using `from_environment()`
4. Create `Pulumi.yaml` and `Pulumi.{env}.yaml` files
5. Update this documentation

## Adding New Environments

1. Create a new environment directory (e.g., `staging/`)
2. Copy the tool structure from an existing environment
3. Add new config files (e.g., `staging.yaml`) to each package's `configs/` directory
4. Update project `Pulumi.{env}.yaml` files to use the new environment
5. Update this documentation

## CI/CD Pipeline Integration

This structure is designed for easy CI/CD integration:
- Package versions can be updated in `requirements.txt` or package references
- Environment configs are versioned with the packages
- Projects only need to specify which environment to use
- No hardcoded values in project files
