variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.large" # Jenkins + SonarQube need ~6 GB RAM
}

variable "key_name" {
  type        = string
  description = "Existing EC2 key pair name (used by Ansible over SSH)."
}

variable "admin_cidrs" {
  type = list(string)
  validation {
    condition     = !contains(var.admin_cidrs, "0.0.0.0/0")
    error_message = "Do not expose the CI server to the whole internet."
  }
}

variable "ecr_repository_arns" {
  type        = list(string)
  description = "ECR repositories the CI role may push to."
}
