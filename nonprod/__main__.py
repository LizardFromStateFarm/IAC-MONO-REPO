import pulumi
from kind_cluster import KindCluster, KindClusterConfig
from grafana_helm import GrafanaHelm, GrafanaHelmConfig
from metrics_server_helm import MetricsServerHelm, MetricsServerHelmConfig

# Configuration
config = pulumi.Config()

# Kind cluster configuration
cluster_name = config.get("clusterName") or "nonprod-kind"
kubernetes_version = config.get("kubernetesVersion") or "v1.28.0"
worker_nodes = config.get_int("workerNodes") or 0

# Create Kind cluster
cluster = KindCluster("nonprod-cluster", KindClusterConfig(
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
metrics_server = MetricsServerHelm("nonprod-metrics-server", MetricsServerHelmConfig(
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
    replicas=1,
), opts=pulumi.ResourceOptions(depends_on=[cluster]))

# Deploy Grafana
grafana = GrafanaHelm("nonprod-grafana", GrafanaHelmConfig(
    namespace="grafana",
    chart_version="7.0.0",
    admin_password="admin123",
    persistence={
        "enabled": True,
        "size": "10Gi",
    },
    service={
        "type": "NodePort",
        "port": 80,
        "nodePort": 30000,
    },
    values={
        "grafana": {
            "adminPassword": "admin123",
            "persistence": {
                "enabled": True,
                "size": "10Gi",
            },
            "service": {
                "type": "NodePort",
                "port": 80,
                "nodePort": 30000,
            },
        },
    },
), opts=pulumi.ResourceOptions(depends_on=[cluster, metrics_server]))

# Export important values
pulumi.export("clusterName", cluster.cluster_name)
pulumi.export("kubeconfig", cluster.get_kubeconfig())
pulumi.export("grafanaUrl", grafana.get_service_url())
pulumi.export("grafanaAdminPassword", grafana.admin_password)
pulumi.export("metricsServerReady", metrics_server.is_ready())