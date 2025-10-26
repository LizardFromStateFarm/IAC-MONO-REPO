import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes import helm
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import yaml
import os


@dataclass
class MetricsServerHelmConfig:
    namespace: Optional[str] = "kube-system"
    chart_version: Optional[str] = "3.10.0"
    values: Optional[Dict[str, Any]] = None
    args: Optional[List[str]] = None
    host_network: Optional[bool] = False
    replicas: Optional[int] = 1

    @classmethod
    def from_environment(cls, environment: str) -> 'MetricsServerHelmConfig':
        """Load configuration from environment-specific YAML file."""
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(package_dir, 'metrics-server-helm', 'configs', f'{environment}.yaml')
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)


class MetricsServerHelm(pulumi.ComponentResource):
    def __init__(self, name: str, config: MetricsServerHelmConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("metrics-server:helm", name, {}, opts)
        
        namespace = config.namespace or "kube-system"
        
        # Create namespace if it's not kube-system
        self.namespace = None
        if namespace != "kube-system":
            self.namespace = k8s.core.v1.Namespace(
                f"{name}-namespace",
                metadata=k8s.meta.v1.ObjectMetaArgs(
                    name=namespace,
                    labels={
                        "app.kubernetes.io/name": "metrics-server",
                        "app.kubernetes.io/instance": name,
                    },
                ),
                opts=pulumi.ResourceOptions(parent=self)
            )
        
        # Default values for metrics-server
        default_values = {
            "args": config.args or [
                "--cert-dir=/tmp",
                "--secure-port=4443",
                "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                "--kubelet-use-node-status-port",
                "--metric-resolution=15s"
            ],
            "hostNetwork": config.host_network or False,
            "replicas": config.replicas or 1,
            "resources": {
                "requests": {
                    "memory": "100Mi",
                    "cpu": "100m",
                },
                "limits": {
                    "memory": "200Mi",
                    "cpu": "200m",
                },
            },
            "nodeSelector": {
                "kubernetes.io/os": "linux",
            },
            "tolerations": [
                {
                    "key": "node-role.kubernetes.io/control-plane",
                    "operator": "Exists",
                    "effect": "NoSchedule",
                },
                {
                    "key": "node-role.kubernetes.io/master",
                    "operator": "Exists",
                    "effect": "NoSchedule",
                },
            ],
        }
        
        # Merge with user-provided values
        values = {**default_values, **(config.values or {})}
        
        # Deploy metrics-server using Helm
        self.release = helm.v3.Release(
            f"{name}-metrics-server",
            chart="metrics-server",
            version=config.chart_version,
            repository_opts=helm.v3.RepositoryOptsArgs(
                repo="https://kubernetes-sigs.github.io/metrics-server/",
            ),
            namespace=namespace,
            values=values,
            create_namespace=False,  # We're handling namespace creation separately
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.namespace] if self.namespace else [],
            )
        )
        
        self.namespace_name = pulumi.Output.from_input(namespace)
        
        # Get the deployment
        self.deployment = self.release.status.apply(
            lambda status: k8s.apps.v1.Deployment.get(
                f"{name}-deployment",
                f"{namespace}/metrics-server",
                opts=pulumi.ResourceOptions(parent=self)
            )
        )
    
    def is_ready(self) -> pulumi.Output[bool]:
        """Check if the metrics server is ready."""
        def check_ready(deployment):
            if deployment.status and deployment.status.ready_replicas and deployment.status.replicas:
                return deployment.status.ready_replicas == deployment.status.replicas
            return False
        
        return self.deployment.apply(check_ready)
