# 🏦 Credit Score Data Platform

> End-to-end Data Engineering platform for credit risk analytics using Medallion Architecture, PySpark, Apache Airflow and modern data engineering best practices.

## Project Status

🚧 Under development

## Overview

This project builds a data platform for the fictional fintech **Data Girls Finance**, using the Kaggle Credit Score Classification dataset.

The platform follows:

- Medallion Architecture
- Data Quality practices
- Data Governance principles
- LGPD-aware handling
- Dimensional Modeling
- Automated orchestration

## Planned Tech Stack

- Python
- PySpark
- Apache Airflow
- Docker
- MinIO
- AWS S3
- Power BI Desktop
- Pytest
- Ruff
- Black

## Architecture

```text
Kaggle Dataset
      |
      v
Bronze Layer
      |
      v
Silver Layer
      |
      v
Gold Layer
      |
      v
Power BI / Object Storage