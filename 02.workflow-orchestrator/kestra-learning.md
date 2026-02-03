Kestra Learning Notes
Overview
Kestra is an open-source, scalable orchestration and scheduling platform that simplifies data engineering workflows.

Core Concepts

1. Namespace
   Logical grouping of flows (similar to folders)

Used for organization and permissions

Example: sales, marketing, production

2. Flow
   Main workflow definition

Contains tasks and triggers

Written in YAML format

Example structure:

id: my_flow
namespace: dev
tasks: [...]
triggers: [...] 3. Task
Individual unit of work

Built-in and plugin tasks available

Examples: io.kestra.plugin.core.http.Download, io.kestra.plugin.core.log.Log

4. Trigger
   Defines when a flow should execute

Examples: schedule, webhook, flow completion

Can be conditional

5. Plugin
   Extends Kestra's functionality

Available plugins: AWS, GCP, Azure, Databases, etc.

Basic Flow Structure

id: example-flow
namespace: company.data
description: "Example workflow"
tasks:

- id: download-file
  type: io.kestra.plugin.core.http.Download
  uri: "https://example.com/data.csv"

- id: log-message
  type: io.kestra.plugin.core.log.Log
  message: "File downloaded successfully"
  Key Features

1. Declarative YAML
   No coding required for basic workflows

Human-readable configuration

Version control friendly

2. Rich Plugin Ecosystem
   Storage: Local, S3, GCS, Azure Blob

Databases: PostgreSQL, MySQL, BigQuery, Snowflake

Messaging: Kafka, RabbitMQ

Cloud: AWS, GCP, Azure services

3. Execution Models
   Flow: Main workflow execution

Subflow: Reusable flow components

Parallel Execution: Multiple tasks concurrently

Dynamic Tasks: Generate tasks at runtime

4. Error Handling
   Retry mechanisms

Alerting and notifications

Dead letter queues

Task Types
Core Tasks

# HTTP Request

- id: download
  type: io.kestra.plugin.core.http.Download
  uri: "https://example.com/data.csv"

# File Operations

- id: read-file
  type: io.kestra.plugin.core.types.Json
  from: "{{ outputs.download.uri }}"

# Logging

- id: log
  type: io.kestra.plugin.core.log.Log
  message: "Processing complete"

# Script Execution

- id: python-script
  type: io.kestra.plugin.scripts.python.Script
  script: |
  import pandas as pd
  print("Hello from Python!")
  Database Tasks

# Query Database

- id: query-db
  type: io.kestra.plugin.jdbc.postgresql.Query
  url: jdbc:postgresql://localhost:5432/db
  username: user
  password: pass
  sql: "SELECT \* FROM users WHERE created_at > '2024-01-01'"
  Advanced Patterns

1. Variables and Templating

   tasks:

- id: set-vars
  type: io.kestra.plugin.core.debug.Return
  format: "{{ task.id }} started at {{ execution.startDate }}"
- id: use-output
  type: io.kestra.plugin.core.log.Log
  message: "Previous task output: {{ outputs.set-vars.value }}"

2. Conditional Execution

   tasks:

- id: check-condition
  type: io.kestra.plugin.core.condition.Expression
  expression: "{{ execution.startDate | date('HH') | int > 8 }}"

- id: day-task
  type: io.kestra.plugin.core.log.Log
  message: "Running during day hours"
  conditions:
  - type: io.kestra.plugin.core.condition.Expression
    expression: "{{ outputs.check-condition }}"

3. Parallel Processing

   tasks:

- id: parallel-tasks
  type: io.kestra.plugin.core.flow.Parallel
  tasks:

  - id: task1
    type: io.kestra.plugin.core.log.Log
    message: "Task 1"

  - id: task2
    type: io.kestra.plugin.core.log.Log
    message: "Task 2"

4. Error Handling

   tasks:

- id: risky-task
  type: io.kestra.plugin.core.http.Download
  uri: "https://example.com/data.csv"
  retry:
  type: io.kestra.plugin.core.retry.Exponential
  maxAttempt: 3
  maxDelay: PT1M
  timeout: PT5M
  Triggers
  Scheduled Trigger

  triggers:

- id: schedule
  type: io.kestra.plugin.core.trigger.Schedule
  cron: "0 9 \* \* \*" # Daily at 9 AM
  backfill:
  start: 2024-01-01T00:00:00Z
  Flow Trigger

  triggers:

- id: flow-trigger
  type: io.kestra.plugin.core.trigger.Flow
  conditions: - type: io.kestra.plugin.core.condition.Execution
  namespace: sales
  flowId: data-extraction
  states: - SUCCESS
  Webhook Trigger

  triggers:

- id: webhook
  type: io.kestra.plugin.core.trigger.Webhook
  key: my-webhook-key
  Inputs and Outputs
  Flow Inputs

  inputs:

- name: filename
  type: STRING
  required: true
  defaults: "data.csv"

- name: process_date
  type: DATETIME
  required: false

tasks:

- id: process
  type: io.kestra.plugin.core.log.Log
  message: "Processing {{ inputs.filename }} for {{ inputs.process_date }}"
  Task Outputs

  tasks:

- id: generate-data
  type: io.kestra.plugin.core.debug.Return
  format: "output-data-{{ execution.id }}"

- id: use-data
  type: io.kestra.plugin.core.log.Log
  message: "Generated data: {{ outputs.generate-data.value }}"
  Real-World Examples
  ETL Pipeline

  id: etl-pipeline
  namespace: data.engineering

tasks:

# Extract

- id: extract
  type: io.kestra.plugin.core.http.Download
  uri: "https://data.source.com/{{ execution.date | date('yyyy-MM') }}.csv"

# Transform

- id: transform
  type: io.kestra.plugin.scripts.python.Script
  inputFiles:
  data.csv: "{{ outputs.extract.uri }}"
  script: |
  import pandas as pd
  df = pd.read_csv('data.csv')
  # Transformation logic
  df.to_csv('transformed.csv', index=False)

# Load

- id: load
  type: io.kestra.plugin.jdbc.postgresql.Load
  from: "{{ outputs.transform.outputFiles['transformed.csv'] }}"
  url: jdbc:postgresql://localhost:5432/warehouse
  username: user
  password: pass
  table: processed_data
  Data Quality Check

  id: data-quality
  namespace: quality

tasks:

- id: check-nulls
  type: io.kestra.plugin.jdbc.postgresql.Query
  sql: |
  SELECT
  COUNT(\*) as total_rows,
  SUM(CASE WHEN column1 IS NULL THEN 1 ELSE 0 END) as null_count
  FROM source_table
  fetch: true

- id: validate
  type: io.kestra.plugin.core.condition.Expression
  expression: "{{ outputs.check-nulls.rows[0]['null_count'] | int == 0 }}"

- id: alert
  type: io.kestra.plugin.core.log.Log
  message: "Data quality check failed: null values found"
  conditions: - type: io.kestra.plugin.core.condition.Expression
  expression: "{{ not outputs.validate.value }}"
  Best Practices

1. Organization
   Use meaningful namespaces

Version control your flows

Document flows with descriptions

2. Error Handling
   Implement retry mechanisms

Set appropriate timeouts

Use dead letter queues for failed messages

3. Performance
   Use parallel execution where possible

Implement caching for expensive operations

Monitor execution metrics

4. Security
   Use secrets for sensitive data

Implement proper access controls

Audit flow executions

Monitoring and Debugging

1. Execution Logs
   View real-time execution logs

Search and filter capabilities

Download logs for analysis

2. Metrics
   Execution duration

Success/failure rates

Resource utilization

3. Alerts
   Email notifications

Webhook integrations

Custom alert conditions

CLI Commands
bash

# List namespaces

kestra namespaces list

# List flows

kestra flows list --namespace company.data

# Execute flow

kestra flows execute --namespace company.data --flow etl-pipeline

# View execution

kestra executions get --id <execution-id>

# Follow logs

kestra executions logs --id <execution-id> --follow
Integration Patterns

1. CI/CD Integration
   Store flows in Git

Automated testing of flows

Deployment pipelines

2. API Integration
   REST API for flow management

Webhook triggers

Custom plugin development

3. Cloud Integration
   Deploy on Kubernetes

Use cloud storage

Integrate with cloud services

Common Issues and Solutions

1. Task Timeout

# Increase timeout

timeout: PT30M # 30 minutes 2. Memory Issues

# Limit task resources

taskDefaults:
runConfig:
memory: 512Mi 3. Dependency Management

# Python dependencies

type: io.kestra.plugin.scripts.python.Script
docker:
image: python:3.9-slim
Learning Resources
Official Documentation
Kestra Docs

Plugin Reference

API Reference

Community
GitHub Repository

Slack Community

Blog & Tutorials

Example Repositories
Kestra Examples

Templates Gallery

Quick Reference
YAML Structure

id: flow-id
namespace: your.namespace
description: "Flow description"
inputs: [...]
tasks: [...]
triggers: [...]
taskDefaults: [...]
Common Task Types
io.kestra.plugin.core.http.\* - HTTP operations

io.kestra.plugin.core.log.\* - Logging

io.kestra.plugin.core.condition.\* - Conditions

io.kestra.plugin.scripts.\* - Script execution

io.kestra.plugin.jdbc.\* - Database operations

Time Format
PT30S - 30 seconds

PT5M - 5 minutes

PT2H - 2 hours

P1D - 1 day

This guide provides a comprehensive overview of Kestra for data orchestration. Start with simple flows and gradually incorporate more complex patterns as needed.
