🎯 Project Overview
Business Problem: Analyze Santander Cycles usage patterns in London to help TfL optimize bike distribution, station placement, and understand rider behavior patterns.

Technical Objective: Build an end-to-end data pipeline that ingests monthly usage data, processes it, stores it in a data warehouse, creates a semantic layer, and visualizes insights through a dashboard.

🛠️ Technology Stack
Core Tools (New in this Project)
Tool Purpose Why We're Using It
Kestra Workflow Orchestration Declarative YAML-based pipelines, built-in UI, simpler than Airflow
DuckDB Embedded Analytics Engine Lightning-fast SQL queries on CSV/Parquet, zero configuration
PostgreSQL Data Warehouse Full-featured SQL database with ACID compliance
Cube.js Semantic Layer Centralized metrics definitions, fast caching layer
Metabase Dashboarding Open-source, user-friendly BI tool

graph LR
A[Traditional Stack] --> B[Complex Python DAGs]
B --> C[Spark Clusters]
C --> D[BigQuery Cloud]
D --> E[Looker Studio]

    F[Modern Stack] --> G[Declarative YAML]
    G --> H[Embedded DuckDB]
    H --> I[PostgreSQL]
    I --> J[Cube.js Layer]
    J --> K[Metabase Dashboards]
