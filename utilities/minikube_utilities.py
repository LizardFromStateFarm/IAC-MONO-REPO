from typing import Dict, Any
from .common_utilities import EnvironmentConfig


class MinikubeUtilities:
    @staticmethod
    def get_minikube_start_command(config: EnvironmentConfig) -> str:
        """Get the minikube start command for the given configuration."""
        return f"minikube start --driver=docker --memory={config.memory} --cpus={config.cpu} --kubernetes-version={config.kubernetes_version} --nodes={config.node_count}"
    
    @staticmethod
    def get_minikube_stop_command(cluster_name: str) -> str:
        """Get the minikube stop command for the given cluster."""
        return f"minikube stop -p {cluster_name}"
    
    @staticmethod
    def get_minikube_delete_command(cluster_name: str) -> str:
        """Get the minikube delete command for the given cluster."""
        return f"minikube delete -p {cluster_name}"
    
    @staticmethod
    def get_kubeconfig_path(cluster_name: str) -> str:
        """Get the kubeconfig path for the given cluster."""
        return f"~/.kube/config-{cluster_name}"
