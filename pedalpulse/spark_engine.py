"""Spark session setup, CSV cleaning, and all trip aggregations."""
import os
import sys
import time

import pandas as pd
from pyspark.sql import SparkSession, functions as F

REQUIRED_COLUMNS = ["start_time", "tripduration", "from_station_name", "usertype"]
DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def create_spark():
    """Start one local Spark session and use this Python executable for workers."""
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    return (SparkSession.builder.master("local[*]").appName("PedalPulse")
            .config("spark.sql.shuffle.partitions", "8")
            .config("spark.ui.enabled", "false").getOrCreate())


def load_and_clean(spark, path):
    """Read, validate, clean, and materialize one cached Spark DataFrame."""
    raw = spark.read.csv(path, header=True, inferSchema=True)
    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    # end_time is part of the source schema, but it is not required for these charts.
    if "end_time" not in raw.columns:
        raw = raw.withColumn("end_time", F.lit(None).cast("timestamp"))
    day_name = F.date_format(F.col("start_time"), "E")
    cleaned = (raw.withColumn("tripduration", F.regexp_replace(F.col("tripduration").cast("string"), ",", "").cast("double"))
               .withColumn("start_time", F.to_timestamp("start_time"))
               .withColumn("end_time", F.to_timestamp("end_time"))
               .filter(F.col("start_time").isNotNull())
               .filter(F.col("tripduration").between(60, 10800))
               .withColumn("hour", F.hour("start_time"))
               .withColumn("day", day_name)
               # Spark numbers Sunday as 1, so rotate the value to sort Monday first.
               .withColumn("day_order", F.pmod(F.dayofweek("start_time") + F.lit(5), F.lit(7)))
               .withColumn("duration_min", F.col("tripduration") / 60.0)
               .cache())
    count = cleaned.count()
    return cleaned, count


def _timed(action):
    start = time.perf_counter()
    result = action()
    elapsed = time.perf_counter() - start
    return result.toPandas(), elapsed


def chart_hour(df):
    return _timed(lambda: df.groupBy("hour").agg(F.count("*").alias("rides")).orderBy("hour"))


def chart_day(df):
    return _timed(lambda: df.groupBy("day", "day_order").agg(F.count("*").alias("rides")).orderBy("day_order").select("day", "rides"))


def chart_usertype(df):
    return _timed(lambda: df.groupBy("usertype").agg(F.count("*").alias("rides"), F.avg("duration_min").alias("avg_duration_min")).orderBy(F.desc("rides")))


def chart_stations(df):
    return _timed(lambda: df.groupBy("from_station_name").agg(F.count("*").alias("rides")).orderBy(F.desc("rides")).limit(10).select(F.col("from_station_name").alias("station"), "rides"))


def chart_heatmap(df):
    return _timed(lambda: df.groupBy("day", "day_order", "hour").agg(F.count("*").alias("rides")).orderBy("day_order").select("day", "hour", "rides"))


def calculate_kpis(df):
    """Compute dashboard headline metrics using Spark aggregations."""
    started = time.perf_counter()
    total = df.count()
    avg = df.agg(F.avg("duration_min").alias("avg")).first()["avg"] or 0.0
    peak = df.groupBy("hour").count().orderBy(F.desc("count"), "hour").first()
    common = df.groupBy("usertype").count().orderBy(F.desc("count")).first()
    result = {"total_rides": total, "avg_duration_min": float(avg),
              "peak_hour": int(peak["hour"]) if peak else 0,
              "common_user": str(common["usertype"]) if common else "Unknown"}
    return result, time.perf_counter() - started
