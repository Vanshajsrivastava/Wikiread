terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configure S3 backend after first bootstrap.
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "wikiread/prod/terraform.tfstate"
  #   region         = "eu-west-2"
  #   dynamodb_table = "your-terraform-lock-table"
  #   encrypt        = true
  # }
}
