import streamlit as st
import pandas as pd
import db_manager
import email_loader
import plotly.express as px

st.set_page_config(page_title="Personal Finance HQ", layout="wide")

st.title("Personal Expense Control Center")

# Load Data from DB
data = db_manager.get_all_expenses()

# Sidebar for actions and filters
st.sidebar.header("🕹️ Control Panel")
if st.sidebar.button("🔄 Sync New Emails"):
    with st.spinner("Fetching Uber, Swiggy & Zomato receipts..."):
        email_loader.run_sync()
    st.success("Sync Complete!")
    st.rerun()

# --- Privacy Toggle ---
st.sidebar.divider()
privacy_mode = st.sidebar.toggle("🔒 Privacy Mode", value=False, help="Mask amounts but keep trend shapes")

# Helper function to mask amounts for text display
def format_amount(value):
    if privacy_mode:
        return "₹ *****"
    return f"₹{value:,.2f}"

if not data:
    st.info("👋 No data found. Click 'Sync New Emails' to start.")
else:
    # --- Pre-processing ---
    df = pd.DataFrame(data)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['Year'] = df['transaction_date'].dt.year
    df['Month Name'] = df['transaction_date'].dt.strftime('%B')
    df['month_year'] = df['transaction_date'].dt.strftime('%b %Y')

    # --- Sidebar Filters ---
    st.sidebar.subheader("📅 Global Filters")
    years = sorted(df['Year'].unique().tolist(), reverse=True)
    years.insert(0, "All Years")
    selected_year = st.sidebar.selectbox("Select Year", years)

    if selected_year != "All Years":
        months = df[df['Year'] == selected_year]['Month Name'].unique().tolist()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        months = sorted(months, key=lambda x: month_order.index(x))
    else:
        months = []
    months.insert(0, "All Months")
    selected_month = st.sidebar.selectbox("Select Month", months)

    # --- Applying Filters ---
    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['Year'] == selected_year]
        if selected_month != "All Months":
            filtered_df = filtered_df[filtered_df['Month Name'] == selected_month]

    # --- KPI Metrics Row ---
    total_spend = filtered_df['amount'].sum()
    uber_spend = filtered_df[filtered_df['service_name'] == 'Uber']['amount'].sum()
    swiggy_spend = filtered_df[filtered_df['service_name'] == 'Swiggy']['amount'].sum()
    zomato_spend = filtered_df[filtered_df['service_name'] == 'Zomato']['amount'].sum()

    st.subheader(f"📊 Insights for: {selected_month} {selected_year if selected_year != 'All Years' else ''}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Spend", format_amount(total_spend))
    m2.metric("Uber", format_amount(uber_spend))
    m3.metric("Swiggy", format_amount(swiggy_spend))
    m4.metric("Zomato", format_amount(zomato_spend))

    st.divider()

    # --- Visualizations Row ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Service Breakdown (%)")
        if not filtered_df.empty:
            fig_pie = px.pie(filtered_df, values='amount', names='service_name', 
                             hole=0.4, color='service_name',
                             color_discrete_map={'Uber': '#000000', 'Swiggy': '#FC8019', 'Zomato': '#E23744'})
            
            # Masking logic for Pie: Show percentage, hide value
            if privacy_mode:
                fig_pie.update_traces(textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Percentage: %{percent}')
            else:
                fig_pie.update_traces(textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Amount: ₹%{value}')
                
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("Spending Trend (Relative)")
        if not filtered_df.empty:
            if selected_month != "All Months":
                trend_data = filtered_df.groupby(filtered_df['transaction_date'].dt.day)['amount'].sum().reset_index()
                x_col, title = 'transaction_date', "Day of Month"
            else:
                trend_data = filtered_df.groupby('month_year')['amount'].sum().reset_index()
                trend_data['sort_date'] = pd.to_datetime(trend_data['month_year'])
                trend_data = trend_data.sort_values('sort_date')
                x_col, title = 'month_year', "Month"

            fig_trend = px.line(trend_data, x=x_col, y='amount', markers=True)
            
            # Masking logic for Trend: Hide Y-axis numbers and tooltips
            if privacy_mode:
                fig_trend.update_yaxes(showticklabels=False, title_text="Amount (Hidden)")
                fig_trend.update_traces(hovertemplate='Date: %{x}<br>Amount: [HIDDEN]')
            else:
                fig_trend.update_layout(yaxis_title="Amount (₹)")

            st.plotly_chart(fig_trend, use_container_width=True)

    # --- Detailed Data View ---
    st.subheader("📝 Transaction Log")
    services = filtered_df['service_name'].unique().tolist()
    selected_services = st.multiselect("Filter by Service", services, default=services)
    
    final_display_df = filtered_df[filtered_df['service_name'].isin(selected_services)].copy()
    
    if privacy_mode:
        final_display_df['amount'] = "*****"
    
    log_df = final_display_df[['transaction_date', 'service_name', 'amount', 'email_subject']].copy()
    log_df.columns = ['Date', 'Service', 'Amount (₹)', 'Description']
    st.dataframe(log_df.sort_values('Date', ascending=False), use_container_width=True)

st.caption("Data stored locally in expenses.db | Built for Abhishek")