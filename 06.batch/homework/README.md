# Module 6 Homework

## Question 1: Install Spark and PySpark

> Install PySpark follow this [guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/06-batch/setup/)
>
> - Install Spark
> - Run PySpark
> - Create a local spark session
> - Execute spark.version.
>   What's the output?

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('homework') \
    .getOrCreate()

print(f"Spark version: {spark.version}")
```

```
Spark version: 3.5.8
```

The output is **3.5.8**.

## Question 2: Yellow November 2025

> Read the November 2025 Yellow into a Spark Dataframe.
>
> Repartition the Dataframe to 4 partitions and save it to parquet.
>
> What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)?

```python
!mkdir -p /data/homework/raw
!mkdir -p /data/homework/parquet

!wget -nc https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet \
    -O /data/homework/raw/yellow_tripdata_2025-11.parquet
```

```python
# Read the November 2025 Yellow into a Spark Dataframe.
df_trips = spark.read.parquet('/data/homework/raw/*.parquet')

# Repartition the Dataframe to 4 partitions and save it to parquet.
df_trips.repartition(4).write.parquet('/data/homework/parquet', mode='overwrite')
```

```python
# What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)?
!ls -lh /data/homework/parquet/*.parquet
```

```
-rw-r--r-- 1 root root 25M Mar  7 11:24 /data/homework/parquet/part-00000-7ef2f8c4-626d-4401-8cc4-97eb59ad5841-c000.snappy.parquet
-rw-r--r-- 1 root root 25M Mar  7 11:24 /data/homework/parquet/part-00001-7ef2f8c4-626d-4401-8cc4-97eb59ad5841-c000.snappy.parquet
-rw-r--r-- 1 root root 25M Mar  7 11:24 /data/homework/parquet/part-00002-7ef2f8c4-626d-4401-8cc4-97eb59ad5841-c000.snappy.parquet
-rw-r--r-- 1 root root 25M Mar  7 11:24 /data/homework/parquet/part-00003-7ef2f8c4-626d-4401-8cc4-97eb59ad5841-c000.snappy.parquet
```

> Select the answer which most closely matches.
>
> - 6MB
> - 25MB
> - 75MB
> - 100MB

The average size is **25MB**.

## Question 3: Count records

> How many taxi trips were there on the 15th of November?
>
> Consider only trips that started on the 15th of November.

```python
from pyspark.sql import functions as F

df_trips = df_trips.withColumn('pickup_date', F.to_date(df_trips.tpep_pickup_datetime))
df_trips.filter(df_trips.pickup_date == '2025-11-15').count()
```

```
162604
```

The number of trips started on the 15th of November is:

- **162,604**

## Question 4: Longest trip

> What is the length of the longest trip in the dataset in hours?

- 22.7
- 58.2
- 90.6
- 134.5

```python
from pyspark.sql import types
from datetime import datetime

def duration(start: datetime, end: datetime) -> int:
    # Difference in minutes (absolute value to support inverted values)
    minutes = abs((end - start).total_seconds()) / 60

    # Conversion to hours
    hours = minutes / 60

    return hours

duration_udf = F.udf(duration, returnType=types.FloatType())

df_trips \
    .withColumn('duration_hours', duration_udf(df_trips.tpep_pickup_datetime, df_trips.tpep_dropoff_datetime)) \
    .groupBy() \
    .max('duration_hours') \
    .show()
```

```
+-------------------+
|max(duration_hours)|
+-------------------+
|           90.64667|
+-------------------+
```

The answer is **90.6**.

## Question 5: User Interface

> Spark's User Interface which shows the application's dashboard runs on which local port?

It runs on port **4040**.

## Question 6: Least frequent pickup location zone

> Load the zone lookup data into a temp view in Spark.

```python
!wget -nc https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv \
    -O /data/homework/raw/taxi_zone_lookup.csv
```

```python
df_zones = spark.read.csv('/data/homework/raw/taxi_zone_lookup.csv', header=True)

df_trips.createOrReplaceTempView('trips')
df_zones.createOrReplaceTempView('zones')

spark.sql("""
WITH trips_by_pickup_location AS (
    SELECT PULocationID, COUNT(*) AS trip_count
    FROM trips
    GROUP BY PULocationID
    ORDER BY trip_count
)
SELECT z.Zone, SUM(t.trip_count) AS trip_count
FROM zones AS z
LEFT JOIN trips_by_pickup_location AS t ON t.PULocationID = z.LocationID
GROUP BY z.Zone
ORDER BY trip_count
""").show(truncate=False)
```

```
+---------------------------------------------+----------+
|Zone                                         |trip_count|
+---------------------------------------------+----------+
|Charleston/Tottenville                       |NULL      |
|Freshkills Park                              |NULL      |
|Great Kills Park                             |NULL      |
|Governor's Island/Ellis Island/Liberty Island|1         |
|Eltingville/Annadale/Prince's Bay            |1         |
|Arden Heights                                |1         |
|Port Richmond                                |3         |
|Rikers Island                                |4         |
|Rossville/Woodrow                            |4         |
|Great Kills                                  |4         |
|Green-Wood Cemetery                          |4         |
|Jamaica Bay                                  |5         |
|Westerleigh                                  |12        |
|West Brighton                                |14        |
|New Dorp/Midland Beach                       |14        |
|Oakwood                                      |14        |
|Crotona Park                                 |14        |
|Willets Point                                |15        |
|Breezy Point/Fort Tilden/Riis Beach          |16        |
|Saint George/New Brighton                    |17        |
+---------------------------------------------+----------+
only showing top 20 rows
```

> Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?

The 3 zones with the least number of trips are these zones, which had no trip recorded during that period:

- **Charleston/Tottenville**
- **Freshkills Park**
- **Great Kills Park**

Then, these 3 zones had only one trip recorded:

- **Governor's Island/Ellis Island/Liberty Island**
- **Eltingville/Annadale/Prince's Bay**
- **Arden Heights**

For **Rikers Island** 4 trips were recorded and for **Jamaica Bay** there were 5.

## Submitting the solutions

- Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw6
- Deadline: See the website
