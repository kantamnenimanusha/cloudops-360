variable "region" {
  type = string
}

variable "cluster_version" {
  type        = string
  description = "Kubernetes version in STANDARD support (check the EKS Kubernetes versions page in the AWS docs)"
}

variable "admin_cidrs" {
  type        = list(string)
  description = "Your public IP as a /32, e.g. [\"203.0.113.7/32\"]"
}

variable "key_name" {
  type        = string
  default     = ""
  description = "EC2 key pair for the CI server (required when create_ci_server = true)"

  validation {
    condition     = !var.create_ci_server || trimspace(var.key_name) != ""
    error_message = "Provide an existing EC2 key pair name when create_ci_server is true."
  }
}

variable "private_nodes" {
  type    = bool
  default = false
}

variable "node_count" {
  type    = number
  default = 2
}

variable "create_ci_server" {
  type        = bool
  default     = false
  description = "Explicitly enable the additional billable CI EC2 instance when required."
}
