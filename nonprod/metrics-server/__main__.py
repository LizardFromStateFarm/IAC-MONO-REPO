import pulumi
import pulumi_kubernetes as k8s
import sys
import os

# Add the packages directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'metrics-server-simple'))

from metrics_server_simple import MetricsServerSimple, MetricsServerSimpleConfig

# Get environment from Pulumi config or default to nonprod
config = pulumi.Config()
environment = config.get("environment") or "nonprod"

# Get kubeconfig from Kind cluster stack
# Using local stack reference since we're using local state
kind_stack = pulumi.StackReference("kind-cluster", stack_name="nonprod")
kubeconfig = kind_stack.get_output("kubeconfig")

# Create Kubernetes provider using the Kind cluster kubeconfig
k8s_provider = k8s.Provider("metrics-server-provider", kubeconfig=kubeconfig)

# Create metrics server config using simple approach
metrics_config = MetricsServerSimpleConfig(
    namespace="kube-system",
    replicas=1,
    kubelet_insecure_tls=True  # Required for Kind clusters
)

# Deploy metrics server using simple approach
metrics_server = MetricsServerSimple("nonprod-metrics-server", metrics_config, opts=pulumi.ResourceOptions(provider=k8s_provider))

# Export important values
pulumi.export("metricsServerReady", metrics_server.is_ready())
