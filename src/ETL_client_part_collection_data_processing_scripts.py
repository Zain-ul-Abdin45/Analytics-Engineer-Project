# For server having internet access we can easily download supported libraries
!pip3 install psycopg2 pandas 
# Importing libraries
import psycopg2
import pandas as pd
import math

# PostgreSQL DB connection parameters with psql user
conn = psycopg2.connect(
    dbname="parts_analysis",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()



# cur.execute("DROP TABLE IF EXISTS client_part_collection_sample")

# Step 2: Create the table if not exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS client_part_collection_sample (
        client_id TEXT,
        country TEXT,
        region_id TEXT,
        currency TEXT,
        data_quality TEXT,
        date_added TIMESTAMP,
        part_id TEXT,
        unit TEXT,
        sonar_results TEXT
    );
""")
conn.commit()

# For streamlining the data with different sources, instead we can read data from the  source and add incremental logic for insertion on the date_add attribute

# Step 3: Load the data from parquet
file_path = 'client_part_collection_sample.parquet'
df = pd.read_parquet(file_path)

# Convert date column and ensure string types 
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
for col in ['client_id', 'country', 'region_id', 'currency', 'data_quality', 'part_id', 'unit', 'sonar_results']:
    df[col] = df[col].astype(str)

# Step 4: Insert in batches for proper ingestion without breakages or long insertion packets
batch_size = 20000
total_rows = len(df)
num_batches = math.ceil(total_rows / batch_size)

print(f"🚀 Starting ingestion in {num_batches} batches of {batch_size} rows each...")

insert_query = """
    INSERT INTO client_part_collection_sample (
        client_id, country, region_id, currency, data_quality, date_added,
        part_id, unit, sonar_results
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Inserting packets into table

for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = min(start_idx + batch_size, total_rows)
    batch_df = df.iloc[start_idx:end_idx].reset_index(drop=True)

    # Replace NaNs and NaTs with None
    batch_df = batch_df.astype(object).where(pd.notnull(batch_df), None)

    # Prepare tuples of rows
    data_tuples = list(batch_df.itertuples(index=False, name=None))

    # Insert into PostgreSQL
    cur.executemany(insert_query, data_tuples)
    conn.commit()

    print(f"✅ Batch {i+1}/{num_batches} inserted ({end_idx - start_idx} rows)")


# Step 5: Verify
cur.execute("SELECT COUNT(*) FROM client_part_collection_sample")
row_count = cur.fetchone()[0]

print(f"\n✅ Total rows in table: {row_count}")

# For further reconciliation we can add
# if len(df) = row_count:

cur.execute("SELECT * FROM client_part_collection_sample LIMIT 10")
rows = cur.fetchall()
print("\nFirst 2 rows:")
for row in rows:
    print(row)

# Clean up
cur.close()
conn.close()

