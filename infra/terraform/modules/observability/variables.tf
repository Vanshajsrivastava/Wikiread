variable "name" {
  type = string
}

variable "common_tags" {
  type = map(string)
}

variable "cluster_name" {
  type = string
}

variable "oidc_provider_arn" {
  type = string
}

variable "cluster_oidc_issuer_url" {
  type = string
}

variable "enable_metrics_server_addon" {
  type = bool
}

variable "enable_cloudwatch_observability_addon" {
  type = bool
}
