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
    # Kind-specific configuration
    kubelet_insecure_tls: Optional[bool] = True
    use_official_approach: Optional[bool] = True  # Use official metrics-server instead of Helm

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
        
        # Use the working approach instead of Helm
        if config.use_official_approach:
            self._create_official_metrics_server(name, config, opts)
        else:
            self._create_helm_metrics_server(name, config, opts)
    
    def _create_official_metrics_server(self, name: str, config: MetricsServerHelmConfig, opts: Optional[pulumi.ResourceOptions] = None):
        """Create metrics server using the official Kubernetes approach."""
        namespace = config.namespace or "kube-system"
        
        # Import the simple metrics server implementation
        from ..metrics_server_simple import MetricsServerSimple, MetricsServerSimpleConfig
        
        # Convert Helm config to Simple config
        simple_config = MetricsServerSimpleConfig(
            namespace=config.namespace,
            replicas=config.replicas,
            kubelet_insecure_tls=config.kubelet_insecure_tls,
        )
        
        # Create the metrics server using the simple approach
        self.metrics_server = MetricsServerSimple(f"{name}-official", simple_config, opts)
        
        # Export the same interface
        self.namespace_name = self.metrics_server.namespace_name
        self.is_ready = self.metrics_server.is_ready
    
    def _create_helm_metrics_server(self, name: str, config: MetricsServerHelmConfig, opts: Optional[pulumi.ResourceOptions] = None):
        """Create metrics server using Helm (legacy approach - not recommended for Kind)."""
        # This is kept for backward compatibility but not recommended
        # The official approach should be used instead
        raise NotImplementedError("Helm approach is deprecated. Use use_official_approach=True instead.")