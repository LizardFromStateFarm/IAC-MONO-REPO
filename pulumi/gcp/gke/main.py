"""
Pulumi configuration for GCP GKE cluster
"""
import pulumi
import pulumi_gcp as gcp

# Configuration
config = pulumi.Config()
cluster_name = config.get("cluster_name") or "pulumi-gke"
node_count = config.get_int("node_count") or 2
machine_type = config.get("machine_type") or "e2-medium"
project_id = config.get("project_id") or "your-project-id"
region = config.get("region") or "us-central1"

# Enable required APIs
compute_api = gcp.projects.Service("compute-api",
    service="compute.googleapis.com",
    project=project_id)

container_api = gcp.projects.Service("container-api",
    service="container.googleapis.com",
    project=project_id)

# VPC Network
vpc_network = gcp.compute.Network("gke-vpc",
    name=f"{cluster_name}-vpc",
    auto_create_subnetworks=False,
    project=project_id)

# Subnet
subnet = gcp.compute.Subnetwork("gke-subnet",
    name=f"{cluster_name}-subnet",
    ip_cidr_range="10.0.0.0/24",
    region=region,
    network=vpc_network.id,
    project=project_id)

# Firewall rule for GKE
firewall_rule = gcp.compute.Firewall("gke-firewall",
    name=f"{cluster_name}-firewall",
    network=vpc_network.id,
    allow=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=["22", "80", "443", "8080"],
        ),
        gcp.compute.FirewallAllowArgs(
            protocol="icmp",
        ),
    ],
    source_ranges=["0.0.0.0/0"],
    target_tags=["gke-node"],
    project=project_id)

# GKE Cluster
cluster = gcp.container.Cluster("gke-cluster",
    name=cluster_name,
    location=region,
    project=project_id,
    network=vpc_network.name,
    subnetwork=subnet.name,
    initial_node_count=node_count,
    remove_default_node_pool=True,
    node_config=gcp.container.ClusterNodeConfigArgs(
        machine_type=machine_type,
        disk_size_gb=20,
        disk_type="pd-standard",
        image_type="COS",
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        tags=["gke-node"],
    ),
    master_auth=gcp.container.ClusterMasterAuthArgs(
        client_certificate_config=gcp.container.ClusterMasterAuthClientCertificateConfigArgs(
            issue_client_certificate=True,
        ),
    ),
    ip_allocation_policy=gcp.container.ClusterIpAllocationPolicyArgs(
        cluster_ipv4_cidr_block="10.1.0.0/16",
        services_ipv4_cidr_block="10.2.0.0/16",
    ),
    private_cluster_config=gcp.container.ClusterPrivateClusterConfigArgs(
        enable_private_nodes=True,
        enable_private_endpoint=False,
        master_ipv4_cidr_block="172.16.0.0/28",
    ))

# Node Pool
node_pool = gcp.container.NodePool("gke-node-pool",
    name=f"{cluster_name}-node-pool",
    location=region,
    cluster=cluster.name,
    project=project_id,
    node_count=node_count,
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type=machine_type,
        disk_size_gb=20,
        disk_type="pd-standard",
        image_type="COS",
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
        tags=["gke-node"],
    ),
    management=gcp.container.NodePoolManagementArgs(
        auto_repair=True,
        auto_upgrade=True,
    ))

# Export outputs
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_endpoint", cluster.endpoint)
pulumi.export("cluster_version", cluster.version)
pulumi.export("network_name", vpc_network.name)
pulumi.export("subnet_name", subnet.name)
