# 📊 AI-Driven E-commerce Analytics Agent & Executive Dashboard

An Enterprise-grade, AI-powered business intelligence platform that combines a **Large Language Model (LLM)** agent with a live cloud data warehouse (**Supabase / PostgreSQL**). The system translates natural language business queries directly into optimized SQL, runs them securely, and dynamically renders fully responsive executive charts using **Streamlit** and **Plotly Express**.

---

## 🚀 What This Project Does & Business Value

Traditional business intelligence (BI) requires specialized data analysts to write complex SQL queries, pull data, and build static dashboards. This platform completely democratizes data access by acting as a **Virtual CFO, CMO, and COO** available 24/7. 

### Key Capabilities:
- **Natural Language to SQL Execution:** Non-technical executives can type plain text questions (e.g., *"What is our SPLY monthly revenue trend?"*) and receive accurate data insights in seconds.
- **Dynamic Chart Engine:** Automatically detects the operational intent of the query and dynamically injects specialized visualization layouts (SPLY Continuous Line charts, Vertical CRM Funnels, Region-to-Payment Stacked Columns, Donut charts, or Single Metric cards).
- **Advanced Caching Architecture:** Implements a token-diet secured caching layer to reduce LLM overhead and prevent cloud database throttling while offering fallback portfolios during high-traffic intervals.

### How it Helps a Business:
- **Instant Strategic Decisions:** Drastically slashes time-to-insight for executive-level meetings from days to fractions of a second.
- **Cross-Department Visibility:** Unifies Marketing data (Ad Spend, ROAS), Operations/CRM logs (Lead stages, conversion metrics, SLA response times), Logistics (Delivery delays), and Finance (Absolute Revenue, payment distributions) under a single interface.
- **Micro-Segmentation Insights:** Allows instant analytical drilling by Sales Agent or customized Date Ranges directly from the interactive UI.

---

## 🧮 Core Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive, mobile-friendly executive dashboard |
| **LLM Orchestration** | LangChain | SQL Agent framework with robust tool-calling |
| **Inference Engine** | Groq Cloud | Powered by Llama-3.3-70b-versatile for sub-second responses |
| **Data Warehouse** | Supabase | Cloud PostgreSQL hosting the analytical Star Schema |
| **Visualization** | Plotly Express | Interactive, container-width reactive financial charts |

---

## 📂 Project Structure

```text
AI_ANALYTICS_AGENT/
├── environment/                        # Core analytical environment and data workspace
│   ├── data/                           # Raw source data tables (Olist based)
│   │   ├── category_subcategory.json   # Mapping dictionary to classify product subcategories
│   │   ├── customers.csv               # Raw customer regional data
│   │   ├── order_items.csv             # Raw items per order details
│   │   ├── order_payments.csv          # Raw payment methods, amounts, and installments
│   │   ├── order_reviews.csv           # Raw customer feedback and satisfaction scores
│   │   ├── orders.csv                  # Raw order timestamps and logistics statuses
│   │   ├── product_category_name_translation.csv # English translation lookup for categories
│   │   └── products.csv                # Raw product physical dimensions and metadata
│   │
│   ├── data_output/                    # Processed, unified, and enriched Star Schema tables
│   │   ├── dim_customers.csv          # Cleaned customer dimensions mapped with state GDP metrics
│   │   ├── dim_products.csv           # Cleaned product dimensions with consolidated subcategories
│   │   ├── dim_reviews.csv            # Cleaned feedback data containing optimized response times
│   │   ├── fact_marketing_spend.csv   # Marketing attribution data (spend, clicks, impressions)
│   │   ├── fact_sales_pipeline.csv    # Enriched CRM sales funnel logs tracking operational milestones
│   │   └── fact_sales.csv             # Unified sales transactions containing absolute revenue metrics
│   │
│   └── scripts/                       # Data engineering, ETL, and backend logic modules
│       ├── ai_agent.py                # Main LangChain architecture and Chart Engine rules definition
│       ├── generate_advanced_data.py  # ETL engine simulating marketing spend, CRM pipelines, and SLA
│       └── upload_to_supabase.py      # Automated script to push localized Data Output into Supabase
│   
├── .env                               # Local environment variables (ADDED TO .GITIGNORE)                      
├── main.py                            # Streamlit application core file containing UI layout and session state
├── README.md                          # Project documentation, setup guide, and architectural overview
└── requirements.txt                   # Python environment packages and library dependencies
```

---


## 🛠️ Installation & Quick Start

Follow these steps to spin up the data pipeline and launch the dashboard locally.

### 1. Clone the Repository & Install Dependencies
Ensure you have Python 3.10+ installed on your system.

```bash
git clone https://github.com/iuriestratulat/AI-Driven-E-Commerce-Analytics-Agent.git
cd AI-Driven-E-Commerce-Agent
cd your-repo-name
pip install -r requirements.txt 
``` 

### 2. Configure Environment Variables
Create a .env file in the root directory of the project (ensure it is added to your .gitignore) and insert your credentials:
```bash
SUPABASE_DB_URL=postgresql://postgres.[YOUR_PASSWORD]@[aws-1-eu-central-1.pooler.supabase.com:5432/postgres]
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 3. Run the ETL Pipeline & Cloud Migration
Generate the unified, enriched Star Schema datasets from raw sources and stream them straight to your Supabase Cloud Database instance:
- Generate advanced tables (Sales pipeline, marketing logs, dimensions)
```bash
python environment/scripts/generate_advanced_data.py
```
-  Drop old schemas and migrate the clean 6-table model to Supabase
```bash 
python environment/scripts/upload_to_supabase.py

```

### 4. Launch the Executive Dashboard
Fire up the responsive Streamlit web application:
```bash
streamlit run main.py
```
