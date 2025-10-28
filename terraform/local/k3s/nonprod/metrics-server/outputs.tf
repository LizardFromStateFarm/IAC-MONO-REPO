output "namespace" {
  description = "Namespace where metrics server is deployed"
  value       = module.metrics_server.namespace
}

output "service_name" {
  description = "Name of the metrics server service"
  value       = module.metrics_server.service_name
}

output "deployment_name" {
  description = "Name of the metrics server deployment"
  value       = module.metrics_server.deployment_name
}

output "api_service_name" {
  description = "Name of the metrics server API service"
  value       = module.metrics_server.api_service_name
}

output "is_ready" {
  description = "Whether the metrics server is ready"
  value       = module.metrics_server.is_ready
}

output "metrics_server_info" {
  description = "Metrics server information"
  value       = module.metrics_server.metrics_server_info
}
