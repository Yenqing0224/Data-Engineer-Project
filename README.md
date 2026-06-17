# 🚀 Crypto Data Engineering Pipeline

A modern ELT data platform built using Snowflake, dbt, Airflow, Terraform, and AWS.

## Overview
This project is an end-to-end Data Engineering platform designed to ingest, transform, and analyze cryptocurrency market data through a scalable cloud-native architecture.

It demonstrates a production-style data pipeline workflow using Infrastructure as Code (IaC), workflow orchestration, cloud data warehousing, automated data transformation, and data quality validation.

The platform focuses on building reliable and maintainable data systems by implementing automated ingestion, modular data modeling, incremental processing, and analytics-ready datasets.

---

# Architecture

<img width="1495" height="971" alt="Data Pipeline Arhitecture" src="https://github.com/user-attachments/assets/9151d118-aaff-47f6-b559-fcf93bf226da" />

## Airflow Orchestration

Apache Airflow manages the end-to-end pipeline workflow.

The DAG coordinates:

<img width="946" height="348" alt="Screenshot 2026-06-17 140526" src="https://github.com/user-attachments/assets/1c58e058-bd72-4c9f-966e-454cbfe7fd93" />

The DAG provides:

* Task dependency management
* Pipeline scheduling
* Retry handling
* Execution monitoring
* Failure handling

## Data Flow

CoinGecko API
→ AWS S3 (Raw Data Lake)
→ Snowflake RAW Layer
→ dbt Staging Models
→ dbt Mart Models
→ Streamlit Dashboard

The pipeline follows an ELT architecture:

* Extract data from CoinGecko API
* Load raw JSON into AWS S3
* Ingest semi-structured data into Snowflake
* Transform data with dbt
* Serve analytical datasets to Streamlit

---

# Tech Stack

| Component              | Technology     |
| ---------------------- | -------------- |
| Programming Language   | Python         |
| Data Lake              | AWS S3         |
| Data Warehouse         | Snowflake      |
| Transformation         | dbt            |
| Orchestration          | Apache Airflow |
| Infrastructure as Code | Terraform      |
| CI/CD                  | GitHub Actions |
| Visualization          | Streamlit      |

---

# Key Features

## Infrastructure as Code

Terraform provisions:

* Snowflake Database
* Snowflake Schema
* Snowflake Warehouse
* AWS Resources

Infrastructure changes are version-controlled and deployed through GitHub Actions.

---

## Automated Orchestration

Apache Airflow orchestrates:

1. Data extraction
2. S3 ingestion
3. Snowflake loading
4. dbt transformations
5. Data quality validation

---

## Incremental Processing

The dbt staging layer uses incremental models to:

* Process only newly ingested files
* Avoid full-table rebuilds
* Reduce Snowflake compute costs
* Support scalable historical data growth

---

## Semi-Structured Data Processing

Raw CoinGecko JSON is stored using Snowflake VARIANT columns.

dbt models use:

* LATERAL FLATTEN
* ARRAY processing
* Incremental MERGE strategies

to transform nested JSON into analytics-ready tables.

---

# Data Model

<img width="400" height="708" alt="dbt-dag" src="https://github.com/user-attachments/assets/c0995372-bf85-4454-918f-dd0f03ea480a" />


## Layers

### RAW

Stores original API payloads.

Characteristics:

* Append-only
* No transformations
* Full auditability

---

### STAGING

Performs:

* JSON flattening
* Type casting
* Timestamp normalization
* Deduplication

Output:

* One row per coin per timestamp

---

### MARTS

Business-ready analytical models.

Examples:

* Daily closing price
* Market capitalization trends
* Volume analysis
* Rolling averages

---

# Data Quality

dbt tests enforce:

* not_null
* unique
* accepted_values
* relationship integrity

Data quality checks run automatically during pipeline execution.

---


# Security

Implemented:

* Least Privilege IAM Policies
* Secrets managed through GitHub Actions
* No credentials stored in repository

---
# Dashboard

<img width="1907" height="913" alt="Screenshot 2026-06-17 134954" src="https://github.com/user-attachments/assets/c3e883ea-8ae1-4096-a213-29fa5b047e38" />

The dashboard provides:

* Historical price trends
* Market cap analysis
* Volume monitoring

---

# Challenges Solved

## GitOps Deployment

Implemented CI/CD deployment using:

* Terraform
* GitHub Actions
* Remote Terraform State

---

## Incremental ELT Design

Designed a scalable ingestion strategy that:

* Preserves raw historical files
* Supports late-arriving data
* Prevents duplicate records

---

# Repository Structure

```text
project/
├── .github/            # CI/CD pipelines (GitHub Actions)
├── airflow/            # Workflows orchestration (DAGs)
├── dashboard/          # Streamlit application
├── dbt_transform/      # Data modeling & quality tests (dbt)
├── snowflake/          # Snowflake configuration scripts
├── src/                # Data Extraction and Ingestion scripts
├── terraform/          # Infrastructure as Code (IaC)
└── requirements.txt    # Dependencies management
```

---

# Author

Built as part of a Data Engineering portfolio project focused on modern cloud-native data platform design.
