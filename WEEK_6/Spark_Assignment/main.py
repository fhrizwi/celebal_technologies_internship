from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# -----------------------------------
# Create Spark Session
# -----------------------------------

spark = SparkSession.builder \
    .appName("Week6 Spark Assignment") \
    .getOrCreate()

print("Spark Session Created Successfully")

# -----------------------------------
# Q3 Read CSV
# -----------------------------------

df = spark.read.csv(
    "data/source.csv",
    header=True,
    inferSchema=True
)

print("\nOriginal Dataset")
df.show()

print("\nSchema")
df.printSchema()

# -----------------------------------
# Q5 Select product_id and price
# category = Electronics
# -----------------------------------

print("\nElectronics Products")

electronics = df.filter(
    col("category") == "Electronics"
).select(
    "product_id",
    "price"
)

electronics.show()

# -----------------------------------
# Q6 Rename column and Cast datatype
# -----------------------------------

print("\nRename old_name -> new_name")

df = df.withColumnRenamed(
    "old_name",
    "new_name"
)

df = df.withColumn(
    "price",
    col("price").cast("double")
)

df.printSchema()

# -----------------------------------
# Q8 Completed Orders
# amount > 1000
# -----------------------------------

print("\nCompleted Orders")

completed = df.filter(
    (col("status") == "Completed") &
    (col("amount") > 1000)
)

completed.show()

# -----------------------------------
# Q10 Add final_price
# -----------------------------------

print("\nAdding Final Price")

df = df.withColumn(
    "final_price",
    col("base_price") * 1.18
)

df.show()

# -----------------------------------
# Q12 Read Parquet
# Save CSV
# -----------------------------------

print("\nSaving as Parquet...")

df.write.mode("overwrite").parquet("output/parquet_data")

print("Reading Parquet...")

parquet_df = spark.read.parquet(
    "output/parquet_data"
)

print("Filter user_id NOT NULL")

filtered = parquet_df.filter(
    col("user_id").isNotNull()
)

filtered.show()

print("Saving CSV")

filtered.write.mode("overwrite").option(
    "header",
    True
).csv("output/csv_output")

# -----------------------------------
# Q14 Region = North
# OR Priority = High
# -----------------------------------

print("\nNorth OR High Priority")

north = df.filter(
    (col("region") == "North") |
    (col("priority") == "High")
)

north.show()

# -----------------------------------
# Handling Null Values
# -----------------------------------

print("\nRows with Non Null user_id")

df.filter(
    col("user_id").isNotNull()
).show()

# -----------------------------------
# Best Practice
# -----------------------------------

print("\nPreview Only")

df.show(5)

# -----------------------------------
# Stop Spark
# -----------------------------------

spark.stop()

print("Assignment Completed Successfully")