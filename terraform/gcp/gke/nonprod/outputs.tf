output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = module.gke.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for GKE control plane"
  value       = module.gke.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version"
  value       = module.gke.cluster_version
}

output "network_name" {
  description = "Name of the VPC network"
  value       = module.gke.network_name
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = module.gke.subnet_name
}

