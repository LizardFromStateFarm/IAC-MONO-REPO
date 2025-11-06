# Terraform configuration for GCP GKE cluster - Prod
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Module - contains all resources (APIs, Networking, Cluster, Node Pool)
module "gke" {
  source = "../modules/gke"

  project_id              = var.project_id
  region                  = var.region
  cluster_name            = var.cluster_name
  node_count              = var.node_count
  machine_type            = var.machine_type
  initial_node_count      = var.initial_node_count
  subnet_cidr             = var.subnet_cidr
  firewall_ports          = var.firewall_ports
  firewall_source_ranges  = var.firewall_source_ranges
  firewall_target_tags    = var.firewall_target_tags
  disk_size_gb            = var.disk_size_gb
  disk_type               = var.disk_type
  image_type              = var.image_type
  oauth_scopes            = var.oauth_scopes
  node_tags               = var.node_tags
  issue_client_certificate = var.issue_client_certificate
  cluster_ipv4_cidr       = var.cluster_ipv4_cidr
  services_ipv4_cidr      = var.services_ipv4_cidr
  enable_private_nodes    = var.enable_private_nodes
  enable_private_endpoint = var.enable_private_endpoint
  master_ipv4_cidr        = var.master_ipv4_cidr
  auto_repair             = var.auto_repair
  auto_upgrade            = var.auto_upgrade
}

