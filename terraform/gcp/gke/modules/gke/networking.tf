# VPC Network
resource "google_compute_network" "gke_vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.compute_api]
}

# Subnet
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${var.cluster_name}-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.gke_vpc.id
}

# Firewall rule for GKE
resource "google_compute_firewall" "gke_firewall" {
  name    = "${var.cluster_name}-firewall"
  network = google_compute_network.gke_vpc.name

  allow {
    protocol = "tcp"
    ports    = var.firewall_ports
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = var.firewall_source_ranges
  target_tags   = var.firewall_target_tags
}

