variable "name" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "az_count" {
  type    = number
  default = 2
}

variable "private_nodes" {
  type        = bool
  default     = false
  description = "false: nodes in public subnets, no NAT (cheapest). true: nodes in private subnets behind ONE NAT gateway (~$0.05/h + data)."
}
