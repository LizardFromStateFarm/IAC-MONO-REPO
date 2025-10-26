import pulumi
import sys
import os

# Add the packages directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'kind-cluster'))

from kind_cluster import KindCluster, KindClusterConfig

# Get environment from Pulumi config or default to nonprod
config = pulumi.Config()
environment = config.get("environment") or "nonprod"

# Load configuration from environment-specific config file
cluster_config = KindClusterConfig.from_environment(environment)

# Create Kind cluster
cluster = KindCluster("nonprod-cluster", cluster_config)

# Export important values
pulumi.export("clusterName", cluster.cluster_name)
pulumi.export("kubeconfig", cluster.get_kubeconfig())
pulumi.export("clusterReady", cluster.ready)
