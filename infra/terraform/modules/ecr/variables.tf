variable "repositories" {
  type    = list(string)
  default = ["cloudops/orders-service", "cloudops/inventory-service", "cloudops/cloudops-backend", "cloudops/cloudops-frontend"]
}

variable "keep_last" {
  type    = number
  default = 15
}
