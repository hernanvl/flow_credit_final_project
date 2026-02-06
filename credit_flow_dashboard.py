import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Page configuration
st.set_page_config(
    page_title="Credit Flow Dashboard-Hernan Lopez",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Credit Flow Analysis Dashboard 2025 - Data Visualization Project / Hernan Lopez (30357360)")
st.header("Interactive dashboard to explore credit flow in Ecuador January - November")    
st.markdown("---")


## DATA
@st.cache_data
def load_data():
    df = pd.read_csv('credit_flow_cleaned.csv')
    
    # Data cleaning
    df['date'] = pd.to_datetime(df['date'])
    #df = df.drop_duplicates()
    #df = df[df['date']<'2025-12-01']
    
    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col != 'date':
            df[col] = df[col].fillna('Unknown')
    
    # Feature engineering
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%B')
    df['day'] = df['date'].dt.day
    
    # Approval status
    df['is_approved'] = ((df['approval_level_analyst'] != '') | 
                         (df['approval_level_automatic'] != '') | 
                         (df['approval_level_supervisor'] != '')).astype(str)
    df['is_approved'] = df['is_approved'].replace({'True': 'Approved', 'False': 'Rejected'})
    
    # Income category
    df['income_category'] = pd.cut(df['income'], 
                                    bins=[0, 500, 1000, float('inf')],
                                    labels=[ 'Low', 'Medium', 'High'])
    
    # Party type
    df['party_type'] = df['supervisor_sales'].apply(
        lambda x: 'Supervisor' if x != '' and x != 'noclient' else 'No Client'
    )
    
    # Score bins
    bins = np.arange(0, 1100, 100)
    df['score_range'] = pd.cut(df['risk_level'], bins=bins, include_lowest=True)
    
    # Risk score category for filtering (grouped by 100)
    def categorize_score(score):
        if pd.isna(score) or score <= 1:
            return None
        elif score <= 100:
            return '0-100'
        elif score <= 200:
            return '100-200'
        elif score <= 300:
            return '200-300'
        elif score <= 400:
            return '300-400'
        elif score <= 500:
            return '400-500'
        elif score <= 600:
            return '500-600'
        elif score <= 700:
            return '600-700'
        elif score <= 800:
            return '700-800'
        elif score <= 900:
            return '800-900'
        elif score <= 1000:
            return '900-1000'
        else:
            return '1000+'
    
    df['risk_score_category'] = df['risk_level'].apply(categorize_score)
    
    return df

df = load_data()

# Month order
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Funnel data
p_preapproved = df[df['processed_prospect'] == 'yes']
p_credit_form = p_preapproved[p_preapproved['event_income'] == 'begin_event']
p_credit_invoice = p_credit_form[p_credit_form['billing'] == 'invoice']


## WIDGETS
st.sidebar.markdown("# Filters")
st.sidebar.markdown("---")


st.sidebar.markdown("### **Main Filters**")

# Month
# Month
selected_months = st.sidebar.multiselect(
    "Select months",
    options=[m for m in month_order if m != "December"],
    default=[]
)

if not selected_months:
    selected_months = month_order


# Province 
allowed_provinces = [
    "Manabí",
    "Guayas",
    "Pichincha",
    "Santo Domingo",
    "Tungurahua",
    "Los Ríos"
]

selected_provinces = st.sidebar.multiselect(
    "Select provinces",
    options=allowed_provinces,
    default=[]
)

if not selected_provinces:
    selected_provinces = sorted(df['province'].unique())

st.sidebar.markdown("---")
st.sidebar.markdown("### Optional Filters")

# Risk Score Category (grouped by 100)
risk_score_ranges = ["900-1000","800-900","700-800","600-700","500-600","400-500","300-400","200-300",
    "100-200"
]
selected_risk_category = st.sidebar.multiselect(
    "Risk score range",
    options=risk_score_ranges
)

# Income category
selected_income_cat = st.sidebar.multiselect(
    "Income category",
    options=['Low','Medium', 'High']
)

st.sidebar.markdown("---")
st.sidebar.info("If there is no filter select, the dashboard will show all data.")


# DATA FILTERING
filtered_df = df.copy()

filtered_df = filtered_df[filtered_df['risk_level'] > 1]

# Apply main filters (months and provinces - always active)
if selected_months:
    filtered_df = filtered_df[filtered_df['month_name'].isin(selected_months)]

if selected_provinces:
    filtered_df = filtered_df[filtered_df['province'].isin(selected_provinces)]

# Apply optional filters
if selected_risk_category:
    filtered_df = filtered_df[filtered_df['risk_score_category'].isin(selected_risk_category)]

if selected_income_cat:
    filtered_df = filtered_df[filtered_df['income_category'].isin(selected_income_cat)]

# Apply optional filters directly to df
if selected_months:
    df = df[df['month_name'].isin(selected_months)]

if selected_provinces:
    df = df[df['province'].isin(selected_provinces)]

if selected_risk_category:
    df = df[df['risk_score_category'].isin(selected_risk_category)]

if selected_income_cat:
    df = df[df['income_category'].isin(selected_income_cat)]

# Apply optional filters directly to p_preapproved
if selected_months:
    p_preapproved = p_preapproved[p_preapproved['month_name'].isin(selected_months)]

if selected_provinces:
    p_preapproved = p_preapproved[p_preapproved['province'].isin(selected_provinces)]

if selected_risk_category:
    p_preapproved = p_preapproved[p_preapproved['risk_score_category'].isin(selected_risk_category)]

if selected_income_cat:
    p_preapproved = p_preapproved[p_preapproved['income_category'].isin(selected_income_cat)]   

# Apply funnel filters
p_preapproved_filtered = filtered_df[filtered_df['processed_prospect'] == 'yes']
p_credit_form_filtered = p_preapproved_filtered[p_preapproved_filtered['event_income'] == 'begin_event']
p_credit_invoice_filtered = p_credit_form_filtered[p_credit_form_filtered['billing'] == 'invoice']



# Display active filters in the dashboard title

def format_filter(name, values):
    if not values:
        return ""
    return f"{name}: {', '.join(str(v) for v in values)}"

active_filters = ", ".join(filter(None, [
    format_filter("Month", selected_months) if len(selected_months) < len(month_order) else "",
    format_filter("Province", selected_provinces) if len(selected_provinces) < len(df['province'].unique()) else "",
    format_filter("Risk Score", selected_risk_category),
    format_filter("Income", selected_income_cat)
]))


#  SUMMARY METRICS
title = "### Dataset Overview"
if active_filters:
    title += f" — {active_filters}"

st.markdown(title)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Credits", f"{len(p_credit_invoice_filtered):,}")

approval_rate = (
    len(p_credit_invoice_filtered) / len(df) * 100
    if len(df) > 0 else 0
)

col2.metric("Approval Rate", f"{approval_rate:.1f}%")

col3.metric("Avg. Income", f"${filtered_df['income'].mean():,.0f}")

col4.metric("Avg. Expenses", f"${filtered_df['financial_expenses'].mean():,.0f}")

st.markdown("---")



# INTERACTIVE CHARTS

#  Client Conversion Funnel, with conversion rates and sales by province map
colA, colMid, colB = st.columns([1.2, 0.5, 2])


colA.subheader("Client Conversion Funnel Process")

funnel_data = pd.DataFrame({
    'Stage': ['Interested','Pre-approved', 'Credit Form', 'Invoice'],
    'Count': [len(df),len(p_preapproved), len(p_credit_form_filtered), len(p_credit_invoice_filtered)]
})

conv_rate_1 = round((len(p_preapproved) / len(df) * 100), 1) if len(df) > 0 else 0
conv_rate_2 = round((len(p_credit_form_filtered) / len(df) * 100), 1) if len(df) > 0 else 0

fig1 = go.Figure(go.Funnel(
    y=funnel_data['Stage'],
    x=funnel_data['Count'],
    textinfo="value+percent initial",
    marker=dict(color=["#3447db","#1683f0", "#f39c12", "#2ecc71"])
))

fig1.update_traces(textfont=dict(color="white"))
fig1.update_layout(height=400, showlegend=False)

colA.plotly_chart(fig1, use_container_width=True)


colMid.subheader("Conversion Metrics")
colMid.metric("Interested", f"{len(df)}")
colMid.markdown("Pre-approved →<br>Credit Form", unsafe_allow_html=True)
colMid.metric("", f"{conv_rate_1:.1f}%")
colMid.metric("Credit Form → Invoice", f"{conv_rate_2:.1f}%")

if len(p_preapproved_filtered) > 0:
    overall_conv = (len(p_credit_invoice_filtered) / len(df)) * 100
    colMid.metric("Overall Conversion", f"{overall_conv:.1f}%")



colB.subheader("Sales Conversion by Province – Ecuador")

sales_by_province = p_credit_invoice_filtered['province'].value_counts().reset_index()
sales_by_province.columns = ['province', 'sales']

if len(sales_by_province) > 0:

    import unicodedata
    def normalize_text(text):
        if pd.isna(text):
            return text
        text = unicodedata.normalize('NFKD', str(text)).encode('ASCII', 'ignore').decode('ASCII')
        return text.upper().strip()

    sales_by_province['province_normalized'] = sales_by_province['province'].apply(normalize_text)

    try:
        import json
        with open('ecuador.geojson', 'r') as f:
            ecuador_geojson = json.load(f)

        fig11 = px.choropleth(
            sales_by_province,
            geojson=ecuador_geojson,
            locations='province_normalized',
            featureidkey='properties.nombre',
            color='sales',
            color_continuous_scale='Blues',
            hover_name='province',
            hover_data={'sales': True, 'province_normalized': False},
            labels={'sales': 'Sales Count'}
        )

        fig11.update_geos(
            fitbounds="locations",
            visible=True,
            showcountries=True,
            showcoastlines=True,
            showland=True,
            landcolor="lightgray"
        )

        fig11.update_layout(height=400, margin={"r":0,"t":30,"l":0,"b":0})
        colB.plotly_chart(fig11, use_container_width=True)

    except Exception as e:
        colB.error(f"Error loading map: {str(e)}")
        fig_fallback = px.bar(
            sales_by_province,
            x='province',
            y='sales',
            color='sales',
            color_continuous_scale='Blues',
            title="Sales by Province"
        )
        fig_fallback.update_layout(height=400)
        colB.plotly_chart(fig_fallback, use_container_width=True)

else:
    colB.info("No sales data available for the selected filters.")

st.markdown("---")


#  Monthly Credit Volume
st.subheader("Monthly Credit Volume Convertions")

monthly_data = (
    p_credit_invoice_filtered.groupby('month_name').size()
    .reindex(month_order)
    .fillna(0)
)

fig2 = px.bar(
    x=monthly_data.index,
    y=monthly_data.values,
    labels={'x': 'Month', 'y': 'Count'}
)

fig2.update_traces(marker_color='#3498db')
fig2.update_layout(height=400, showlegend=False)

st.plotly_chart(fig2, use_container_width=True)


#  Top Provinces
col3, col4 = st.columns(2)

col3.subheader("Top Provinces by Credit Volume")
province_data = filtered_df['province'].value_counts().head(10)

fig3 = go.Figure(data=[
    go.Bar(x=province_data.values, y=province_data.index, 
           orientation='h', marker_color='#9b59b6')
])
fig3.update_layout(xaxis_title="Number of Credits", height=400, showlegend=False)
col3.plotly_chart(fig3, use_container_width=True)


#  Risk Level Distribution
col4.subheader("Risk Score Distribution")

# Desired display order (descending, without 1000+)
risk_score_ranges = [
    "0-100",
    "100-200",
    "200-300",
    "300-400",
    "400-500",
    "500-600",
    "600-700",
    "700-800",
    "800-900",
    "900-1000"
]

# Count and reorder safely
risk_data = (
    filtered_df['risk_score_category']
    .value_counts()
    .reindex(risk_score_ranges, fill_value=0)
)

import plotly.colors

colors = plotly.colors.diverging.RdYlGn

fig4 = go.Figure(data=[go.Bar(
    x=risk_data.index,
    y=risk_data.values,
    marker_color=colors[:len(risk_data)],
    text=risk_data.values,
    textposition='auto'
)])

fig4.update_layout(
    xaxis_title="Risk Score Range (Higher = Safer)",
    yaxis_title="Count",
    height=400,
    showlegend=False
)

col4.plotly_chart(fig4, use_container_width=True)

# Income Distribution & Age Distribution
if len(filtered_df) > 0:
    col5, col6 = st.columns(2)
    
    col5.subheader("Income Distribution")
    fig5 = go.Figure(data=[go.Histogram(
        x=filtered_df['income'],
        nbinsx=40,
        marker_color='#f39c12'
    )])
    fig5.update_layout(
        xaxis_title="Income",
        yaxis_title="Count",
        height=400,
        showlegend=False
    )
    col5.plotly_chart(fig5, use_container_width=True)
    
    col6.subheader("Age Distribution")
    fig6 = go.Figure()
    fig6.add_trace(go.Box(
        y=filtered_df['age'],
        marker_color='#1abc9c',
        name='Age'
    ))
    fig6.update_layout(yaxis_title="Age", height=400, showlegend=False)
    col6.plotly_chart(fig6, use_container_width=True)


#  Income vs Financial Expenses
st.subheader("Income vs Financial Expenses")

sample_size = min(1000, len(filtered_df[filtered_df['financial_expenses'] > 0]))
if sample_size > 0:
    df_scatter = filtered_df[filtered_df['financial_expenses'] > 0].sample(sample_size)
    
    fig7 = px.scatter(
        df_scatter,
        x='income',
        y='financial_expenses',
        color='risk_level',
        title='Income vs Financial Expenses by Risk Level',
        labels={'income': 'Income', 'financial_expenses': 'Financial Expenses'},
        color_discrete_map={'low': '#2ecc71', 'medium': '#f39c12', 'high': '#e74c3c'}
    )
    fig7.update_layout(height=400)
    st.plotly_chart(fig7, use_container_width=True)
else:
    st.info("No data available for the selected filters.")



st.markdown("---")





# Monthly Funnel Volume by Stage
st.subheader("Monthly Funnel Volume by Stage")

monthly_all = filtered_df.groupby('month_name').size().reindex(month_order).fillna(0)
monthly_form = p_credit_form_filtered.groupby('month_name').size().reindex(month_order).fillna(0)
monthly_invoice = p_credit_invoice_filtered.groupby('month_name').size().reindex(month_order).fillna(0)

fig10 = go.Figure()

fig10.add_trace(go.Scatter(
    x=month_order,
    y=monthly_all.values,
    mode='lines+markers',
    name='All Applicants',
    line=dict(color='#f39c12', width=2),
    marker=dict(size=8)
))

fig10.add_trace(go.Scatter(
    x=month_order,
    y=monthly_form.values,
    mode='lines+markers',
    name='Credit Started',
    line=dict(color='#3498db', width=2),
    marker=dict(size=8)
))

fig10.add_trace(go.Scatter(
    x=month_order,
    y=monthly_invoice.values,
    mode='lines+markers',
    name='Sales (Invoice)',
    line=dict(color='#e74c3c', width=2),
    marker=dict(size=8)
))

fig10.update_layout(
    xaxis_title='Month',
    yaxis_title='Number of Clients',
    height=400,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig10, use_container_width=True)


st.markdown("---")


# Chart 10: Ecuador Map - Sales Conversion by Province



st.markdown("---")


# DATASET Download
st.markdown("### Pre-aproved Dataset View")

columns_to_show = ['id', 'date', 'income', 'financial_expenses', 'province', 
                   'risk_level', 'age', 'is_approved', 'income_category']

st.write(f"Showing {len(p_preapproved)} records out of {len(df)} total")
st.dataframe(p_preapproved[columns_to_show], use_container_width=True, height=400)


# Statistics
st.markdown("### Descriptive Statistics")

numeric_cols = p_preapproved.select_dtypes(include=[np.number]).columns.tolist()

st.dataframe(p_preapproved[numeric_cols].describe(), use_container_width=True)
