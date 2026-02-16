# Module 4 Homework: Analytics Engineering with dbt

This document contains the setup, answers, and reflections for the Module 4 homework of the Data Engineering Zoomcamp. The work was completed using dbt Cloud, BigQuery, and the NYC TLC taxi data for 2019–2020.

---

## Setup

### 1. Project Configuration

- **dbt Cloud Project:** Connected to the `https://github.com/maheshwarLigade/Data-Engineering-BootCamp-2026/tree/main/04.analytics-engineering`
- **Project Subdirectory:** `04.analytics-engineering/taxi_rides_ny`
- **BigQuery Connection:**
  - Project ID: `your-project-id` (replace with actual project ID)
  - Source Dataset: `nytaxi` (contains raw trip data)
  - Development Schema: `your-dev-schema` (where dbt builds models)

### 2. Data Loading

The following NYC taxi data was loaded into BigQuery:

- **Green taxi data** (2019–2020): ~7.5 million records
- **Yellow taxi data** (2019–2020): ~108 million records
- **FHV data** (2019): ~41 million records

Data source: [DataTalksClub NYC TLC Data repository](https://github.com/DataTalksClub/nyc-tlc-data) (frozen snapshot).

### 3. Key Configuration Changes

**`dbt_project.yml`**

- Updated `require-dbt-version` to support dbt 2.0: `[">=1.7.0", "<3.0.0"]`
- Changed profile from `taxi_rides_ny` to `default`

**`sources.yml`**

- Removed deprecated `freshness` and `loaded_at_field` configurations for dbt 2.0 compatibility
- Added `fhv_tripdata` as a new source

**`stg_green_tripdata.sql` and `stg_yellow_tripdata.sql`**

- Added a date filter to restrict data to 2019–2020:

```sql
where pickup_datetime >= '2019-01-01'
  and pickup_datetime < '2021-01-01'
```

## Answers

## Homework Answers

### Question 1: dbt Lineage and Execution

**Question:** If you run `dbt run --select int_trips_unioned`, what models will be built?

**Answer:** `int_trips_unioned` only.

**Explanation:** The `--select` flag without a `+` prefix builds only the specified model. To include upstream dependencies, you would use `dbt run --select +int_trips_unioned`.

---

### Question 2: dbt Tests

**Question:** A new value `6` appears in `payment_type`. What happens when you run `dbt test --select fct_trips`?

**Answer:** dbt will fail the test, returning a non-zero exit code.

**Explanation:** The `accepted_values` test is a hard constraint. When an unexpected value appears in the data, the test fails and dbt exits with a non-zero code, preventing bad data from moving downstream.

---

### Question 3: Record Count in `fct_monthly_zone_revenue`

**Query:**

```sql
SELECT COUNT(*) as total_records
FROM `your-project-id.your-dev-schema.fct_monthly_zone_revenue`;
```

**Answer:** 12,184

### Question 4: Best Performing Zone for Green Taxis (2020)

**Query:**

```sql
SELECT
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS total_revenue
FROM `your-project-id.your-dev-schema.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 5;
```

**Answer:** East Harlem North

### Question 5: Total Trips for Green Taxis (October 2019)

**Query:**

```sql
SELECT
    SUM(total_monthly_trips) AS total_trips
FROM `your-project-id.your-dev-schema.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND EXTRACT(YEAR FROM revenue_month) = 2019
  AND EXTRACT(MONTH FROM revenue_month) = 10;
```

**Answer:** 500,234

### Question 6: FHV Staging Model Record Count

#### Model Created: models/staging/stg_fhv_tripdata.sql

**Query:**

```sql
with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        dispatching_base_num,
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropOff_datetime as timestamp) as dropoff_datetime,
        cast(PUlocationID as integer) as pickup_location_id,
        cast(DOlocationID as integer) as dropoff_location_id,
        SR_Flag as sr_flag
    from source
    where dispatching_base_num is not null
      and pickup_datetime >= '2019-01-01'
      and pickup_datetime < '2020-01-01'
)

select * from renamed
```

**Query to verify record count:**

```sql
SELECT COUNT(*) as total_records
FROM `your-project-id.your-dev-schema.stg_fhv_tripdata`;
```

**Answer:** 42,084,899

## Conclusion

Module 4 was successfully completed by setting up dbt Cloud with BigQuery, creating staging models with proper data filtering, building fact and dimension tables, implementing data quality tests, and analyzing NYC taxi revenue patterns. The project demonstrates a solid understanding of the Transform layer in ELT pipelines and the importance of data testing in analytics engineering workflows.
