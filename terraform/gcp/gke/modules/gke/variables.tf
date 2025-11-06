variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
}

variable "machine_type" {
  description = "Machine type for worker nodes"
  type        = string
}

variable "initial_node_count" {
  description = "Initial number of nodes in the cluster"
  type        = number
  default     = 1
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
  type        = string
  default     = "10.0.0.0/24"
}

variable "firewall_ports" {
  description = "Firewall ports to allow"
  type        = list(string)
  default     = ["22", "80", "443", "8080"]
}

variable "firewall_source_ranges" {
  description = "Source ranges for firewall rules"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "firewall_target_tags" {
  description = "Target tags for firewall rules"
  type        = list(string)
  default     = ["gke-node"]
}

variable "disk_size_gb" {
  description = "Disk size in GB for nodes"
  type        = number
  default     = 20
}

variable "disk_type" {
  description = "Disk type for nodes"
  type        = string
  default     = "pd-standard"
}

variable "image_type" {
  description = "Image type for nodes"
  type        = string
  default     = "COS"
}

variable "oauth_scopes" {
  description = "OAuth scopes for nodes"
  type        = list(string)
  default     = ["https://www.googleapis.com/auth/cloud-platform"]
}

variable "node_tags" {
  description = "Tags for nodes"
  type        = list(string)
  default     = ["gke-node"]
}

variable "issue_client_certificate" {
  description = "Whether to issue client certificate"
  type        = bool
  default     = true
}

variable "cluster_ipv4_cidr" {
  description = "CIDR block for cluster IPs"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_ipv4_cidr" {
  description = "CIDR block for service IPs"
  type        = string
  default     = "10.2.0.0/16"
}

variable "enable_private_nodes" {
  description = "Enable private nodes"
  type        = bool
  default     = true
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint"
  type        = bool
  default     = false
}

variable "master_ipv4_cidr" {
  description = "CIDR block for master IPs"
  type        = string
  default     = "172.16.0.0/28"
}

variable "auto_repair" {
  description = "Enable auto repair for node pool"
  type        = bool
  default     = true
}

variable "auto_upgrade" {
  description = "Enable auto upgrade for node pool"
  type        = bool
  default     = true
}

