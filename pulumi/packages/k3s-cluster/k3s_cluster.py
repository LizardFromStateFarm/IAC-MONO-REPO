import pulumi
import pulumi_kubernetes as k8s
import pulumi_command as command
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import yaml
import os
import subprocess
import shutil
import sys


@dataclass
class K3sClusterConfig:
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
    # K3s specific configuration
    disable_components: Optional[List[str]] = None  # Components to disable
    enable_components: Optional[List[str]] = None  # Components to enable
    podman_runtime: Optional[bool] = True  # Use Podman instead of Docker
    k3s_image: Optional[str] = None  # Custom K3s image
    # Network configuration
    cluster_cidr: Optional[str] = "10.42.0.0/16"
    service_cidr: Optional[str] = "10.43.0.0/16"
    cluster_dns: Optional[str] = "10.43.0.10"
    # Metrics server configuration
    enable_metrics_server: Optional[bool] = True
    metrics_server_namespace: Optional[str] = "kube-system"
    metrics_server_replicas: Optional[int] = 1

    @classmethod
    def from_environment(cls, environment: str) -> 'K3sClusterConfig':
        """Load configuration from environment-specific YAML file."""
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(package_dir, 'k3s-cluster', 'configs', f'{environment}.yaml')
        
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)


class K3sCluster(pulumi.ComponentResource):
    def __init__(self, name: str, config: K3sClusterConfig, opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("k3s:cluster", name, {}, opts)
        
        self.cluster_name = pulumi.Output.from_input(config.cluster_name)
        self.kubernetes_version = pulumi.Output.from_input(config.kubernetes_version)
        
        # Check if Podman is available
        self.podman_available = self._check_podman_available()
        
        # Create K3s cluster configuration
        k3s_config = self._create_k3s_config(config)
        
        # Create K3s cluster using command provider
        if config.podman_runtime and self.podman_available:
            self.cluster = self._create_k3s_with_podman(name, config, k3s_config)
        else:
            self.cluster = self._create_k3s_with_docker(name, config, k3s_config)
        
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
            create=f"k3s kubeconfig write {config.cluster_name}",
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
        
        # Deploy metrics server if enabled
        if config.enable_metrics_server:
            self.metrics_server = self._deploy_metrics_server(name, config)
        else:
            self.metrics_server = None
    
    def _check_podman_available(self) -> bool:
        """Check if Podman is available on the system."""
        try:
            result = subprocess.run(['podman', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _create_k3s_with_podman(self, name: str, config: K3sClusterConfig, k3s_config: str) -> command.local.Command:
        """Create K3s cluster using Podman."""
        # Set up Podman environment
        env_vars = {
            "CONTAINER_RUNTIME": "podman",
            "K3S_RUNTIME": "podman"
        }
        
        # Create K3s cluster
        return command.local.Command(
            f"{name}-create-podman",
            create=f"k3s server --cluster-init --write-kubeconfig-mode=644 --config=-",
            stdin=k3s_config,
            environment=env_vars,
            opts=pulumi.ResourceOptions(parent=self)
        )
    
    def _create_k3s_with_docker(self, name: str, config: K3sClusterConfig, k3s_config: str) -> command.local.Command:
        """Create K3s cluster using Docker (fallback)."""
        return command.local.Command(
            f"{name}-create-docker",
            create=f"k3s server --cluster-init --write-kubeconfig-mode=644 --config=-",
            stdin=k3s_config,
            opts=pulumi.ResourceOptions(parent=self)
        )
    
    def _create_k3s_config(self, config: K3sClusterConfig) -> str:
        """Create K3s cluster configuration YAML."""
        k3s_config = {
            "apiVersion": "k3s.cattle.io/v1",
            "kind": "Cluster",
            "metadata": {
                "name": config.cluster_name
            },
            "spec": {
                "kubernetesVersion": config.kubernetes_version,
                "clusterCIDR": config.cluster_cidr,
                "serviceCIDR": config.service_cidr,
                "clusterDNS": config.cluster_dns,
                "disable": config.disable_components or [],
                "enable": config.enable_components or []
            }
        }
        
        # Add node configuration
        if config.nodes > 0 or config.worker_nodes > 0:
            k3s_config["spec"]["nodes"] = []
            
            # Add control plane nodes
            for i in range(config.nodes):
                node = {
                    "role": "control-plane",
                    "image": config.k3s_image or f"rancher/k3s:{config.kubernetes_version}-k3s1"
                }
                
                # Add port mappings if specified
                if config.port_mappings:
                    node["extraPortMappings"] = config.port_mappings
                
                if config.extra_port_mappings:
                    if "extraPortMappings" not in node:
                        node["extraPortMappings"] = []
                    node["extraPortMappings"].extend(config.extra_port_mappings)
                
                k3s_config["spec"]["nodes"].append(node)
            
            # Add worker nodes
            for i in range(config.worker_nodes):
                worker = {
                    "role": "worker",
                    "image": config.k3s_image or f"rancher/k3s:{config.kubernetes_version}-k3s1"
                }
                k3s_config["spec"]["nodes"].append(worker)
        
        return json.dumps(k3s_config, indent=2)
    
    def _deploy_metrics_server(self, name: str, config: K3sClusterConfig) -> pulumi.ComponentResource:
        """Deploy metrics server to the K3s cluster."""
        # Add the packages directory to the Python path
        packages_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'packages')
        if packages_dir not in sys.path:
            sys.path.append(packages_dir)
        
        try:
            from metrics_server_simple import MetricsServerSimple, MetricsServerSimpleConfig
            
            # Create metrics server configuration
            metrics_config = MetricsServerSimpleConfig(
                namespace=config.metrics_server_namespace,
                replicas=config.metrics_server_replicas,
                kubelet_insecure_tls=True,  # K3s works well with this setting
            )
            
            # Deploy metrics server
            return MetricsServerSimple(
                f"{name}-metrics-server",
                metrics_config,
                opts=pulumi.ResourceOptions(
                    parent=self,
                    provider=self.provider,
                    depends_on=[self.provider]
                )
            )
        except ImportError as e:
            pulumi.log.warn(f"Could not import metrics server package: {e}")
            # Fallback: create a simple metrics server deployment
            return self._create_simple_metrics_server(name, config)
    
    def _create_simple_metrics_server(self, name: str, config: K3sClusterConfig) -> pulumi.ComponentResource:
        """Create a simple metrics server deployment as fallback."""
        namespace = config.metrics_server_namespace or "kube-system"
        
        # Create ServiceAccount
        service_account = k8s.core.v1.ServiceAccount(
            f"{name}-metrics-sa",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server",
                namespace=namespace,
                labels={"k8s-app": "metrics-server"},
            ),
            opts=pulumi.ResourceOptions(parent=self, provider=self.provider)
        )
        
        # Create ClusterRole
        cluster_role = k8s.rbac.v1.ClusterRole(
            f"{name}-metrics-cr",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="system:metrics-server",
                labels={"k8s-app": "metrics-server"},
            ),
            rules=[
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""], resources=["nodes/metrics"], verbs=["get"]
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=[""], resources=["pods", "nodes"], verbs=["get", "list", "watch"]
                ),
                k8s.rbac.v1.PolicyRuleArgs(
                    api_groups=["metrics.k8s.io"], resources=["*"], verbs=["get", "list"]
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self, provider=self.provider)
        )
        
        # Create ClusterRoleBinding
        cluster_role_binding = k8s.rbac.v1.ClusterRoleBinding(
            f"{name}-metrics-crb",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="system:metrics-server",
            ),
            role_ref=k8s.rbac.v1.RoleRefArgs(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=cluster_role.metadata["name"],
            ),
            subjects=[
                k8s.rbac.v1.SubjectArgs(
                    kind="ServiceAccount",
                    name=service_account.metadata["name"],
                    namespace=namespace,
                ),
            ],
            opts=pulumi.ResourceOptions(parent=self, provider=self.provider)
        )
        
        # Create Service
        service = k8s.core.v1.Service(
            f"{name}-metrics-svc",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server",
                namespace=namespace,
                labels={"k8s-app": "metrics-server"},
            ),
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={"k8s-app": "metrics-server"},
                ports=[
                    k8s.core.v1.ServicePortArgs(
                        port=443, protocol="TCP", target_port=4443
                    ),
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self, provider=self.provider)
        )
        
        # Create Deployment
        deployment = k8s.apps.v1.Deployment(
            f"{name}-metrics-deploy",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="metrics-server",
                namespace=namespace,
                labels={"k8s-app": "metrics-server"},
            ),
            spec=k8s.apps.v1.DeploymentSpecArgs(
                replicas=config.metrics_server_replicas or 1,
                selector=k8s.meta.v1.LabelSelectorArgs(
                    match_labels={"k8s-app": "metrics-server"}
                ),
                template=k8s.core.v1.PodTemplateSpecArgs(
                    metadata=k8s.meta.v1.ObjectMetaArgs(
                        labels={"k8s-app": "metrics-server"},
                    ),
                    spec=k8s.core.v1.PodSpecArgs(
                        service_account_name=service_account.metadata["name"],
                        containers=[
                            k8s.core.v1.ContainerArgs(
                                name="metrics-server",
                                image="registry.k8s.io/metrics-server/metrics-server:v0.6.4",
                                args=[
                                    "--cert-dir=/tmp",
                                    "--secure-port=4443",
                                    "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                                    "--kubelet-use-node-status-port",
                                    "--metric-resolution=15s",
                                    "--kubelet-insecure-tls",  # K3s specific
                                ],
                                ports=[
                                    k8s.core.v1.ContainerPortArgs(
                                        name="https", container_port=4443, protocol="TCP"
                                    ),
                                ],
                                resources=k8s.core.v1.ResourceRequirementsArgs(
                                    requests={"cpu": "100m", "memory": "200Mi"},
                                    limits={"cpu": "100m", "memory": "200Mi"},
                                ),
                            ),
                        ],
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                provider=self.provider,
                depends_on=[service_account, cluster_role, cluster_role_binding]
            )
        )
        
        # Create APIService
        api_service = k8s.apiregistration.v1.APIService(
            f"{name}-metrics-api",
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name="v1beta1.metrics.k8s.io",
                labels={"k8s-app": "metrics-server"},
            ),
            spec=k8s.apiregistration.v1.APIServiceSpecArgs(
                service=k8s.apiregistration.v1.ServiceReferenceArgs(
                    name=service.metadata["name"],
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
                provider=self.provider,
                depends_on=[service, deployment]
            )
        )
        
        # Create a simple component resource to represent the metrics server
        class SimpleMetricsServer(pulumi.ComponentResource):
            def __init__(self, name, opts=None):
                super().__init__("metrics-server:simple", name, {}, opts)
                self.namespace_name = pulumi.Output.from_input(namespace)
                self.is_ready = deployment.status.apply(
                    lambda status: status.ready_replicas > 0 if status and status.ready_replicas else False
                )
        
        return SimpleMetricsServer(
            f"{name}-metrics-server",
            opts=pulumi.ResourceOptions(parent=self)
        )
    
    def delete_cluster(self) -> pulumi.Output[None]:
        """Delete the K3s cluster."""
        return command.local.Command(
            f"{self.cluster_name}-delete",
            create=f"k3s server --cluster-reset",
            opts=pulumi.ResourceOptions(parent=self)
        )
    
    def get_kubeconfig(self) -> pulumi.Output[str]:
        """Get the kubeconfig for the cluster."""
        return self.kubeconfig.stdout
    
    def get_cluster_info(self) -> pulumi.Output[Dict[str, Any]]:
        """Get cluster information."""
        return pulumi.Output.all(
            cluster_name=self.cluster_name,
            kubernetes_version=self.kubernetes_version,
            kubeconfig=self.kubeconfig.stdout
        ).apply(lambda args: {
            "cluster_name": args["cluster_name"],
            "kubernetes_version": args["kubernetes_version"],
            "kubeconfig": args["kubeconfig"],
            "metrics_server_enabled": self.metrics_server is not None
        })
    
    def get_metrics_server_info(self) -> pulumi.Output[Dict[str, Any]]:
        """Get metrics server information."""
        if self.metrics_server is None:
            return pulumi.Output.from_input({
                "enabled": False,
                "status": "disabled"
            })
        
        return pulumi.Output.all(
            namespace=self.metrics_server.namespace_name,
            is_ready=self.metrics_server.is_ready
        ).apply(lambda args: {
            "enabled": True,
            "namespace": args["namespace"],
            "ready": args["is_ready"],
            "status": "ready" if args["is_ready"] else "starting"
        })
