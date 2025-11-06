output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.gke_cluster.name
}

output "cluster_endpoint" {
  description = "Endpoint for GKE control plane"
  value       = google_container_cluster.gke_cluster.endpoint
}

output "cluster_version" {
  description = "Kubernetes version"
  value       = google_container_cluster.gke_cluster.version
}

output "network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.gke_vpc.name
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = google_compute_subnetwork.gke_subnet.name
}

