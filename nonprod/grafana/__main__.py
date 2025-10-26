import pulumi
import pulumi_kubernetes as k8s
import sys
import os

# Add the packages directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'grafana-helm'))

from grafana_helm import GrafanaHelm, GrafanaHelmConfig

# Get environment from Pulumi config or default to nonprod
config = pulumi.Config()
environment = config.get("environment") or "nonprod"

# Get kubeconfig from Kind cluster stack
kind_stack = pulumi.StackReference("kind-cluster", stack_name="nonprod/kind-cluster")
kubeconfig = kind_stack.get_output("kubeconfig")

# Create Kubernetes provider using the Kind cluster kubeconfig
k8s_provider = k8s.Provider("grafana-provider", kubeconfig=kubeconfig)

# Load configuration from environment-specific config file
grafana_config = GrafanaHelmConfig.from_environment(environment)

# Deploy Grafana
grafana = GrafanaHelm("nonprod-grafana", grafana_config, opts=pulumi.ResourceOptions(provider=k8s_provider))

# Export important values
pulumi.export("grafanaUrl", grafana.get_service_url())
pulumi.export("grafanaAdminPassword", grafana.admin_password)
