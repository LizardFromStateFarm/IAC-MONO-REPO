variable "namespace" {
  description = "Namespace for metrics server"
  type        = string
  default     = "kube-system"
}

variable "replicas" {
  description = "Number of replicas"
  type        = number
  default     = 1
}

variable "image" {
  description = "Metrics server image"
  type        = string
  default     = "registry.k8s.io/metrics-server/metrics-server:v0.6.4"
}

variable "kubelet_insecure_tls" {
  description = "Use insecure TLS for kubelet (K3s specific)"
  type        = bool
  default     = true
}
