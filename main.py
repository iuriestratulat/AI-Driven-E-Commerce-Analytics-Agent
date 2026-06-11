import streamlit as st
import re
import os
import sys
import pandas as pd
from datetime import datetime, date
from sqlalchemy import create_engine

# 1. Keep this so Python knows where to resolve inner imports inside ai_agent.py
sys.path.append(os.path.join(os.path.dirname(__file__), "environment", "scripts"))

# 2. Import using the explicit folder structure path
from environment.scripts.ai_agent import agent_executor

# Configure premium executive page layout
st.set_page_config(page_title="AI E-commerce Analytics Agent", page_icon="📊", layout="wide")

st.title("📊 AI Analytics Agent – Dynamic Executive Dashboard")
st.markdown("Ask complex business questions or use the predefined scenarios in the sidebar to generate automated analyses and charts.")

# ----------------- SIDEBAR FILTERS & PREDEFINED SCENARIOS -----------------
st.sidebar.header("🎛️ Executive Filters")

# 1. Sales Agent Selector
lista_agenti = ["All agents", "Ana Silva", "Lucas Santos", "Mariana Costa", "Rodrigo Mello"]
agent_selectat = st.sidebar.selectbox("Select Sales Agent:", lista_agenti)

st.sidebar.markdown("### 📋 Team Activity History")
if agent_selectat == "All agents":
    st.sidebar.info("💡 **Ana Silva**: September 2023\n\n⚡ **Lucas Santos**: February 2024\n\n🟢 **Mariana Costa**: December 2024\n\n🟢 **Rodrigo Mello**: December 2024")
elif agent_selectat == "Ana Silva":
    st.sidebar.success("👑 **Department Founder**: Active since September 2023. Holds the largest customer portfolio.")
elif agent_selectat == "Lucas Santos":
    st.sidebar.success("⚡ **Senior Agent**: Joined in February 2024. Responsible for Q2-Q3 volume expansion.")
elif agent_selectat == "Mariana Costa":
    st.sidebar.success("🟢 **Specialized Agent**: Hired in December 2024 following massive Black Friday growth.")
elif agent_selectat == "Rodrigo Mello":
    st.sidebar.success("🟢 **Specialized Agent**: Hired in December 2024 to optimize pipeline conversions.")

# 2. Date Filter Range (Adjusted to real Olist dataset bounds up to Nov 2025)
st.sidebar.subheader("📅 Date Range")
data_start = st.sidebar.date_input("Start Date:", date(2023, 9, 1), format="DD/MM/YYYY")
data_end = st.sidebar.date_input("End Date:", date(2025, 10, 31), format="DD/MM/YYYY")

st.sidebar.caption("⚠️ **Note:** Select the date range to anchor the automated chart rendering context.")
st.sidebar.markdown("---")

# --- SIMPLE SCENARIOS ---
st.sidebar.subheader("🟢 Simple Scenarios")
if st.sidebar.button("📊 Total Revenue by Category (Bar Chart)"):
    st.session_state.user_input = "Show the top product categories based on total revenue generated as a bar_chart."

if st.sidebar.button("📊 Monthly Order Volume (Column Chart)"):
    st.session_state.user_input = "Show the evolution of the total number of orders placed each month (grouped by year and month) as a column_chart."

if st.sidebar.button("🍕 Agent Efficiency by Revenue (Pie Chart)"):
    st.session_state.user_input = "Show the ranking and efficiency of sales agents (agent_name) from the pipeline as a percentage share of total revenue generated using a pie_chart."

st.sidebar.markdown("---")

# --- COMPLEX SCENARIOS ---
st.sidebar.subheader("⚡ Complex & Advanced Scenarios")

if st.sidebar.button("📉 SPLY Revenue Comparison"):
    st.session_state.user_input = "Perform a monthly Same Period Last Year (SPLY) comparative analysis for revenue between 2023 and 2024. Generate a comparative line_chart where the X-axis is the month (1-12), Y-axis is revenue, and the legend/color represents the year, drawing a separate continuous line for each year."

if st.sidebar.button("🥞 Responsiveness: Orders vs Reviews"):
    st.session_state.user_input = "Analyze customer responsiveness by joining fact_sales and dim_reviews. Display on a monthly basis how many total orders were completed versus how many unique reviews were submitted, using a stacked_bar_chart or comparative bar chart."

if st.sidebar.button("📈 Ad Spend vs Revenue (2023-2025)"):
    st.session_state.user_input = "Analyze marketing performance for the entire 2023-2025 period. Extract the total advertising expenses (ad_spend from fact_marketing_spend) and the resulting revenue (revenue from fact_sales) for each month. Generate a modern line_chart displaying both lines on the same graph."

if st.sidebar.button("⏳ CRM Sales Funnel (Funnel Chart)"):
    st.session_state.user_input = "Extract pipeline stages from CRM (lead_status from fact_sales_pipeline) and the number of opportunities in each phase to generate a conversion funnel_chart."

if st.sidebar.button("🏪 Top 10 Regions vs Payment Methods"):
    st.session_state.user_input = "Identify the top 10 regions (state) by revenue and display how sales are distributed across those regions based on payment methods (payment_type), using a stacked_column_chart (or stacked bar)."

if st.sidebar.button("🍩 Installment Distribution (Donut Chart)"):
    st.session_state.user_input = "Analyze the customer distribution based on the number of installments chosen (payment_installments from fact_sales). Group them as follows: if 1 then '1 Installment', if 2 then '2 Installments', 3 then '3 Installments', 4 then '4 Installments', and if >= 5 label it '5 or more'. Display the result as a percentage donut_chart."

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.cache_data.clear()  # Triggers native Streamlit cache clearing function
    st.rerun()

# ----------------- ADVANCED TOKEN DIET CACHING ENGINE -----------------
@st.cache_data(show_spinner=False, ttl=86400)
def get_cached_agent_response(prompt_text, selected_agent):
    """
    Executes SQL LLM Agent and stores the output.
    Contains robust try/except fallback block with flush-left multiline strings to avoid indentation issues.
    """
    try:
        response = agent_executor.invoke({"input": prompt_text})
        return response["output"]
    except Exception as e:
        # Check if the error is due to Groq rate limiting (429)
        if "429" in str(e) or "rate_limit" in str(e).lower():
            
            # 1. Fallback for Marketing Spend vs Revenue
            if "marketing_spend" in prompt_text or "performanța de marketing" in prompt_text:
                return """Here is the requested marketing analysis (Portfolio Mode - Fallback Active).

```sql
SELECT 
    TO_CHAR(fs.created::timestamp, 'YYYY-MM') AS month,
    SUM(fm.ad_spend) AS total_spend,
    SUM(fs.revenue) AS total_revenue
FROM fact_sales fs
JOIN fact_marketing_spend fm ON fs.order_id = fm.order_id
GROUP BY 1 ORDER BY 1;
```

```python
import streamlit as st
import plotly.express as px
fig = px.line(df, x="month", y=["total_spend", "total_revenue"], title="Ad Spend vs Revenue Trends")
st.plotly_chart(fig, use_container_width=True)
```
"""
            
            # 2. Fallback for Category Revenue Chart
            elif "category" in prompt_text or "categories" in prompt_text:
                return """Here is the category ranking analysis (Portfolio Mode - Fallback Active).

```sql
SELECT dp.category, SUM(fs.revenue) AS total_revenue
FROM fact_sales fs
JOIN dim_products dp ON fs.product_id = dp.product_id
GROUP BY dp.category ORDER BY total_revenue DESC;
```

```python
import streamlit as st
import plotly.express as px
fig = px.bar(df, x="category", y="total_revenue", title="Top Product Categories by Revenue")
st.plotly_chart(fig, use_container_width=True)
```
"""
            
            # General fallback response for arbitrary questions when rate limited
            return "⚠️ The Groq API rate limits have been reached due to heavy traffic. Please use the predefined scenario buttons in the sidebar (🟢 Simple Scenarios / ⚡ Complex Scenarios) which are fully optimized and cached for stable execution!"
        else:
            raise e

# ----------------- SESSION STATE INITIALIZATION -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat history to maintain persistent state
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text_content"])
        if msg.get("sql_code"):
            with st.expander("🔍 Show SQL Query"):
                st.code(msg["sql_code"], language="sql")
        if msg.get("chart_code") and msg.get("sql_code"):
            try:
                engine = create_engine(os.getenv("SUPABASE_DB_URL"))
                df = pd.read_sql(msg["sql_code"], engine)
                df.columns = [str(col).lower().strip() for col in df.columns]
                chart_env = {"df": df, "st": st}
                if "plotly.express" in msg["chart_code"]:
                    import plotly.express as px
                    chart_env["px"] = px
                exec(msg["chart_code"], chart_env)
            except Exception:
                pass

# ----------------- LIVE INTERACTION ENGINE -----------------
user_query = st.chat_input("Ask the AI agent something specific or trigger sidebar scenarios...")

if "user_input" in st.session_state and st.session_state.user_input:
    user_query = st.session_state.user_input
    st.session_state.user_input = None  # Reset latch

if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "text_content": user_query})
    
    with st.chat_message("assistant"):
        
        message_placeholder = st.empty()
        message_placeholder.markdown("🧠 Agent is compiling the optimized analytical query (Secured Caching Engine Active)...")
        
        try:
            context_string = f" Context injected from user dashboard: The analysis timeline parameters must filter strictly between {data_start.strftime('%Y-%m-%d')} and {data_end.strftime('%Y-%m-%d')}."
            if agent_selectat != "All agents":
            
                context_string += f" Filter and isolate records strictly matching sales agent: '{agent_selectat}'."
            
            enriched_prompt = f"{user_query}\n\n{context_string}"
            
            # Fetch response safely using caching
            full_response = get_cached_agent_response(enriched_prompt, agent_selectat)
            
            # Regex extraction for code blocks
            chart_match = re.search(r"```python\s*(.*?)\s*```", full_response, re.DOTALL)
            sql_match = re.search(r"```sql\s*(.*?)\s*```", full_response, re.DOTALL)
            
            chart_code = ""
            text_clean = full_response
            
            if chart_match:
                chart_code = chart_match.group(1)
                text_clean = re.sub(r"```python.*?```", "", text_clean, flags=re.DOTALL).strip()
            
            extracted_sql = sql_match.group(1) if sql_match else None
            if extracted_sql:
                text_clean = re.sub(r"```sql.*?```", "", text_clean, flags=re.DOTALL).strip()
            
            message_placeholder.markdown(text_clean)
            
            if extracted_sql:
                with st.expander("🔍 Show SQL Query"):
                    st.code(extracted_sql, language="sql")
            
            # Execute and Plot
            if chart_code and extracted_sql:
                try:
                    engine = create_engine(os.getenv("SUPABASE_DB_URL"))
                    df = pd.read_sql(extracted_sql, engine)
                    df.columns = [str(col).lower().strip() for col in df.columns]
                    
                    chart_env = {"df": df, "st": st}
                    if "plotly.express" in chart_code:
                        import plotly.express as px
                        chart_env["px"] = px
                        
                    exec(chart_code, chart_env)
                    
                except Exception as chart_err:
                    st.error(f"⚠️ Chart Engine Execution Exception: {str(chart_err)}")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "text_content": text_clean,
                "chart_code": chart_code,
                "sql_code": extracted_sql
            })
            
        except Exception as e:
            error_msg = f"❌ Processing Error: {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "text_content": error_msg})