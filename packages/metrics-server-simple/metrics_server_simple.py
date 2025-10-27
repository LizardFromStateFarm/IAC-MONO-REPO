import pulumi
import pulumi_kubernetes as k8s
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MetricsServerSimpleConfig:
    namespace: Optional[str] = "kube-system"
    replicas: Optional[int] = 1
    image: Optional[str] = "registry.k8s.io/metrics-server/metrics-server:v0.6.4"


class MetricsServerSimple(pulumi.ComponentResource):
    def __init__(self, name: str, config: MetricsServerSimpleConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("metrics-server:simple", name, {}, opts)
        
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
        
        # Create ServiceAccount
        self.service_account = k8s.core.v1.ServiceAccount(
            f"{name}-service-account",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=f"{name}-metrics-server",
                namespace=namespace,
                labels={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create ClusterRole
        self.cluster_role = k8s.rbac.v1.ClusterRole(
            f"{name}-cluster-role",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=f"{name}-metrics-server",
                labels={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
            ),
            rules=[
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["nodes/metrics"],
                    verbs=["get"],
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["pods", "nodes"],
                    verbs=["get", "list"],
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create ClusterRoleBinding
        self.cluster_role_binding = k8s.rbac.v1.ClusterRoleBinding(
            f"{name}-cluster-role-binding",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=f"{name}-metrics-server",
                labels={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
            ),
            role_ref=k8s.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=self.cluster_role.metadata["name"],
            ),
            subjects=[
                k8s.rbac.v1.SubjectArgs(
                    kind="ServiceAccount",
                    name=self.service_account.metadata["name"],
                    namespace=namespace,
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create Service
        self.service = k8s.core.v1.Service(
            f"{name}-service",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=f"{name}-metrics-server",
                namespace=namespace,
                labels={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
            ),
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
                ports=[
                    k8s.core.v1.ServicePortArgs(
                        name="https",
                        port=4443,
                        protocol="TCP",
                        target_port=4443,
                    ),
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create Deployment
        self.deployment = k8s.apps.v1.Deployment(
            f"{name}-deployment",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name=f"{name}-metrics-server",
                namespace=namespace,
                labels={
                    "app.kubernetes.io/name": "metrics-server",
                    "app.kubernetes.io/instance": name,
                },
            ),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                replicas=config.replicas or 1,
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app.kubernetes.io/name": "metrics-server",
                        "app.kubernetes.io/instance": name,
                    },
                ),
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        labels={
                            "app.kubernetes.io/name": "metrics-server",
                            "app.kubernetes.io/instance": name,
                        },
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        service_account_name=self.service_account.metadata["name"],
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name="metrics-server",
                                image=config.image or "registry.k8s.io/metrics-server/metrics-server:v0.6.4",
                                image_pull_policy="IfNotPresent",
                                args=[
                                    "--cert-dir=/tmp",
                                    "--secure-port=4443",
                                    "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                                    "--kubelet-use-node-status-port",
                                    "--metric-resolution=15s",
                                    "--kubelet-insecure-tls",  # Required for Kind clusters
                                ],
                                ports=[
                                    k8s.core.v1.ContainerPortArgs(
                                        name="https",
                                        container_port=4443,
                                        protocol="TCP",
                                    ),
                                ],
                                resources=k8s.core.v1.ResourceRequirementsArgs(
                                    requests={
                                        "cpu": "100m",
                                        "memory": "100Mi",
                                    },
                                    limits={
                                        "cpu": "200m",
                                        "memory": "200Mi",
                                    },
                                ),
                                liveness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/livez",
                                        port=4443,
                                        scheme="HTTP",  # Use HTTP for local development
                                    ),
                                    initial_delay_seconds=20,
                                    period_seconds=10,
                                ),
                                readiness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/readyz",
                                        port=4443,
                                        scheme="HTTP",  # Use HTTP for local development
                                    ),
                                    initial_delay_seconds=20,
                                    period_seconds=10,
                                ),
                                security_context=k8s.core.v1.SecurityContextArgs(
                                    allow_privilege_escalation=False,
                                    read_only_root_filesystem=True,
                                    run_as_non_root=True,
                                    run_as_user=1000,
                                    capabilities=k8s.core.v1.CapabilitiesArgs(
                                        drop=["ALL"],
                                    ),
                                ),
                            ),
                        ],
                        node_selector={
                            "kubernetes.io/os": "linux",
                        },
                        tolerations=[
                            k8s.core.v1.TolerationArgs(
                                key="node-role.kubernetes.io/control-plane",
                                operator="Exists",
                                effect="NoSchedule",
                            ),
                            k8s.core.v1.TolerationArgs(
                                key="node-role.kubernetes.io/master",
                                operator="Exists",
                                effect="NoSchedule",
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.service_account, self.cluster_role, self.cluster_role_binding],
            )
        )
        
        self.namespace_name = pulumi.Output.from_input(namespace)
        
    def is_ready(self) -> pulumi.Output[bool]:
        """Check if the metrics server is ready."""
        def check_ready(status):
            if status and status.ready_replicas and status.ready_replicas > 0:
                return True
            return False
        
        return self.deployment.status.apply(check_ready)
