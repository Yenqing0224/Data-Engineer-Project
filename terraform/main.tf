# AWS
# Create S3 Data Lake
resource "aws_s3_bucket" "crypto_bucket" {
  bucket        = var.bucket_name
  force_destroy = true
  tags = {
    Name        = "Crypto Data Lake"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket" "test_bucket" {
  bucket        = "yqqq-crypto-data-lake-test"
  force_destroy = true
  tags = {
    Name        = "Crypto Data Lake"
    Environment = "Dev"
  }
}

# Snowflake
# Create DB
resource "snowflake_database" "crypto_db" {
  name    = "CRYPTO_DB"
  comment = "Database for Cryptocurrency Data Ingestion"
}

# Create SChema for DB
resource "snowflake_schema" "raw_schema" {
  database   = snowflake_database.crypto_db.name
  name       = "RAW"
}

# Create Warehouse
resource "snowflake_warehouse" "crypto_wh" {
  name           = "CRYPTO_WH"
  warehouse_size = "XSMALL"
  auto_suspend   = 60       
  auto_resume    = true     
  initially_suspended = true    
}