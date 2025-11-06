# Terraform configuration for AWS EKS cluster - Prod
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# EKS Module - contains all resources (Networking, IAM, Cluster, Node Group)
module "eks" {
  source = "../modules/eks"

  cluster_name       = var.cluster_name
  kubernetes_version = var.kubernetes_version
  node_count         = var.node_count
  instance_type      = var.instance_type
  vpc_cidr           = var.vpc_cidr
  public_subnet_count = var.public_subnet_count
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  min_size            = var.min_size
  max_size_buffer     = var.max_size_buffer
  tags                = var.tags
}

