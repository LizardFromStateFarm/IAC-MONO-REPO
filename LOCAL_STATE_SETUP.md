# Local State Setup for Pulumi

This project is configured to use **local state files only** - no cloud storage. Each tool in each environment has its own separate state file to prevent conflicts when multiple developers work on different tools simultaneously.

## State File Structure

Each tool maintains its own local state file:

```
prod/
├── kind-cluster/
│   ├── state/
│   │   ├── prod-kind-cluster.json          # State file
│   │   └── prod-kind-cluster-secrets.json  # Secrets file
│   ├── init-local.ps1                      # PowerShell init script
│   └── init-local.bat                      # Batch init script
├── grafana/
│   ├── state/
│   │   ├── prod-grafana.json
│   │   └── prod-grafana-secrets.json
│   ├── init-local.ps1
│   └── init-local.bat
└── metrics-server/
    ├── state/
    │   ├── prod-metrics-server.json
    │   └── prod-metrics-server-secrets.json
    ├── init-local.ps1
    └── init-local.bat

nonprod/
├── kind-cluster/
│   ├── state/
│   │   ├── nonprod-kind-cluster.json
│   │   └── nonprod-kind-cluster-secrets.json
│   ├── init-local.ps1
│   └── init-local.bat
├── grafana/
│   ├── state/
│   │   ├── nonprod-grafana.json
│   │   └── nonprod-grafana-secrets.json
│   ├── init-local.ps1
│   └── init-local.bat
└── metrics-server/
    ├── state/
    │   ├── nonprod-metrics-server.json
    │   └── nonprod-metrics-server-secrets.json
    ├── init-local.ps1
    └── init-local.bat
```

## Quick Setup

### Option 1: Initialize All Tools at Once
```powershell
# PowerShell
.\init-all-local.ps1

# Command Prompt
init-all-local.bat
```

### Option 2: Initialize Individual Tools
```powershell
# Navigate to specific tool directory
cd prod\kind-cluster

# Run initialization script
.\init-local.ps1
```

## Benefits of This Setup

1. **No Cloud Dependencies**: All state is stored locally
2. **Separate State Files**: Each tool has its own state, preventing conflicts
3. **Parallel Development**: Multiple developers can work on different tools simultaneously
4. **Environment Isolation**: Prod and nonprod are completely separate
5. **Offline Capable**: Works without internet connection

## Working with Tools

After initialization, you can work with each tool independently:

```powershell
# Navigate to tool directory
cd prod\grafana

# Deploy
pulumi up

# Check status
pulumi stack ls

# View outputs
pulumi stack output
```

## State File Locations

- **prod/kind-cluster**: `prod/kind-cluster/state/prod-kind-cluster.json`
- **prod/grafana**: `prod/grafana/state/prod-grafana.json`
- **prod/metrics-server**: `prod/metrics-server/state/prod-metrics-server.json`
- **nonprod/kind-cluster**: `nonprod/kind-cluster/state/nonprod-kind-cluster.json`
- **nonprod/grafana**: `nonprod/grafana/state/nonprod-grafana.json`
- **nonprod/metrics-server**: `nonprod/metrics-server/state/nonprod-metrics-server.json`

## Cloud Disabled

The `disable-cloud.ps1` script ensures that:
- Pulumi Cloud is completely disabled
- All state is stored locally
- No accidental cloud uploads can occur

## Troubleshooting

If you encounter cloud-related issues:
1. Run `.\disable-cloud.ps1` to force local state
2. Check that each tool directory has its own `state/` folder
3. Verify no cloud URLs are in the configuration
