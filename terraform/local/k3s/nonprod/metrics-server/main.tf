terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

# Get kubeconfig from cluster state
data "terraform_remote_state" "cluster" {
  backend = "local"
  config = {
    path = "../cluster/terraform.tfstate"
  }
}

module "metrics_server" {
  source = "../../modules/metrics-server"

  kubeconfig_path      = data.terraform_remote_state.cluster.outputs.kubeconfig_path
  namespace           = var.namespace
  replicas            = var.replicas
  image              = var.image
  kubelet_insecure_tls = var.kubelet_insecure_tls
}
