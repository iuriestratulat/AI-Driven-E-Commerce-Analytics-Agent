# 📊 AI-Driven E-commerce Analytics Agent & Executive Dashboard

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-driven-e-commerce-analytics-agent.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.24-3F4F75.svg?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C.svg?style=flat&logo=chainlink&logoColor=white)](https://www.langchain.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![Groq](https://img.shields.io/badge/Inference-Groq%20Cloud-orange.svg?style=flat)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)

An Enterprise-grade, AI-powered business intelligence platform that combines a **Large Language Model (LLM)** agent with a live cloud data warehouse (**Supabase / PostgreSQL**). The system translates natural language business queries directly into optimized SQL, runs them securely, and dynamically renders fully responsive executive charts using **Streamlit** and **Plotly Express**.

---

## 🔗 Live Dashboard
The production-ready executive dashboard is actively hosted in the cloud:

👉 **[Click here to view the Live Streamlit Application](https://ai-driven-e-commerce-analytics-agent.streamlit.app/)

> ⚡ *Note: The first load may take 15-30 seconds as the free tier service wakes up.*

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

## 🧠 System Architecture & How It Works

This suite bridges the gap between raw corporate data and executive decision-making using a robust, decoupled architecture divided into three core phases:

### 1. The ETL & Data Modeling Layer (Python + Pandas)
Before any AI interaction occurs, raw, unorganized e-commerce datasets are processed locally:
* **Data Cleansing & Normalization:** Python scripts ingest distributed source files, resolve missing values, parse timestamps, and standardize chaotic fields (e.g., transforming legacy payment codes into clean categories like `cash`, `credit_card`).
* **Star Schema Migration:** The data is architected into an optimized relational Star Schema—separating transaction metrics into a central Fact table (`fact_sales`) surrounded by descriptive Dimension tables. This guarantees ultra-fast SQL execution.

### 2. The Cloud Data Warehouse (Supabase + PostgreSQL)
* The structured Star Schema is securely streamed and hosted on a cloud-native Supabase instance.
* **Row-Level Security (RLS):** Strict security policies are enforced directly at the database level. Anonymous frontend clients have isolated `INSERT-only` permissions to record user feedback, while administrative roles hold full database access, preventing data leaks or unauthorized script injections.

### 3. The Autonomous AI Orchestration (LangChain + Groq + Llama 3.3)
When a user inputs a natural language question (in English, Romanian, German, etc.), the backend agent executes a deterministic multi-step reasoning loop:

[User Query] ➡️ [Llama 3.3 Translation & Concept Mapping] ➡️ [Secure Tool Calling]
|
[Interactive Visuals] ⬅️ [Pandas Dataframe] ⬅️ [SQL Execution] 🍁 [PostgreSQL Database]

1. **Semantic Translation:** The model translates multi-language business terms into precise data concepts matching the database schema.
2. **Safe Tool Calling:** LangChain securely passes the context to an internal SQL generation tool. The model generates standard, read-only PostgreSQL syntax.
3. **Execution & Sandboxing:** The query is executed in a secure environment. The results are returned as a structured Pandas Dataframe.
4. **Dynamic Rendering:** The frontend dynamically intercepts the dataframe. If the schema contains visual distribution trend data, it automatically overrides standard markdown text and injects fully interactive vertical or horizontal Plotly charts.

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
├── LICENSE                            # MIT License
├── README.md                          # Project documentation, setup guide, and architectural overview                     
├── main.py                            # Streamlit application core file containing UI layout and session state
└── requirements.txt                   # Python environment packages and library dependencies
```

---

## 🛠️ Installation & Quick Start

Follow these steps to spin up the data pipeline and launch the dashboard locally.

### 1. Clone the Repository & Install Dependencies
Ensure you have Python 3.10+ installed on your system.

```bash
git clone [https://github.com/iuriestratulat/AI-Driven-E-Commerce-Analytics-Agent.git](https://github.com/iuriestratulat/AI-Driven-E-Commerce-Analytics-Agent.git)
cd AI-Driven-E-Commerce-Analytics-Agent
pip install -r requirements.txt
``` 

### 2. Configure Environment Variables
Create a .env file in the root directory of the project (ensure it is added to your .gitignore) and insert your own cloud credentials:
```env
SUPABASE_DB_URL=postgresql://postgres.[YOUR_DATABASE_PASSWORD]@[aws-1-eu-central-1.pooler.supabase.com:5432/postgres](https://aws-1-eu-central-1.pooler.supabase.com:5432/postgres)
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
