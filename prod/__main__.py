import pulumi
from kind_cluster import KindCluster, KindClusterConfig
from grafana_helm import GrafanaHelm, GrafanaHelmConfig
from metrics_server_helm import MetricsServerHelm, MetricsServerHelmConfig

# Configuration
config = pulumi.Config()

# Kind cluster configuration
cluster_name = config.get("clusterName") or "prod-kind"
kubernetes_version = config.get("kubernetesVersion") or "v1.28.0"
worker_nodes = config.get_int("workerNodes") or 1

# Create Kind cluster with multiple nodes for production
cluster = KindCluster("prod-cluster", KindClusterConfig(
    cluster_name=cluster_name,
    kubernetes_version=kubernetes_version,
    nodes=1,
    worker_nodes=worker_nodes,
    port_mappings=[
        {"containerPort": 30000, "hostPort": 30000, "protocol": "TCP"},
        {"containerPort": 30001, "hostPort": 30001, "protocol": "TCP"},
    ],
    wait_for_ready=True,
    wait_for_ready_timeout="300s",
))

# Deploy metrics server
metrics_server = MetricsServerHelm("prod-metrics-server", MetricsServerHelmConfig(
    namespace="kube-system",
    chart_version="3.10.0",
    args=[
        "--cert-dir=/tmp",
        "--secure-port=4443",
        "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
        "--kubelet-use-node-status-port",
        "--metric-resolution=15s"
    ],
    host_network=False,
    replicas=2,  # Higher replica count for production
), opts=pulumi.ResourceOptions(depends_on=[cluster]))

# Deploy Grafana with production settings
grafana = GrafanaHelm("prod-grafana", GrafanaHelmConfig(
    namespace="grafana",
    chart_version="7.0.0",
    admin_password="prod-admin-2024!",  # More secure password for production
    persistence={
        "enabled": True,
        "size": "50Gi",  # Larger storage for production
    },
    service={
        "type": "NodePort",
        "port": 80,
        "nodePort": 30000,
    },
    values={
        "grafana": {
            "adminPassword": "prod-admin-2024!",
            "persistence": {
                "enabled": True,
                "size": "50Gi",
            },
            "service": {
                "type": "NodePort",
                "port": 80,
                "nodePort": 30000,
            },
            "resources": {
                "requests": {
                    "memory": "512Mi",
                    "cpu": "500m",
                },
                "limits": {
                    "memory": "1Gi",
                    "cpu": "1000m",
                },
            },
            "replicas": 2,  # Multiple replicas for high availability
        },
    },
), opts=pulumi.ResourceOptions(depends_on=[cluster, metrics_server]))

# Export important values
pulumi.export("clusterName", cluster.cluster_name)
pulumi.export("kubeconfig", cluster.get_kubeconfig())
pulumi.export("grafanaUrl", grafana.get_service_url())
pulumi.export("grafanaAdminPassword", grafana.admin_password)
pulumi.export("metricsServerReady", metrics_server.is_ready())