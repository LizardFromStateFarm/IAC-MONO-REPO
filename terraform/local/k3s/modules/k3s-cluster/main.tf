terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

# Check if Podman is available
data "external" "podman_check" {
  program = ["powershell", "-Command", "try { podman --version | Out-Null; Write-Output '{\"available\": \"true\"}' } catch { Write-Output '{\"available\": \"false\"}' }"]
}

# Create K3s cluster using local-exec provisioner
resource "null_resource" "k3s_cluster" {
  triggers = {
    cluster_name     = var.cluster_name
    kubernetes_version = var.kubernetes_version
    nodes           = var.nodes
    worker_nodes    = var.worker_nodes
    podman_available = data.external.podman_check.result.available
  }

  provisioner "local-exec" {
    command = data.external.podman_check.result.available == "true" ? 
      "k3s server --cluster-init --write-kubeconfig-mode=644 --config=-" :
      "k3s server --cluster-init --write-kubeconfig-mode=644 --config=-"
    
    working_dir = path.module
  }

  provisioner "local-exec" {
    when = destroy
    command = "k3s server --cluster-reset"
    working_dir = path.module
  }
}

# Wait for cluster to be ready
resource "null_resource" "k3s_ready" {
  depends_on = [null_resource.k3s_cluster]

  provisioner "local-exec" {
    command = "kubectl wait --for=condition=Ready nodes --all --timeout=${var.wait_for_ready_timeout}"
  }

  triggers = {
    cluster_name = var.cluster_name
  }
}

# Get kubeconfig
data "local_file" "kubeconfig" {
  depends_on = [null_resource.k3s_ready]
  filename   = pathexpand("~/.kube/config")
}

# Create kubeconfig file in current directory for reference
resource "local_file" "kubeconfig_local" {
  depends_on = [null_resource.k3s_ready]
  content    = data.local_file.kubeconfig.content
  filename   = "${path.module}/kubeconfig"
}
