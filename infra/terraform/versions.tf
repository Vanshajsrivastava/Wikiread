terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "wikiread-tfstate-016817716036"
    key            = "wikiread/prod/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "wikiread-tf-lock"
    encrypt        = true
  }
}
