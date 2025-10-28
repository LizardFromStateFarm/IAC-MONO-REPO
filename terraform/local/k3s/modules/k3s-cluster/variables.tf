variable "cluster_name" {
  description = "Name of the K3s cluster"
  type        = string
  default     = "k3s-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version to use"
  type        = string
  default     = "v1.28.0"
}

variable "nodes" {
  description = "Number of control plane nodes"
  type        = number
  default     = 1
}

variable "worker_nodes" {
  description = "Number of worker nodes"
  type        = number
  default     = 0
}

variable "port_mappings" {
  description = "Port mappings for host access"
  type = list(object({
    container_port = number
    host_port      = number
    protocol       = string
  }))
  default = [
    {
      container_port = 80
      host_port      = 8080
      protocol       = "TCP"
    },
    {
      container_port = 443
      host_port      = 8443
      protocol       = "TCP"
    },
    {
      container_port = 30000
      host_port      = 30000
      protocol       = "TCP"
    }
  ]
}

variable "wait_for_ready_timeout" {
  description = "Timeout for waiting for cluster to be ready"
  type        = string
  default     = "300s"
}

variable "node_memory" {
  description = "Memory per node"
  type        = string
  default     = "2Gi"
}

variable "total_memory_limit" {
  description = "Total cluster memory limit"
  type        = string
  default     = "4Gi"
}

variable "disable_components" {
  description = "Components to disable"
  type        = list(string)
  default     = ["traefik", "servicelb"]
}

variable "enable_components" {
  description = "Components to enable"
  type        = list(string)
  default     = ["metrics-server"]
}

variable "podman_runtime" {
  description = "Use Podman instead of Docker"
  type        = bool
  default     = true
}

variable "k3s_image" {
  description = "Custom K3s image"
  type        = string
  default     = null
}

variable "cluster_cidr" {
  description = "Pod network CIDR"
  type        = string
  default     = "10.42.0.0/16"
}

variable "service_cidr" {
  description = "Service network CIDR"
  type        = string
  default     = "10.43.0.0/16"
}

variable "cluster_dns" {
  description = "Cluster DNS IP"
  type        = string
  default     = "10.43.0.10"
}
