terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.90" 
    }
  }

  backend "s3" {
    bucket         = "yqqq-terraform-backend-state"
    key            = "state/terraform.tfstate" 
    region         = "ap-southeast-1" 
  }
}

# AWS
provider "aws" {
  region = "ap-southeast-1"
}

# Snowflake
provider "snowflake" {
  role     = "ACCOUNTADMIN"
}