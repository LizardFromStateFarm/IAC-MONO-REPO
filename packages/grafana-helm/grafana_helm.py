import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes import helm
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GrafanaHelmConfig:
    namespace: Optional[str] = "grafana"
    chart_version: Optional[str] = "7.0.0"
    values: Optional[Dict[str, Any]] = None
    admin_password: Optional[str] = "admin"
    persistence: Optional[Dict[str, Any]] = None
    service: Optional[Dict[str, Any]] = None


class GrafanaHelm(pulumi.ComponentResource):
    def __init__(self, name: str, config: GrafanaHelmConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("grafana:helm", name, {}, opts)
        
        namespace = config.namespace or "grafana"
        admin_password = config.admin_password or "admin"
        
        # Create namespace
        self.namespace = k8s.core.v1.Namespace(
            f"{name}-namespace",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=namespace,
                labels={
                    "app.kubernetes.io/name": "grafana",
                    "app.kubernetes.io/instance": name,
                },
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Default values for Grafana
        default_values = {
            "adminPassword": admin_password,
            "persistence": {
                "enabled": config.persistence.get("enabled", True) if config.persistence else True,
                "size": config.persistence.get("size", "10Gi") if config.persistence else "10Gi",
            },
            "service": {
                "type": config.service.get("type", "ClusterIP") if config.service else "ClusterIP",
                "port": config.service.get("port", 80) if config.service else 80,
            },
            "resources": {
                "requests": {
                    "memory": "256Mi",
                    "cpu": "250m",
                },
                "limits": {
                    "memory": "512Mi",
                    "cpu": "500m",
                },
            },
        }
        
        # Merge with user-provided values
        values = {**default_values, **(config.values or {})}
        
        # Deploy Grafana using Helm
        self.release = helm.v3.Release(
            f"{name}-grafana",
            chart="grafana",
            version=config.chart_version,
            repository_opts=helm.v3.RepositoryOptsArgs(
                repo="https://grafana.github.io/helm-charts",
            ),
            namespace=namespace,
            values=values,
            create_namespace=False,  # We're creating the namespace separately
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.namespace],
            )
        )
        
        self.namespace_name = pulumi.Output.from_input(namespace)
        self.admin_password = pulumi.Output.from_input(admin_password)
        
        # Get the service
        self.service = self.release.status.apply(
            lambda status: k8s.core.v1.Service.get(
                f"{name}-service",
                f"{namespace}/grafana",
                opts=pulumi.ResourceOptions(parent=self)
            )
        )
    
    def get_service_url(self) -> pulumi.Output[str]:
        """Get the service URL for Grafana."""
        def get_url(svc):
            if svc.spec and svc.spec.type == "NodePort" and svc.spec.ports and svc.spec.ports[0].node_port:
                return f"http://localhost:{svc.spec.ports[0].node_port}"
            return f"http://{svc.metadata.name}.{self.namespace_name}.svc.cluster.local"
        
        return self.service.apply(get_url)
