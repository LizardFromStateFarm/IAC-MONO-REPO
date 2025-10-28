output "cluster_name" {
  description = "Name of the K3s cluster"
  value       = var.cluster_name
}

output "kubernetes_version" {
  description = "Kubernetes version"
  value       = var.kubernetes_version
}

output "kubeconfig" {
  description = "Kubeconfig content"
  value       = data.local_file.kubeconfig.content
  sensitive   = true
}

output "kubeconfig_path" {
  description = "Path to kubeconfig file"
  value       = local_file.kubeconfig_local.filename
}

output "cluster_info" {
  description = "Cluster information"
  value = {
    cluster_name       = var.cluster_name
    kubernetes_version = var.kubernetes_version
    nodes             = var.nodes
    worker_nodes      = var.worker_nodes
    podman_available  = data.external.podman_check.result.available
  }
}
