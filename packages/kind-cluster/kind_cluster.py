import pulumi
import pulumi_kubernetes as k8s
import pulumi_command as command
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import yaml
import os


@dataclass
class KindClusterConfig:
    cluster_name: str
    kubernetes_version: Optional[str] = "v1.28.0"
    nodes: Optional[int] = 1
    worker_nodes: Optional[int] = 0
    port_mappings: Optional[List[Dict[str, int]]] = None
    extra_port_mappings: Optional[List[Dict[str, Any]]] = None
    wait_for_ready: Optional[bool] = True
    wait_for_ready_timeout: Optional[str] = "300s"
    # Memory configuration
    node_memory: Optional[str] = "2Gi"  # Memory per node
    total_memory_limit: Optional[str] = "4Gi"  # Total cluster memory limit

    @classmethod
    def from_environment(cls, environment: str) -> 'KindClusterConfig':
        """Load configuration from environment-specific YAML file."""
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(package_dir, 'kind-cluster', 'configs', f'{environment}.yaml')
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)


class KindCluster(pulumi.ComponentResource):
    def __init__(self, name: str, config: KindClusterConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("kind:cluster", name, {}, opts)
        
        self.cluster_name = pulumi.Output.from_input(config.cluster_name)
        self.kubernetes_version = pulumi.Output.from_input(config.kubernetes_version)
        
        # Create Kind cluster configuration
        kind_config = self._create_kind_config(config)
        
        # Create Kind cluster using command provider
        self.cluster = command.local.Command(
            f"{name}-create",
            create=f"kind create cluster --name {config.cluster_name} --config -",
            stdin=kind_config,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Wait for cluster to be ready
        if config.wait_for_ready:
            self.ready = command.local.Command(
                f"{name}-ready",
                create=f"kubectl wait --for=condition=Ready nodes --all --timeout={config.wait_for_ready_timeout}",
                opts=pulumi.ResourceOptions(
                    parent=self,
                    depends_on=[self.cluster]
                )
            )
        else:
            self.ready = self.cluster
        
        # Get kubeconfig
        self.kubeconfig = command.local.Command(
            f"{name}-kubeconfig",
            create=f"kind get kubeconfig --name {config.cluster_name}",
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.ready]
            )
        )
        
        # Create Kubernetes provider
        self.provider = k8s.Provider(
            f"{name}-provider",
            kubeconfig=self.kubeconfig.stdout,
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.ready])
        )
    
    def _create_kind_config(self, config: KindClusterConfig) -> str:
        """Create Kind cluster configuration YAML."""
        kind_config = {
            "kind": "Cluster",
            "apiVersion": "kind.x-k8s.io/v1alpha4",
            "name": config.cluster_name,
            "nodes": []
        }
        
        # Add control plane node
        control_plane = {
            "role": "control-plane",
            "image": f"kindest/node:{config.kubernetes_version}",
        }
        
        # Memory configuration will be handled by Docker Desktop resource limits
        # No need for kubelet patches that can cause startup issues
        
        # Add port mappings if specified
        if config.port_mappings:
            control_plane["extraPortMappings"] = config.port_mappings
        
        if config.extra_port_mappings:
            if "extraPortMappings" not in control_plane:
                control_plane["extraPortMappings"] = []
            control_plane["extraPortMappings"].extend(config.extra_port_mappings)
        
        kind_config["nodes"].append(control_plane)
        
        # Add worker nodes
        for i in range(config.worker_nodes):
            worker = {
                "role": "worker",
                "image": f"kindest/node:{config.kubernetes_version}",
            }
            
            # Memory configuration will be handled by Docker Desktop resource limits
            # No need for kubelet patches that can cause startup issues
            
            kind_config["nodes"].append(worker)
        
        return json.dumps(kind_config, indent=2)
    
    def delete_cluster(self) -> pulumi.Output[None]:
        """Delete the Kind cluster."""
        return command.local.Command(
            f"{self.cluster_name}-delete",
            create=f"kind delete cluster --name {self.cluster_name}",
            opts=pulumi.ResourceOptions(parent=self)
        )
    
    def get_kubeconfig(self) -> pulumi.Output[str]:
        """Get the kubeconfig for the cluster."""
        return self.kubeconfig.stdout
