import pulumi
import pulumi_kubernetes as k8s
from typing import Dict, Optional, Any
from dataclasses import dataclass


CommonLabels = Dict[str, str]


@dataclass
class EnvironmentConfig:
    name: str
    cluster_name: str
    node_count: int
    memory: str
    cpu: str
    kubernetes_version: str


class CommonUtilities:
    @staticmethod
    def get_common_labels(environment: str, component: str) -> CommonLabels:
        """Get common labels for Kubernetes resources."""
        return {
            "app.kubernetes.io/name": component,
            "app.kubernetes.io/instance": f"{environment}-{component}",
            "app.kubernetes.io/version": "1.0.0",
            "app.kubernetes.io/component": component,
            "app.kubernetes.io/part-of": "minikube-stack",
            "environment": environment,
        }
    
    @staticmethod
    def get_environment_config(environment: str) -> EnvironmentConfig:
        """Get environment-specific configuration."""
        configs = {
            "nonprod": EnvironmentConfig(
                name="nonprod",
                cluster_name="nonprod-minikube",
                node_count=1,
                memory="4g",
                cpu="2",
                kubernetes_version="v1.28.0",
            ),
            "prod": EnvironmentConfig(
                name="prod",
                cluster_name="prod-minikube",
                node_count=2,
                memory="8g",
                cpu="4",
                kubernetes_version="v1.28.0",
            ),
        }
        
        return configs.get(environment, configs["nonprod"])
    
    @staticmethod
    def create_namespace(
        name: str,
        namespace: str,
        labels: CommonLabels,
        opts: Optional[pulumi.ResourceOptions] = None
    ) -> k8s.core.v1.Namespace:
        """Create a Kubernetes namespace with labels."""
        return k8s.core.v1.Namespace(
            name,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=namespace,
                labels=labels,
            ),
            opts=opts
        )
    
    @staticmethod
    def get_resource_quota(
        name: str,
        namespace: str,
        requests: Dict[str, str],
        limits: Dict[str, str],
        opts: Optional[pulumi.ResourceOptions] = None
    ) -> k8s.core.v1.ResourceQuota:
        """Create a resource quota for a namespace."""
        return k8s.core.v1.ResourceQuota(
            name,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=name,
                namespace=namespace,
            ),
            spec=k8s.core.v1.ResourceQuotaSpecArgs(
                hard={
                    "requests.cpu": requests["cpu"],
                    "requests.memory": requests["memory"],
                    "limits.cpu": limits["cpu"],
                    "limits.memory": limits["memory"],
                },
            ),
            opts=opts
        )
    
    @staticmethod
    def get_limit_range(
        name: str,
        namespace: str,
        default_limits: Dict[str, str],
        opts: Optional[pulumi.ResourceOptions] = None
    ) -> k8s.core.v1.LimitRange:
        """Create a limit range for a namespace."""
        return k8s.core.v1.LimitRange(
            name,
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=name,
                namespace=namespace,
            ),
            spec=k8s.core.v1.LimitRangeSpecArgs(
                limits=[
                    k8s.core.v1.LimitRangeItemArgs(
                        type="Container",
                        default=default_limits,
                        default_request={
                            "cpu": "100m",
                            "memory": "128Mi",
                        },
                    ),
                ],
            ),
            opts=opts
        )
