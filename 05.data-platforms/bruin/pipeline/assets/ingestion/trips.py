"""@bruin

# TODO: Set the asset name (recommended pattern: schema.asset_name).
# - Convention in this module: use an `ingestion.` schema for raw ingestion tables.
name: ingestion.trips

# TODO: Set the asset type.
# Docs: https://getbruin.com/docs/bruin/assets/python
type: python

# TODO: Pick a Python image version (Bruin runs Python in isolated environments).
# Example: python:3.11
image: python:3.11

# TODO: Set the connection.
connection: duckdb-default

# TODO: Choose materialization (optional, but recommended).
# Bruin feature: Python materialization lets you return a DataFrame (or list[dict]) and Bruin loads it into your destination.
# This is usually the easiest way to build ingestion assets in Bruin.
# Alternative (advanced): you can skip Bruin Python materialization and write a "plain" Python asset that manually writes
# into DuckDB (or another destination) using your own client library and SQL. In that case:
# - you typically omit the `materialization:` block
# - you do NOT need a `materialize()` function; you just run Python code
# Docs: https://getbruin.com/docs/bruin/assets/python#materialization
materialization:
  # TODO: choose `table` or `view` (ingestion generally should be a table)
  type: table
  # TODO: pick a strategy.
  # suggested strategy: append
  strategy: append

# TODO: Define output columns (names + types) for metadata, lineage, and quality checks.
# Tip: mark stable identifiers as `primary_key: true` if you plan to use `merge` later.
# Docs: https://getbruin.com/docs/bruin/assets/columns
# currently use default
#columns:
#  - name: TODO_col1
#    type: TODO_type
#    description: TODO

@bruin"""

# TODO: Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python


# TODO: Only implement `materialize()` if you are using Bruin Python materialization.
# If you choose the manual-write approach (no `materialization:` block), remove this function and implement ingestion
# as a standard Python script instead.

import os
import json
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def generate_month_range(start_date: str, end_date: str):
    """Generate first-day-of-month dates between start and end."""
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(day=1)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(day=1)

    current = start
    while current <= end:
        yield current
        current += relativedelta(months=1)


def build_endpoint(taxi_type: str, year: int, month: int):
    """
    Example endpoint builder for NYC TLC parquet files.
    Adjust base URL if needed.
    """
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    return f"{base_url}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"


def materialize():
    """
    TODO: Implement ingestion using Bruin runtime context.

    Required Bruin concepts to use here:
    - Built-in date window variables:
      - BRUIN_START_DATE / BRUIN_END_DATE (YYYY-MM-DD)
      - BRUIN_START_DATETIME / BRUIN_END_DATETIME (ISO datetime)
      Docs: https://getbruin.com/docs/bruin/assets/python#environment-variables
    - Pipeline variables:
      - Read JSON from BRUIN_VARS, e.g. `taxi_types`
      Docs: https://getbruin.com/docs/bruin/getting-started/pipeline-variables

    Design TODOs (keep logic minimal, focus on architecture):
    - Use start/end dates + `taxi_types` to generate a list of source endpoints for the run window.
    - Fetch data for each endpoint, parse into DataFrames, and concatenate.
    - Add a column like `extracted_at` for lineage/debugging (timestamp of extraction).
    - Prefer append-only in ingestion; handle duplicates in staging.
    """
    # return final_dataframe
    


    # ---- 1. Read Bruin built-in window ----
    start_date = os.environ.get("BRUIN_START_DATE")
    end_date = os.environ.get("BRUIN_END_DATE")

    if not start_date or not end_date:
        raise ValueError("BRUIN_START_DATE and BRUIN_END_DATE must be set.")

    # ---- 2. Read pipeline variables ----
    vars_json = os.environ.get("BRUIN_VARS", "{}")
    pipeline_vars = json.loads(vars_json)

    taxi_types = pipeline_vars.get("taxi_types", ["yellow", "green"])

    all_dfs = []

    # ---- 3. Generate endpoints for time window ----
    for month_dt in generate_month_range(start_date, end_date):
        year = month_dt.year
        month = month_dt.month

        for taxi_type in taxi_types:
            endpoint = build_endpoint(taxi_type, year, month)
            print(f"Fetching: {endpoint}")

            try:
                df = pd.read_parquet(endpoint)

                # ---- 4. Add lineage column ----
                df["extracted_at"] = datetime.utcnow()

                # Optional metadata
                df["source_taxi_type"] = taxi_type
                df["source_year"] = year
                df["source_month"] = month

                all_dfs.append(df)

            except Exception as e:
                print(f"Failed to fetch {endpoint}: {e}")

    # ---- 5. Concatenate ----
    if not all_dfs:
        return pd.DataFrame()

    final_dataframe = pd.concat(all_dfs, ignore_index=True)

    # NOTE:
    # - This is append-only ingestion.
    # - Deduplication should happen in staging/transform layer.
    # - Downstream model can use time_interval strategy.

    return final_dataframe

