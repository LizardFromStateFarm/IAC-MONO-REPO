terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

module "k3s_cluster" {
  source = "../../modules/k3s-cluster"

  cluster_name        = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  nodes              = var.nodes
  worker_nodes       = var.worker_nodes
  port_mappings      = var.port_mappings
  wait_for_ready_timeout = var.wait_for_ready_timeout
  node_memory        = var.node_memory
  total_memory_limit = var.total_memory_limit
  disable_components = var.disable_components
  enable_components  = var.enable_components
  podman_runtime     = var.podman_runtime
  k3s_image         = var.k3s_image
  cluster_cidr      = var.cluster_cidr
  service_cidr      = var.service_cidr
  cluster_dns       = var.cluster_dns
}
