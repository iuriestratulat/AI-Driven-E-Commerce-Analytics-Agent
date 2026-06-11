import os
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Dynamically calculate absolute paths based on project structure
# __file__ points to: environment/scripts/generate_advanced_data.py
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(base_dir, "data")
OUTPUT_DIR = os.path.join(base_dir, "data_output")

# Ensure directories exist before reading or writing data
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🚀 Pornire motor ETL local avansat (Versiunea Enterprise - Model cu 6 Tabele)...")
print("="*60)

# Helper function to shift years into the future (2016->2023, 2017->2024, 2018->2025, 2019->2026)
def refresh_timestamp(dt):
    if pd.isnull(dt):
        return dt
    year_mapping = {2016: 2023, 2017: 2024, 2018: 2025, 2019: 2026}
    if dt.year in year_mapping:
        try:
            return dt.replace(year=year_mapping[dt.year])
        except ValueError:
            # Handle leap year edge cases (e.g., Feb 29) safely by shifting days
            return dt.replace(year=year_mapping[dt.year], day=dt.day - 1)
    return dt

# =============================================================
# 1. PROCESS DIM_CUSTOMERS (With Official IBGE GDP in Millions USD)
# =============================================================
print("📦 Processing dim_customers and mapping official IBGE GDP (Converted to Millions USD)...")
df_cust_raw = pd.read_csv(os.path.join(INPUT_DIR, "customers.csv"))
dim_customers = df_cust_raw[['customer_id', 'customer_city', 'customer_state']].copy()
dim_customers.columns = ['customer_id', 'city', 'state']

# Exchange rate from Brazilian Real (BRL) to US Dollar (USD)
ex_rate = 0.19 

# Official 2023 GDP data from IBGE (Values represent millions of BRL)
ibge_pib_mapping_usd = {
    'AC': round(26291 * ex_rate, 2),   'AL': round(89689 * ex_rate, 2),   'AP': round(28020 * ex_rate, 2),
    'AM': round(161795 * ex_rate, 2),  'BA': round(430988 * ex_rate, 2),  'CE': round(232239 * ex_rate, 2),
    'DF': round(365669 * ex_rate, 2),  'ES': round(209830 * ex_rate, 2),  'GO': round(336747 * ex_rate, 2),
    'MA': round(149227 * ex_rate, 2),  'MT': round(273009 * ex_rate, 2),  'MS': round(184402 * ex_rate, 2),
    'MG': round(971978 * ex_rate, 2),  'PR': round(670919 * ex_rate, 2),  'PB': round(96963 * ex_rate, 2),
    'PA': round(254547 * ex_rate, 2),  'PE': round(270475 * ex_rate, 2),  'PI': round(80917 * ex_rate, 2),
    'RJ': round(1172871 * ex_rate, 2), 'RN': round(101740 * ex_rate, 2),  'RS': round(650107 * ex_rate, 2),
    'RO': round(76456 * ex_rate, 2),   'RR': round(25125 * ex_rate, 2),   'SC': round(513393 * ex_rate, 2),
    'SE': round(60817 * ex_rate, 2),   'SP': round(3444814 * ex_rate, 2), 'TO': round(64318 * ex_rate, 2)
}

dim_customers['state_gdp_millions_usd'] = dim_customers['state'].map(ibge_pib_mapping_usd).fillna(10000.0).astype(float)

# =============================================================
# 2. PROCESS DIM_PRODUCTS (With BOTH Category and Subcategory)
# =============================================================
print("📦 Processing dim_products & Category Translation JSON...")
df_prod_raw = pd.read_csv(os.path.join(INPUT_DIR, "products.csv"))
df_trans_raw = pd.read_csv(os.path.join(INPUT_DIR, "product_category_name_translation.csv"))

desc_col = 'product_description_lenght' if 'product_description_lenght' in df_prod_raw.columns else 'product_description_length'

with open(os.path.join(INPUT_DIR, "category_subcategory.json"), "r", encoding="utf-8-sig") as f:
    json_cat_map = json.load(f)

df_prod_eng = pd.merge(df_prod_raw, df_trans_raw, on='product_category_name', how='left')
df_prod_eng['product_category_name_english'] = df_prod_eng['product_category_name_english'].fillna('other')
df_prod_eng['macro_category'] = df_prod_eng['product_category_name_english'].map(json_cat_map).fillna('Others')

dim_products = df_prod_eng[['product_id', 'macro_category', 'product_category_name_english', 'product_weight_g', desc_col, 'product_photos_qty']].copy()
dim_products.columns = ['product_id', 'category', 'subcategory', 'weight_g', 'description_length', 'photos_qty']
dim_products['description_length'] = dim_products['description_length'].fillna(0).astype(int)
dim_products['photos_qty'] = dim_products['photos_qty'].fillna(0).astype(int)

# =============================================================
# LOAD CORE FILES & RAW INPUTS
# =============================================================
print("📋 Loading transactional baseline files...")
df_orders_raw = pd.read_csv(os.path.join(INPUT_DIR, "orders.csv"))
df_items_raw = pd.read_csv(os.path.join(INPUT_DIR, "order_items.csv"))
df_payments_raw = pd.read_csv(os.path.join(INPUT_DIR, "order_payments.csv"))
df_reviews_raw = pd.read_csv(os.path.join(INPUT_DIR, "order_reviews.csv"))

# Parse raw dates for orders
date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
for col in date_cols:
    df_orders_raw[col] = pd.to_datetime(df_orders_raw[col])

# Shift years to make data fresh for orders
print("📅 Refreshing transaction and review timestamps to 2023-2026 timeline...")
for col in date_cols:
    df_orders_raw[col] = df_orders_raw[col].apply(refresh_timestamp)

# --- CRITICAL DATA QUALITY DROP: REMOVE 20 SICK ORDERS LATE 2025 ---
# Filter out any orders created from September 1st, 2025 onwards to guarantee clean time-series trends
df_orders_raw = df_orders_raw[df_orders_raw['order_purchase_timestamp'] < '2025-09-01'].copy()

# Rename boleto to cash in payments raw file before aggregation
df_payments_raw['payment_type'] = df_payments_raw['payment_type'].replace('boleto', 'cash')

# --- CRITICAL DATA QUALITY DROP: REMOVE NOT_DEFINED AND UNKNOWN METRIC POLLUTERS ---
# Drop the 3 rows of 'not_defined' and 1 row of 'unknown' natively at the transformation phase
df_payments_raw = df_payments_raw[~df_payments_raw['payment_type'].isin(['not_defined', 'unknown'])].copy()

# Aggregate payments per order (Get primary payment type and max installments)
df_pay_agg = df_payments_raw.sort_values(by='payment_value', ascending=False).groupby('order_id').agg({
    'payment_type': 'first',
    'payment_installments': 'max'
}).reset_index()

# Aggregate item statistics per order
df_items_agg = df_items_raw.groupby('order_id').agg({
    'product_id': 'first',
    'price': 'sum',
    'freight_value': 'sum'
}).reset_index()

# =============================================================
# 3. PROCESS DIM_REVIEWS (New Dedicated Granular Table)
# =============================================================
print("📦 Processing dim_reviews (Keeping 100% fidelity without grouping order_id)...")
# Process and shift review timestamps for Reputation Analytics SLA
df_reviews_raw['review_creation_date'] = pd.to_datetime(df_reviews_raw['review_creation_date']).apply(refresh_timestamp)
df_reviews_raw['review_answer_timestamp'] = pd.to_datetime(df_reviews_raw['review_answer_timestamp']).apply(refresh_timestamp)

# Calculate Review Response Latency in Days
def calculate_review_sla(row):
    if pd.isnull(row['review_answer_timestamp']) or pd.isnull(row['review_creation_date']):
        return 0
    delta = (row['review_answer_timestamp'].date() - row['review_creation_date'].date()).days
    return max(0, delta)

df_reviews_raw['review_response_days'] = df_reviews_raw.apply(calculate_review_sla, axis=1)

# Build clean dimension table (We keep every record intact, even duplicates per order_id)
dim_reviews = df_reviews_raw[['review_id', 'order_id', 'review_score', 'review_response_days']].copy()
# Force integer scores to remove any fractional artifact from our dataset
dim_reviews['review_score'] = dim_reviews['review_score'].fillna(5).astype(int)
dim_reviews['review_response_days'] = dim_reviews['review_response_days'].fillna(0).astype(int)

# Filter out reviews belonging to deleted late 2025 orders to preserve relational integrity
dim_reviews = dim_reviews[dim_reviews['order_id'].isin(df_orders_raw['order_id'])].copy()

# =============================================================
# 4. PROCESS FACT_SALES (The Unified Funnel Architecture - Cleansed of Reviews)
# =============================================================
print("📦 Building fact_sales with SLA delivery delay logic...")
fact_sales = pd.merge(df_orders_raw, df_items_agg, on='order_id', how='inner') # Inner join eliminates unmapped artifacts
fact_sales = pd.merge(fact_sales, df_pay_agg, on='order_id', how='left')

# Calculate pure date-based delivery delays to prevent time-of-day false alerts
def calculate_delivery_delay(row):
    if pd.isnull(row['order_delivered_customer_date']) or pd.isnull(row['order_estimated_delivery_date']):
        return 0
    actual_date = row['order_delivered_customer_date'].date()
    estimated_date = row['order_estimated_delivery_date'].date()
    delta = (actual_date - estimated_date).days
    return max(0, delta)

fact_sales['delivery_delay_days'] = fact_sales.apply(calculate_delivery_delay, axis=1)

# Format inputs safely
fact_sales['price'] = fact_sales['price'].fillna(0.0)
fact_sales['freight_value'] = fact_sales['freight_value'].fillna(0.0)
fact_sales['payment_type'] = fact_sales['payment_type'].fillna('cash') # Defaulting to clean cash payment string

# --- CRITICAL FIX FOR THE 0.002% GRAPH NULL ANOMALY ---
# Ensure any missing installments default to 1, and convert structural 0s directly into 1 payment
fact_sales['payment_installments'] = fact_sales['payment_installments'].fillna(1)
fact_sales['payment_installments'] = fact_sales['payment_installments'].apply(lambda x: 1 if x == 0 else x).astype(int)

# --- CRITICAL BLACK FRIDAY SPIKE SIMULATION ENGINE (+70% IN NOV 2024) ---
print("🔥 Simulating Black Friday traffic amplification (+70% orders in November 2024)...")
fact_sales['order_purchase_timestamp'] = pd.to_datetime(fact_sales['order_purchase_timestamp'])
nov_2024_mask = (fact_sales['order_purchase_timestamp'].dt.year == 2024) & (fact_sales['order_purchase_timestamp'].dt.month == 11)
df_nov_2024 = fact_sales[nov_2024_mask]

if not df_nov_2024.empty:
    df_spike_clone = df_nov_2024.sample(frac=0.70, random_state=42).copy()
    df_spike_clone['order_id'] = df_spike_clone['order_id'] + "_bf"
    # Inject cloned traffic directly into active pipeline
    fact_sales = pd.concat([fact_sales, df_spike_clone], ignore_index=True)

# Standardize output columns
fact_sales_final = fact_sales[[
    'order_id', 'customer_id', 'product_id', 'order_status',
    'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 
    'order_delivered_customer_date', 'order_estimated_delivery_date', 'delivery_delay_days',
    'price', 'freight_value', 'payment_type', 'payment_installments'
]].copy()

fact_sales_final.columns = [
    'order_id', 'customer_id', 'product_id', 'status',
    'created', 'approved', 'shipped', 'delivered', 'estimated_delivery', 'delivery_delay_days',
    'revenue', 'freight_cost', 'payment_type', 'payment_installments'
]

# Forcing clean fillna values across final datasets
fact_sales_final['revenue'] = fact_sales_final['revenue'].fillna(0.0)
fact_sales_final['freight_cost'] = fact_sales_final['freight_cost'].fillna(0.0)
fact_sales_final['payment_type'] = fact_sales_final['payment_type'].fillna('cash')

# Save datetime objects to standard database string format
for col in ['created', 'approved', 'shipped', 'delivered', 'estimated_delivery']:
    fact_sales_final[col] = pd.to_datetime(fact_sales_final[col]).dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')

# =============================================================
# 5. PROCESS FACT_MARKETING_SPEND (ROI Analytics)
# =============================================================
print("📦 Generating fact_marketing_spend...")
valid_marketing_orders = fact_sales_final[fact_sales_final['approved'] != ''].copy()

marketing_data = []
channels = ["Google Ads", "Meta Ads", "TikTok Ads", "Organic", "Direct Traffic"]

for _, row in valid_marketing_orders.iterrows():
    channel = random.choices(channels, weights=[35, 30, 15, 12, 8], k=1)[0]
    
    if channel in ["Organic", "Direct Traffic"]:
        impressions, clicks, ad_spend = 0, 0, 0.0
    else:
        impressions = random.randint(1000, 7500)
        ctr = random.uniform(0.012, 0.048)
        clicks = int(impressions * ctr)
        cpc = random.uniform(0.45, 1.85) if channel == "Google Ads" else random.uniform(0.30, 1.20)
        ad_spend = round(clicks * cpc, 2)
        
    marketing_data.append({
        "order_id": row["order_id"],
        "date": row["approved"],
        "channel": channel,
        "ad_spend": ad_spend,
        "impressions": impressions,
        "clicks": clicks
    })

fact_marketing_spend = pd.DataFrame(marketing_data)

# =============================================================
# 6. PROCESS FACT_SALES_PIPELINE (Operational Real Funnel Architecture)
# =============================================================
print("📦 Generating fact_sales_pipeline based strictly on operational timeline records...")
pipeline_data = []

agent_id_map = {
    "Ana Silva": "A1",
    "Lucas Santos": "A2",
    "Mariana Costa": "A3",
    "Rodrigo Mello": "A4"
}

# Process each order to map its full cascade path matching the slide requirements
for _, row in fact_sales_final.iterrows():
    if row["created"] == '':
        continue
        
    created_dt = datetime.strptime(row["created"], '%Y-%m-%d %H:%M:%S')
    year = created_dt.year
    month = created_dt.month
    
    # --- ADVANCED TIME-BASED WORKFORCE ALLOCATION ENGINE ---
    assigned_agent = "Ana Silva"
    if year == 2023:
        assigned_agent = "Ana Silva"
    elif year == 2024:
        if month == 1:
            assigned_agent = "Ana Silva"
        elif 2 <= month <= 11:
            assigned_agent = random.choices(["Lucas Santos", "Ana Silva"], weights=[0.40, 0.60], k=1)[0]
        else:
            assigned_agent = random.choices(["Ana Silva", "Lucas Santos", "Mariana Costa", "Rodrigo Mello"], weights=[0.35, 0.30, 0.23, 0.22], k=1)[0]
    else:
        assigned_agent = random.choices(["Ana Silva", "Lucas Santos", "Mariana Costa", "Rodrigo Mello"], weights=[0.35, 0.30, 0.23, 0.22], k=1)[0]

    calls_made = random.randint(1, 4)
    
    # Build the sequential waterfall milestones per order to emulate a perfect cumulative funnel
    milestones = [('created', row['created'])]
    if row['approved'] != '':
        milestones.append(('approved', row['approved']))
    if row['shipped'] != '':
        milestones.append(('shipped', row['shipped']))
    if row['delivered'] != '':
        milestones.append(('delivered', row['delivered']))
        
    # Append a clean data block for every phase reached by this specific transaction
    for stage_name, stage_timestamp_str in milestones:
        end_call = datetime.strptime(stage_timestamp_str, '%Y-%m-%d %H:%M:%S')
        start_call = end_call - timedelta(minutes=random.randint(5, 45))
        
        pipeline_data.append({
            "order_id": row["order_id"],
            "agent_id": agent_id_map[assigned_agent],
            "agent_name": assigned_agent,
            "calls_made": calls_made,
            "start_call": start_call.strftime('%Y-%m-%d %H:%M:%S'),
            "end_call": end_call.strftime('%Y-%m-%d %H:%M:%S'),
            "lead_status": stage_name
        })

fact_sales_pipeline = pd.DataFrame(pipeline_data)

# =============================================================
# EXPORT OUTPUTS (Now including dim_reviews.csv)
# =============================================================
print("\n💾 Step 7: Exporting the 6 absolute pipeline datasets...")
datasets = {
    "dim_customers.csv": dim_customers,
    "dim_products.csv": dim_products,
    "dim_reviews.csv": dim_reviews,       
    "fact_sales.csv": fact_sales_final,
    "fact_marketing_spend.csv": fact_marketing_spend,
    "fact_sales_pipeline.csv": fact_sales_pipeline
}

for filename, df in datasets.items():
    full_path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(full_path, index=False, encoding='utf-8')
    print(f"✅ Exported: {filename} ({len(df)} rows)")

print("="*60)
print(f"🎉 ARHITECTURĂ CU 6 TABELE VALIDATĂ LOCAL!\n📁 Fișierele sunt salvate în: {OUTPUT_DIR}")