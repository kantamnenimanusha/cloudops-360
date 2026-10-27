variable "name" {
  type = string
}

variable "cluster_version" {
  type        = string
  description = "Kubernetes version. MUST be in standard support (extended support costs 6x). Check the EKS release calendar."
}

variable "cluster_subnet_ids" {
  type = list(string)
}

variable "node_subnet_ids" {
  type = list(string)
}

variable "admin_cidrs" {
  type        = list(string)
  description = "CIDRs allowed to reach the public Kubernetes API endpoint (your IP as x.x.x.x/32)."
  validation {
    condition     = !contains(var.admin_cidrs, "0.0.0.0/0")
    error_message = "Do not expose the Kubernetes API to the whole internet."
  }
}

variable "instance_types" {
  type    = list(string)
  default = ["t3.large"]
}

variable "desired_nodes" {
  type    = number
  default = 2
}

variable "max_nodes" {
  type    = number
  default = 3
}

variable "disk_size_gb" {
  type    = number
  default = 30
}

variable "app_namespace" {
  type    = string
  default = "cloudops"
}

variable "backend_service_account" {
  type    = string
  default = "cloudops-backend"
}
