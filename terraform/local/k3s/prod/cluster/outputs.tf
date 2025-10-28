output "cluster_name" {
  description = "Name of the K3s cluster"
  value       = module.k3s_cluster.cluster_name
}

output "kubernetes_version" {
  description = "Kubernetes version"
  value       = module.k3s_cluster.kubernetes_version
}

output "kubeconfig" {
  description = "Kubeconfig content"
  value       = module.k3s_cluster.kubeconfig
  sensitive   = true
}

output "kubeconfig_path" {
  description = "Path to kubeconfig file"
  value       = module.k3s_cluster.kubeconfig_path
}

output "cluster_info" {
  description = "Cluster information"
  value       = module.k3s_cluster.cluster_info
}
