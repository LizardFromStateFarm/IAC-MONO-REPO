import pulumi
import pulumi_kubernetes as k8s
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MetricsServerSimpleConfig:
    namespace: Optional[str] = "kube-system"
    replicas: Optional[int] = 1
    image: Optional[str] = "registry.k8s.io/metrics-server/metrics-server:v0.6.4"
    # Kind-specific configuration
    kubelet_insecure_tls: Optional[bool] = True


class MetricsServerSimple(pulumi.ComponentResource):
    def __init__(self, name: str, config: MetricsServerSimpleConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("metrics-server:simple", name, {}, opts)
        
        namespace = config.namespace or "kube-system"
        
        # Create ServiceAccount
        self.service_account = k8s.core.v1.ServiceAccount(
            f"{name}-service-account",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server",
                namespace=namespace,
                labels={
                    "k8s-app": "metrics-server",
                },
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create ClusterRole for aggregated metrics reader
        self.aggregated_metrics_reader_role = k8s.rbac.v1.ClusterRole(
            f"{name}-aggregated-metrics-reader",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="system:aggregated-metrics-reader",
                labels={
                    "rbac.authorization.k8s.io/aggregate-to-view": "true",
                    "rbac.authorization.k8s.io/aggregate-to-edit": "true",
                    "rbac.authorization.k8s.io/aggregate-to-admin": "true",
                },
            ),
            rules=[
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=["metrics.k8s.io"],
                    resources=["pods", "nodes"],
                    verbs=["get", "list"],
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create ClusterRole for metrics server
        self.cluster_role = k8s.rbac.v1.ClusterRole(
            f"{name}-cluster-role",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="system:metrics-server",
                labels={
                    "k8s-app": "metrics-server",
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
                    verbs=["get", "list", "watch"],
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["configmaps"],
                    verbs=["get", "list", "watch"],
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=["metrics.k8s.io"],
                    resources=["*"],
                    verbs=["get", "list"],
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""],
                    resources=["nodes/stats"],
                    verbs=["get"],
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=["apiextensions.k8s.io"],
                    resources=["customresourcedefinitions"],
                    verbs=["get", "list"],
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create RoleBinding for auth reader
        self.auth_reader_binding = k8s.rbac.v1.RoleBinding(
            f"{name}-auth-reader-binding",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server-auth-reader",
                namespace=namespace,
            ),
            role_ref=k8s.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="Role",
                name="extension-apiserver-authentication-reader",
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
        
        # Create ClusterRoleBinding for auth delegator
        self.auth_delegator_binding = k8s.rbac.v1.ClusterRoleBinding(
            f"{name}-auth-delegator-binding",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server:system:auth-delegator",
            ),
            role_ref=k8s.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name="system:auth-delegator",
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
        
        # Create ClusterRoleBinding for metrics server
        self.cluster_role_binding = k8s.rbac.v1.ClusterRoleBinding(
            f"{name}-cluster-role-binding",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="system:metrics-server",
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
                name="metrics-server",
                namespace=namespace,
                labels={
                    "k8s-app": "metrics-server",
                },
            ),
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={
                    "k8s-app": "metrics-server",
                },
                ports=[
                    k8s.core.v1.ServicePortArgs(
                        port=443,
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
                name="metrics-server",
                namespace=namespace,
                labels={
                    "k8s-app": "metrics-server",
                },
            ),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                replicas=config.replicas or 1,
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "k8s-app": "metrics-server",
                    },
                ),
                strategy=k8s.apps.v1.DeploymentStrategyArgs(
                    rolling_update=k8s.apps.v1.RollingUpdateDeploymentArgs(
                        max_unavailable=0,
                    ),
                ),
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        name="metrics-server",
                        labels={
                            "k8s-app": "metrics-server",
                        },
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        service_account_name=self.service_account.metadata["name"],
                        volumes=[
                            k8s.core.v1.VolumeArgs(
                                name="tmp-dir",
                                empty_dir=k8s.core.v1.EmptyDirVolumeSourceArgs(),
                            ),
                        ],
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name="metrics-server",
                                image=config.image or "registry.k8s.io/metrics-server/metrics-server:v0.6.4",
                                image_pull_policy="IfNotPresent",
                                args=self._get_container_args(config),
                                ports=[
                                    k8s.core.v1.ContainerPortArgs(
                                        name="https",
                                        container_port=4443,
                                        protocol="TCP",
                                    ),
                                ],
                                readiness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/readyz",
                                        port="https",
                                        scheme="HTTPS",
                                    ),
                                    period_seconds=10,
                                    failure_threshold=3,
                                ),
                                liveness_probe=k8s.core.v1.ProbeArgs(
                                    http_get=k8s.core.v1.HTTPGetActionArgs(
                                        path="/livez",
                                        port="https",
                                        scheme="HTTPS",
                                    ),
                                    period_seconds=10,
                                    failure_threshold=3,
                                ),
                                volume_mounts=[
                                    k8s.core.v1.VolumeMountArgs(
                                        name="tmp-dir",
                                        mount_path="/tmp",
                                    ),
                                ],
                                resources=k8s.core.v1.ResourceRequirementsArgs(
                                    requests={
                                        "cpu": "100m",
                                        "memory": "200Mi",
                                    },
                                    limits={
                                        "cpu": "100m",
                                        "memory": "200Mi",
                                    },
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
                depends_on=[
                    self.service_account,
                    self.aggregated_metrics_reader_role,
                    self.cluster_role,
                    self.auth_reader_binding,
                    self.auth_delegator_binding,
                    self.cluster_role_binding,
                ],
            )
        )
        
        # Create APIService for metrics.k8s.io
        self.api_service = k8s.apiregistration.v1.APIService(
            f"{name}-api-service",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="v1beta1.metrics.k8s.io",
                labels={
                    "k8s-app": "metrics-server",
                },
            ),
            spec=k8s.apiregistration.v1.APIServiceSpecArgs(
                service=k8s.apiregistration.v1.ServiceReferenceArgs(
                    name=self.service.metadata["name"],
                    namespace=namespace,
                    port=443,
                ),
                group="metrics.k8s.io",
                version="v1beta1",
                insecure_skip_tls_verify=True,
                group_priority_minimum=100,
                version_priority=100,
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.service, self.deployment],
            )
        )
        
        self.namespace_name = pulumi.Output.from_input(namespace)
        
    def _get_container_args(self, config: MetricsServerSimpleConfig) -> list[str]:
        """Get container arguments based on configuration."""
        args = [
            "--cert-dir=/tmp",
            "--secure-port=4443",
            "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
            "--kubelet-use-node-status-port",
            "--metric-resolution=15s",
        ]
        
        # Add Kind-specific flag if enabled
        if config.kubelet_insecure_tls:
            args.append("--kubelet-insecure-tls")
            
        return args
        
    def is_ready(self) -> pulumi.Output[bool]:
        """Check if the metrics server is ready."""
        def check_ready(status):
            if status and status.ready_replicas and status.ready_replicas > 0:
                return True
            return False
        
        return self.deployment.status.apply(check_ready)