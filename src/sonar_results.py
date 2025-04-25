# Adding libraries

!pip3 install pandas psycopg2 json ast

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import json
import math
import numpy as np
import duckdb


# PostgreSQL DB connection parameters
conn = psycopg2.connect(
    dbname="parts_analysis",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Step 1: Create the sonar results table if not exists
cur.execute("DROP TABLE IF EXISTS parsed_sonar_data")
cur.execute("""
    CREATE TABLE parsed_sonar_data (
        id SERIAL PRIMARY KEY,
        result_id TEXT,
        part_id TEXT,
        amount TEXT,
        currency TEXT,
        date_sonar TIMESTAMP,
        delivery BIGINT,       -- Changed from INTEGER to BIGINT
        price NUMERIC(38,10),  -- Added precision and scale
        status TEXT,
        supplier_country TEXT,
        supplier_id TEXT,
        supplier_name TEXT
    );
""")
conn.commit()
print("✅ Created parsed_sonar_data table")

# Load Parquet file using DuckDB
file_path = 'client_part_collection_sample.parquet'
df = duckdb.query(f"SELECT * FROM '{file_path}'").to_df()

# Modified value validation before insertion
sonar_rows = []

# Iterating through data from the dataframe

for index, row in df.iterrows():
    try:
        part_id = str(row['part_id'])
        
        # Safer way to extract and check sonar_results
        raw_sonar = row.get('sonar_results', None)
        
        # Skip if it's clearly NA or empty
        if raw_sonar is None:
            continue
        
        # Check if it's a pandas NA value
        try:
            if pd.isna(raw_sonar):
                continue
        except ValueError:
            # If we get a ValueError, it's likely an array
            # Try to convert it to a list and check if it's empty
            try:
                if isinstance(raw_sonar, str):
                    if raw_sonar.strip() in ('[]', ''):
                        continue
                    
                    # Try to parse JSON
                    try:
                        parsed_data = json.loads(raw_sonar)
                    except:
                        try:
                            # Try literal_eval as fallback
                            import ast
                            parsed_data = ast.literal_eval(raw_sonar)
                        except:
                            # One more attempt with quote replacement
                            fixed_str = raw_sonar.replace("'", '"')
                            try:
                                parsed_data = json.loads(fixed_str)
                            except:
                                print(f"Could not parse sonar data for row {index}, part_id {part_id}")
                                continue
                elif isinstance(raw_sonar, list):
                    parsed_data = raw_sonar
                    if not parsed_data:  # Skip empty lists
                        continue
                else:
                    # Try to iterate and convert to list
                    try:
                        parsed_data = list(raw_sonar)
                        if not parsed_data:
                            continue
                    except:
                        print(f"Skipping row {index}, part_id {part_id} - Could not process sonar data")
                        continue
            except:
                print(f"Skipping row {index}, part_id {part_id} - Error processing sonar data")
                continue
        
        # Process each entry
        if not isinstance(parsed_data, list):
            print(f"Skipping row {index} - parsed_data is not a list, got {type(parsed_data)}")
            continue
            
        for entry in parsed_data:
            if isinstance(entry, dict):
                # Process dictionary fields with stronger validation
                try:
                    # Handle delivery field with range checking
                    delivery = entry.get('delivery')
                    if delivery is not None:
                        try:
                            delivery = int(delivery)
                            # Check for reasonable range
                            if abs(delivery) > 9223372036854775807:  # Max value for BIGINT
                                print(f"Warning: delivery value {delivery} exceeds BIGINT range, setting to NULL")
                                delivery = None
                        except (ValueError, TypeError):
                            delivery = None
                    
                    # Handle price field with range checking
                    price = entry.get('price')
                    if price is not None:
                        try:
                            price = float(price)
                            # Check for reasonable range
                            if not (1e-10 <= abs(price) <= 1e28 or price == 0):
                                print(f"Warning: price value {price} is extreme, setting to NULL")
                                price = None
                        except (ValueError, TypeError):
                            price = None
                    
                    sonar_rows.append({
                        'result_id': entry.get('result_id'),
                        'part_id': part_id,
                        'amount': entry.get('amount'),
                        'currency': entry.get('currency'),
                        'date_sonar': entry.get('date_sonar'),
                        'delivery': delivery,
                        'price': price,
                        'status': entry.get('status'),
                        'supplier_country': entry.get('supplier_country'),
                        'supplier_id': entry.get('supplier_id'),
                        'supplier_name': entry.get('supplier_name')
                    })
                except Exception as e:
                    print(f"Error processing entry in row {index}: {str(e)}")
    except Exception as e:
        print(f"Error processing row {index}: {str(e)}")

# Create DataFrame from parsed data
if not sonar_rows:
    print("No valid sonar data found in the dataset")
    cur.close()
    conn.close()
    exit()

sonar_df = pd.DataFrame(sonar_rows)

# Convert date_sonar to datetime
if 'date_sonar' in sonar_df.columns:
    sonar_df['date_sonar'] = pd.to_datetime(sonar_df['date_sonar'], errors='coerce')

# Step 4: Insert data in batches with more careful error handling
batch_size = 10000
total_rows = len(sonar_df)
num_batches = math.ceil(total_rows / batch_size)

print(f"🚀 Starting sonar data ingestion in {num_batches} batches of {batch_size} rows each...")

insert_query = """
    INSERT INTO parsed_sonar_data (
        result_id, part_id, amount, currency, date_sonar, delivery, price, 
        status, supplier_country, supplier_id, supplier_name
    ) VALUES %s
"""

for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = min(start_idx + batch_size, total_rows)
    batch_df = sonar_df.iloc[start_idx:end_idx].reset_index(drop=True)
    
    # Replace NaNs with None for PostgreSQL compatibility
    batch_df = batch_df.astype(object).where(pd.notnull(batch_df), None)
    
    try:
        # Prepare data tuples for batch insert with additional validation
        data_tuples = []
        for _, row in batch_df.iterrows():
            try:
                # Additional validation for numeric fields
                delivery = row.get('delivery')
                if delivery is not None and not isinstance(delivery, (int, float, type(None))):
                    try:
                        delivery = int(delivery)
                    except:
                        delivery = None
                
                price = row.get('price')
                if price is not None and not isinstance(price, (int, float, type(None))):
                    try:
                        price = float(price)
                    except:
                        price = None
                
                data_tuples.append((
                    row.get('result_id'), 
                    row.get('part_id'), 
                    row.get('amount'),
                    row.get('currency'), 
                    row.get('date_sonar'), 
                    delivery,
                    price, 
                    row.get('status'), 
                    row.get('supplier_country'),
                    row.get('supplier_id'), 
                    row.get('supplier_name')
                ))
            except Exception as e:
                print(f"Error preparing row in batch {i+1}: {str(e)}")
        
        # Execute batch insert
        execute_values(cur, insert_query, data_tuples)
        conn.commit()
        print(f"Batch {i+1}/{num_batches} inserted ({len(data_tuples)} rows)")
    
    except Exception as e:
        print(f"Error processing batch {i+1}: {str(e)}")
        conn.rollback()
        
        # Try inserting one by one to identify problematic rows
        print("Attempting to insert records one by one to identify problematic rows...")
        successful_inserts = 0
        
        for j, row in batch_df.iterrows():
            try:
                single_insert_query = """
                    INSERT INTO parsed_sonar_data (
                        result_id, part_id, amount, currency, date_sonar, delivery, price, 
                        status, supplier_country, supplier_id, supplier_name
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                delivery = row.get('delivery')
                price = row.get('price')
                
                # Extra validation
                if delivery is not None:
                    try:
                        delivery = int(float(delivery))
                    except:
                        delivery = None
                
                if price is not None:
                    try:
                        price = float(price)
                    except:
                        price = None
                
                cur.execute(
                    single_insert_query,
                    (
                        row.get('result_id'), 
                        row.get('part_id'), 
                        row.get('amount'),
                        row.get('currency'), 
                        row.get('date_sonar'), 
                        delivery,
                        price, 
                        row.get('status'), 
                        row.get('supplier_country'),
                        row.get('supplier_id'), 
                        row.get('supplier_name')
                    )
                )
                conn.commit()
                successful_inserts += 1
            except Exception as row_e:
                conn.rollback()
                print(f"  ❌ Error on row {start_idx + j}: {str(row_e)}")
                print(f"  Problem values: delivery={row.get('delivery')}, price={row.get('price')}")
        
        print(f"  ✓ Successfully inserted {successful_inserts} out of {end_idx - start_idx} rows individually")

# Step 5: Verify the data
cur.execute("SELECT COUNT(*) FROM parsed_sonar_data")
row_count = cur.fetchone()[0]
print(f"\n✅ Total rows in parsed_sonar_data table: {row_count}")

# Clean up
cur.close()
conn.close()
print("✅ PostgreSQL connection closed")
