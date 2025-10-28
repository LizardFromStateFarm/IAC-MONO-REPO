terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

# Kubernetes provider
provider "kubernetes" {
  config_path = var.kubeconfig_path
}

# ServiceAccount
resource "kubernetes_service_account" "metrics_server" {
  metadata {
    name      = "metrics-server"
    namespace = var.namespace
    labels = {
      "k8s-app" = "metrics-server"
    }
  }
}

# ClusterRole for aggregated metrics reader
resource "kubernetes_cluster_role" "aggregated_metrics_reader" {
  metadata {
    name = "system:aggregated-metrics-reader"
    labels = {
      "rbac.authorization.k8s.io/aggregate-to-view"  = "true"
      "rbac.authorization.k8s.io/aggregate-to-edit"  = "true"
      "rbac.authorization.k8s.io/aggregate-to-admin" = "true"
    }
  }

  rule {
    api_groups = ["metrics.k8s.io"]
    resources  = ["pods", "nodes"]
    verbs      = ["get", "list"]
  }
}

# ClusterRole for metrics server
resource "kubernetes_cluster_role" "metrics_server" {
  metadata {
    name = "system:metrics-server"
    labels = {
      "k8s-app" = "metrics-server"
    }
  }

  rule {
    api_groups = [""]
    resources  = ["nodes/metrics"]
    verbs      = ["get"]
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "nodes"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = [""]
    resources  = ["configmaps"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["metrics.k8s.io"]
    resources  = ["*"]
    verbs      = ["get", "list"]
  }

  rule {
    api_groups = [""]
    resources  = ["nodes/stats"]
    verbs      = ["get"]
  }

  rule {
    api_groups = ["apiextensions.k8s.io"]
    resources  = ["customresourcedefinitions"]
    verbs      = ["get", "list"]
  }
}

# RoleBinding for auth reader
resource "kubernetes_role_binding" "auth_reader" {
  metadata {
    name      = "metrics-server-auth-reader"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = "extension-apiserver-authentication-reader"
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.metrics_server.metadata[0].name
    namespace = var.namespace
  }
}

# ClusterRoleBinding for auth delegator
resource "kubernetes_cluster_role_binding" "auth_delegator" {
  metadata {
    name = "metrics-server:system:auth-delegator"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "system:auth-delegator"
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.metrics_server.metadata[0].name
    namespace = var.namespace
  }
}

# ClusterRoleBinding for metrics server
resource "kubernetes_cluster_role_binding" "metrics_server" {
  metadata {
    name = "system:metrics-server"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.metrics_server.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.metrics_server.metadata[0].name
    namespace = var.namespace
  }
}

# Service
resource "kubernetes_service" "metrics_server" {
  metadata {
    name      = "metrics-server"
    namespace = var.namespace
    labels = {
      "k8s-app" = "metrics-server"
    }
  }

  spec {
    selector = {
      "k8s-app" = "metrics-server"
    }

    port {
      port        = 443
      protocol    = "TCP"
      target_port = 4443
    }
  }
}

# Deployment
resource "kubernetes_deployment" "metrics_server" {
  metadata {
    name      = "metrics-server"
    namespace = var.namespace
    labels = {
      "k8s-app" = "metrics-server"
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        "k8s-app" = "metrics-server"
      }
    }

    strategy {
      rolling_update {
        max_unavailable = 0
      }
    }

    template {
      metadata {
        name = "metrics-server"
        labels = {
          "k8s-app" = "metrics-server"
        }
      }

      spec {
        service_account_name = kubernetes_service_account.metrics_server.metadata[0].name

        volume {
          name = "tmp-dir"
          empty_dir {}
        }

        container {
          name  = "metrics-server"
          image = var.image
          image_pull_policy = "IfNotPresent"

          args = var.kubelet_insecure_tls ? [
            "--cert-dir=/tmp",
            "--secure-port=4443",
            "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
            "--kubelet-use-node-status-port",
            "--metric-resolution=15s",
            "--kubelet-insecure-tls"
          ] : [
            "--cert-dir=/tmp",
            "--secure-port=4443",
            "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
            "--kubelet-use-node-status-port",
            "--metric-resolution=15s"
          ]

          port {
            name           = "https"
            container_port = 4443
            protocol       = "TCP"
          }

          readiness_probe {
            http_get {
              path   = "/readyz"
              port   = "https"
              scheme = "HTTPS"
            }
            period_seconds    = 10
            failure_threshold = 3
          }

          liveness_probe {
            http_get {
              path   = "/livez"
              port   = "https"
              scheme = "HTTPS"
            }
            period_seconds    = 10
            failure_threshold = 3
          }

          volume_mount {
            name       = "tmp-dir"
            mount_path = "/tmp"
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "200Mi"
            }
            limits = {
              cpu    = "100m"
              memory = "200Mi"
            }
          }
        }

        node_selector = {
          "kubernetes.io/os" = "linux"
        }

        toleration {
          key      = "node-role.kubernetes.io/control-plane"
          operator = "Exists"
          effect   = "NoSchedule"
        }

        toleration {
          key      = "node-role.kubernetes.io/master"
          operator = "Exists"
          effect   = "NoSchedule"
        }
      }
    }
  }

  depends_on = [
    kubernetes_service_account.metrics_server,
    kubernetes_cluster_role.aggregated_metrics_reader,
    kubernetes_cluster_role.metrics_server,
    kubernetes_role_binding.auth_reader,
    kubernetes_cluster_role_binding.auth_delegator,
    kubernetes_cluster_role_binding.metrics_server
  ]
}

# APIService
resource "kubernetes_api_service" "metrics_server" {
  metadata {
    name = "v1beta1.metrics.k8s.io"
    labels = {
      "k8s-app" = "metrics-server"
    }
  }

  spec {
    service {
      name      = kubernetes_service.metrics_server.metadata[0].name
      namespace = var.namespace
      port      = 443
    }
    group                   = "metrics.k8s.io"
    version                 = "v1beta1"
    insecure_skip_tls_verify = true
    group_priority_minimum  = 100
    version_priority        = 100
  }

  depends_on = [
    kubernetes_service.metrics_server,
    kubernetes_deployment.metrics_server
  ]
}
