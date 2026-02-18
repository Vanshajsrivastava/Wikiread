locals {
  name = "${var.project}-${var.environment}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  nat_gateway_count_effective = min(var.nat_gateway_count, var.az_count)
}
