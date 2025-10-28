output "namespace" {
  description = "Namespace where metrics server is deployed"
  value       = var.namespace
}

output "service_name" {
  description = "Name of the metrics server service"
  value       = kubernetes_service.metrics_server.metadata[0].name
}

output "deployment_name" {
  description = "Name of the metrics server deployment"
  value       = kubernetes_deployment.metrics_server.metadata[0].name
}

output "api_service_name" {
  description = "Name of the metrics server API service"
  value       = kubernetes_api_service.metrics_server.metadata[0].name
}

output "is_ready" {
  description = "Whether the metrics server is ready"
  value       = kubernetes_deployment.metrics_server.status[0].ready_replicas > 0
}

output "metrics_server_info" {
  description = "Metrics server information"
  value = {
    enabled   = true
    namespace = var.namespace
    ready     = kubernetes_deployment.metrics_server.status[0].ready_replicas > 0
    status    = kubernetes_deployment.metrics_server.status[0].ready_replicas > 0 ? "ready" : "starting"
  }
}
