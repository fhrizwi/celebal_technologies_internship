from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("Week5 Assignment") \
    .getOrCreate()

df = spark.read.csv(
    "data/sales.csv",
    header=True,
    inferSchema=True
)

print("Original Data")
df.show()

# Q3 Remove Duplicates
df = df.dropDuplicates(
    ["user_id", "transaction_date"]
)

# Q5 Fill Null Status
df = df.na.fill(
    {"status": "Unknown"}
)

# Q12 Remove Invalid Rows
df = df.filter(
    col("email").isNotNull()
)

df = df.filter(
    col("username") != ""
)

# Q8 Filter Premium Users
premium_df = df.filter(
    (col("age") >= 18) &
    (col("age") <= 30) &
    (col("subscription") == "Premium")
)

print("Premium Users")
premium_df.show()

# Q4 Region West Average Sale
west_avg = df.filter(
    col("region") == "West"
).groupBy(
    "product_category"
).avg(
    "sale_amount"
)

print("West Region Average Sales")
west_avg.show()

# Q6 City Count > 100
city_count = df.groupBy(
    "city"
).count().filter(
    col("count") > 100
)

city_count.show()

# Q13 Multiple Aggregations
df.select(
    min("price").alias("Min"),
    max("price").alias("Max"),
    avg("price").alias("Average")
).show()

# Q10 Cast Timestamp
df = df.withColumn(
    "raw_timestamp",
    current_timestamp()
)

df = df.withColumn(
    "event_time",
    col("raw_timestamp").cast(TimestampType())
)

df = df.drop("raw_timestamp")

# Q15 Final Pipeline
pipeline = df.dropDuplicates() \
    .na.fill({"price": 0}) \
    .groupBy("store_id") \
    .sum("price")

print("Store Revenue")
pipeline.show()

spark.stop()