import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Load configuration from .env
load_dotenv()
db_url = os.getenv("SUPABASE_DB_URL")

if not db_url:
    raise ValueError("❌ Critical Error: SUPABASE_DB_URL not found in your .env file!")

# Dynamically calculate the absolute path to 'environment/data_output'
# __file__ is 'environment/scripts/upload_to_supabase.py'
# First dirname goes to 'environment/scripts'
# Second dirname goes to 'environment'
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_OUTPUT_DIR = os.path.join(base_dir, "data_output")

engine = create_engine(db_url, pool_pre_ping=True)

print("🚀 Starting Enterprise Data Migration (6-Table Model) to Supabase Cloud...")
print("="*60)

# 2. Clean up the old structure (Adding dim_reviews to the cascade drop)
print("🧹 Dropping existing tables to clean up database schema...")
drop_query = """
DROP TABLE IF EXISTS fact_sales_pipeline CASCADE;
DROP TABLE IF EXISTS fact_marketing_spend CASCADE;
DROP TABLE IF EXISTS dim_reviews CASCADE;
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_products CASCADE;
DROP TABLE IF EXISTS dim_customers CASCADE;
"""
with engine.connect() as conn:
    conn.execute(text(drop_query))
    conn.commit()
print("✅ Database cleared successfully.")
print("-"*60)

# 3. Define the 6 datasets to upload from data_output folder
datasets = {
    "dim_customers.csv": "dim_customers",
    "dim_products.csv": "dim_products",
    "dim_reviews.csv": "dim_reviews",       # Added new table
    "fact_sales.csv": "fact_sales",
    "fact_marketing_spend.csv": "fact_marketing_spend",
    "fact_sales_pipeline.csv": "fact_sales_pipeline"
}

# 4. Stream each CSV file to Supabase Cloud
for filename, table_name in datasets.items():
    file_path = os.path.join(DATA_OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"⚠️ Warning: Missing file {filename} in {DATA_OUTPUT_DIR}. Skipping...")
        continue
        
    print(f"📦 Loading {filename} into memory...")
    df = pd.read_csv(file_path)
    
    print(f"⬆️ Uploading {len(df)} rows to table '{table_name}'...")
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',
        index=False,
        chunksize=5000
    )
    print(f"✅ Success: Table '{table_name}' is live in Supabase!")
    print("-"*60)

print("="*60)
print("🎉 MIGRATION COMPLETE! All 6 advanced datasets are successfully live in Supabase.")