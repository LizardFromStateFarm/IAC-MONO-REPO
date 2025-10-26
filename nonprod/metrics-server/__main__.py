import pulumi
import pulumi_kubernetes as k8s
import sys
import os

# Add the packages directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'metrics-server-helm'))

from metrics_server_helm import MetricsServerHelm, MetricsServerHelmConfig

# Get environment from Pulumi config or default to nonprod
config = pulumi.Config()
environment = config.get("environment") or "nonprod"

# Get kubeconfig from Kind cluster stack
kind_stack = pulumi.StackReference("kind-cluster", stack_name="nonprod/kind-cluster")
kubeconfig = kind_stack.get_output("kubeconfig")

# Create Kubernetes provider using the Kind cluster kubeconfig
k8s_provider = k8s.Provider("metrics-server-provider", kubeconfig=kubeconfig)

# Load configuration from environment-specific config file
metrics_config = MetricsServerHelmConfig.from_environment(environment)

# Deploy metrics server
metrics_server = MetricsServerHelm("nonprod-metrics-server", metrics_config, opts=pulumi.ResourceOptions(provider=k8s_provider))

# Export important values
pulumi.export("metricsServerReady", metrics_server.is_ready())
