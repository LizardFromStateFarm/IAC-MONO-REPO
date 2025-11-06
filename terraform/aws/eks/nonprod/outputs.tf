output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes version"
  value       = module.eks.cluster_version
}

output "cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.eks.vpc_id
}

output "subnet_ids" {
  description = "IDs of the subnets"
  value       = module.eks.subnet_ids
}

