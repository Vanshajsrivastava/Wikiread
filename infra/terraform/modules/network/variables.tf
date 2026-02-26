variable "name" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

variable "vpc_cidr" {
  type = string
}

variable "az_count" {
  type = number
}

variable "nat_gateway_count" {
  type = number
}
