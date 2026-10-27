variable "monthly_limit_usd" {
  type    = number
  default = 150
}

variable "alert_thresholds_usd" {
  type    = list(number)
  default = [25, 50, 75]
}

variable "email" {
  type = string
}
