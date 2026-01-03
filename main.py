import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np
from app.core.services.account import AccountService
from app.core.services.branch import BranchService
from app.core.services.customer import CustomerService
from app.core.services.dailybalance import DailyBalanceService
from app.core.services.datedim import DateDimService
from app.core.services.transaction import TransactionService
from app.db.base import get_db


st.set_page_config(
    page_title="Bank Intelligence Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: #0E1217;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1C2127 0%, #262C34 100%);
        padding: 2.5rem;
        border-radius: 4px;
        margin-bottom: 2rem;
        border: 1px solid #383F47;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: #F5F8FA;
        font-size: 2.8rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: #A7B6C2;
        font-size: 1rem;
        margin: 0.8rem 0 0 0;
        font-weight: 400;
    }
    
    .metric-card {
        background: #1C2127;
        padding: 1.8rem;
        border-radius: 4px;
        border: 1px solid #383F47;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        background: #262C34;
        border-color: #4A90E2;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.15);
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 600;
        color: #4A90E2;
        margin: 0;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #8A9BA8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .metric-change {
        font-size: 0.85rem;
        color: #0F9960;
        margin-top: 0.5rem;
    }
    
    .section-header {
        color: #F5F8FA;
        font-size: 1.4rem;
        font-weight: 600;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #383F47;
        letter-spacing: -0.3px;
    }
    
    .stDataFrame {
        background: #1C2127;
        border: 1px solid #383F47;
        border-radius: 4px;
    }
    
    div[data-testid="stMetricValue"] {
        color: #4A90E2;
        font-size: 2.2rem;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8A9BA8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stSidebar"] {
        background: #1C2127;
        border-right: 1px solid #383F47;
    }
    
    .stSelectbox, .stMultiSelect, .stDateInput, .stNumberInput {
        background: #262C34;
    }
    
    .stSelectbox > div > div {
        background: #262C34;
        border: 1px solid #383F47;
        color: #F5F8FA;
    }
    
    .insight-box {
        background: #1C2127;
        padding: 1.5rem;
        border-radius: 4px;
        border-left: 3px solid #4A90E2;
        margin: 1rem 0;
        border: 1px solid #383F47;
    }
    
    .insight-box h4 {
        color: #4A90E2;
        margin-top: 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .insight-box p {
        color: #A7B6C2;
        margin-bottom: 0;
        line-height: 1.6;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1C2127;
        border-radius: 4px;
        padding: 0.3rem;
        border: 1px solid #383F47;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 3px;
        color: #8A9BA8;
        font-weight: 500;
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: #4A90E2;
        color: #FFFFFF;
    }
    
    .stButton > button {
        background: #262C34;
        color: #F5F8FA;
        border: 1px solid #383F47;
        border-radius: 4px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #4A90E2;
        border-color: #4A90E2;
        color: #FFFFFF;
    }
    
    .analysis-panel {
        background: #1C2127;
        padding: 1.5rem;
        border-radius: 4px;
        border: 1px solid #383F47;
        margin: 1rem 0;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: #262C34;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #383F47;
    }
    
    .stat-item-label {
        color: #8A9BA8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .stat-item-value {
        color: #4A90E2;
        font-size: 1.8rem;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    h3 {
        color: #F5F8FA;
        font-weight: 600;
    }
    
    .stAlert {
        background: #262C34;
        border: 1px solid #383F47;
        color: #A7B6C2;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def get_services():
    db = next(get_db())
    return {
        'account': AccountService(db),
        'branch': BranchService(db),
        'customer': CustomerService(db),
        'daily_balance': DailyBalanceService(db),
        'date_dim': DateDimService(db),
        'transaction': TransactionService(db)
    }


def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>⬢ BANK INTELLIGENCE PLATFORM</h1>
        <p>Advanced Analytics & Data Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_metrics(services):
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        total_customers = services['customer'].count_all()
        total_accounts = services['account'].count_all()
        active_accounts = services['account'].count_active()
        total_transactions = services['transaction'].count_all()
        
        with col1:
            st.metric(
                label="TOTAL CUSTOMERS",
                value=f"{total_customers:,}",
                delta="Active"
            )
        
        with col2:
            st.metric(
                label="TOTAL ACCOUNTS",
                value=f"{total_accounts:,}",
                delta=f"{active_accounts:,} Active"
            )
        
        with col3:
            st.metric(
                label="TRANSACTIONS",
                value=f"{total_transactions:,}",
                delta="All Time"
            )
        
        with col4:
            avg_credit = services['customer'].get_average_credit_score()
            st.metric(
                label="AVG CREDIT SCORE",
                value=f"{avg_credit:.0f}",
                delta="Good Standing"
            )
    except Exception as e:
        st.error(f"Error loading KPIs: {str(e)}")


def calculate_statistics(data, metric):
    if not data:
        return {}
    
    values = [item[metric] for item in data if item.get(metric) is not None]
    
    if not values:
        return {}
    
    return {
        'mean': np.mean(values),
        'median': np.median(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'sum': np.sum(values),
        'count': len(values)
    }


def render_advanced_transaction_analytics(services):
    st.markdown('<p class="section-header">📊 TRANSACTION ANALYTICS SUITE</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### Analysis Configuration")
        
        date_range = st.date_input(
            "Date Range",
            value=(date.today() - timedelta(days=30), date.today()),
            max_value=date.today()
        )
        
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Category Breakdown", "Merchant Analysis", "Time Series", "Amount Distribution"]
        )
        
        metrics_to_show = st.multiselect(
            "Statistics to Display",
            ["Mean", "Median", "Std Dev", "Min", "Max", "Sum", "Count"],
            default=["Mean", "Sum", "Count"]
        )
        
        min_amount = st.number_input("Min Amount Filter", value=0.0, step=100.0)
        max_amount = st.number_input("Max Amount Filter", value=1000000.0, step=1000.0)
    
    with col1:
        try:
            if len(date_range) == 2:
                start_date = datetime.combine(date_range[0], datetime.min.time())
                end_date = datetime.combine(date_range[1], datetime.max.time())
                
                if analysis_type == "Category Breakdown":
                    category_breakdown = services['transaction'].get_category_breakdown(
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if category_breakdown:
                        df_categories = pd.DataFrame(category_breakdown)
                        
                        stats = calculate_statistics(category_breakdown, 'total')
                        
                        st.markdown("#### Statistical Summary")
                        stat_cols = st.columns(len(metrics_to_show))
                        for idx, metric in enumerate(metrics_to_show):
                            with stat_cols[idx]:
                                metric_key = metric.lower().replace(" ", "_")
                                if metric_key == "std_dev":
                                    metric_key = "std"
                                value = stats.get(metric_key, 0)
                                if metric_key in ['mean', 'median', 'min', 'max', 'sum']:
                                    st.metric(metric, f"${value:,.2f}")
                                else:
                                    st.metric(metric, f"{value:,.0f}")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=df_categories['category'],
                            y=df_categories['total'],
                            name='Total Amount',
                            marker=dict(
                                color=df_categories['total'],
                                colorscale='Blues',
                                showscale=True,
                                colorbar=dict(title="Amount ($)")
                            ),
                            text=df_categories['total'].apply(lambda x: f'${x:,.0f}'),
                            textposition='outside',
                            hovertemplate='<b>%{x}</b><br>Total: $%{y:,.2f}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title="Transaction Volume by Category",
                            xaxis_title="Category",
                            yaxis_title="Total Amount ($)",
                            plot_bgcolor='#0E1217',
                            paper_bgcolor='#0E1217',
                            font=dict(color='#F5F8FA', family='Inter'),
                            height=450,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("#### Detailed Breakdown")
                        st.dataframe(
                            df_categories.style.format({
                                'total': '${:,.2f}',
                                'average': '${:,.2f}',
                                'count': '{:,.0f}'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                
                elif analysis_type == "Merchant Analysis":
                    merchant_breakdown = services['transaction'].get_merchant_breakdown(
                        start_date=start_date,
                        end_date=end_date,
                        limit=20
                    )
                    
                    if merchant_breakdown:
                        df_merchants = pd.DataFrame(merchant_breakdown)
                        
                        stats = calculate_statistics(merchant_breakdown, 'total')
                        
                        st.markdown("#### Statistical Summary")
                        stat_cols = st.columns(len(metrics_to_show))
                        for idx, metric in enumerate(metrics_to_show):
                            with stat_cols[idx]:
                                metric_key = metric.lower().replace(" ", "_")
                                if metric_key == "std_dev":
                                    metric_key = "std"
                                value = stats.get(metric_key, 0)
                                if metric_key in ['mean', 'median', 'min', 'max', 'sum']:
                                    st.metric(metric, f"${value:,.2f}")
                                else:
                                    st.metric(metric, f"{value:,.0f}")
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                y=df_merchants['merchant_name'].head(15),
                                x=df_merchants['total'].head(15),
                                orientation='h',
                                marker=dict(
                                    color=df_merchants['total'].head(15),
                                    colorscale='Teal',
                                    showscale=True
                                ),
                                text=df_merchants['total'].head(15).apply(lambda x: f'${x:,.0f}'),
                                textposition='outside'
                            )
                        ])
                        
                        fig.update_layout(
                            title="Top Merchants by Transaction Volume",
                            xaxis_title="Total Amount ($)",
                            yaxis_title="Merchant",
                            plot_bgcolor='#0E1217',
                            paper_bgcolor='#0E1217',
                            font=dict(color='#F5F8FA', family='Inter'),
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                elif analysis_type == "Amount Distribution":
                    transactions = services['transaction'].get_by_date_range(
                        start_date=start_date,
                        end_date=end_date,
                        pagination=10000
                    )
                    
                    if transactions:
                        amounts = [t.amount for t in transactions if min_amount <= t.amount <= max_amount]
                        
                        if amounts:
                            stats = {
                                'mean': np.mean(amounts),
                                'median': np.median(amounts),
                                'std': np.std(amounts),
                                'min': np.min(amounts),
                                'max': np.max(amounts),
                                'sum': np.sum(amounts),
                                'count': len(amounts)
                            }
                            
                            st.markdown("#### Statistical Summary")
                            stat_cols = st.columns(len(metrics_to_show))
                            for idx, metric in enumerate(metrics_to_show):
                                with stat_cols[idx]:
                                    metric_key = metric.lower().replace(" ", "_")
                                    if metric_key == "std_dev":
                                        metric_key = "std"
                                    value = stats.get(metric_key, 0)
                                    if metric_key in ['mean', 'median', 'min', 'max', 'sum']:
                                        st.metric(metric, f"${value:,.2f}")
                                    else:
                                        st.metric(metric, f"{value:,.0f}")
                            
                            fig = go.Figure()
                            
                            fig.add_trace(go.Histogram(
                                x=amounts,
                                nbinsx=50,
                                marker=dict(
                                    color='#4A90E2',
                                    line=dict(color='#383F47', width=1)
                                ),
                                name='Frequency'
                            ))
                            
                            fig.update_layout(
                                title="Transaction Amount Distribution",
                                xaxis_title="Amount ($)",
                                yaxis_title="Frequency",
                                plot_bgcolor='#0E1217',
                                paper_bgcolor='#0E1217',
                                font=dict(color='#F5F8FA', family='Inter'),
                                height=450
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            fig_box = go.Figure()
                            fig_box.add_trace(go.Box(
                                y=amounts,
                                name='Amount Distribution',
                                marker=dict(color='#4A90E2'),
                                boxmean='sd'
                            ))
                            
                            fig_box.update_layout(
                                title="Box Plot - Amount Distribution",
                                yaxis_title="Amount ($)",
                                plot_bgcolor='#0E1217',
                                paper_bgcolor='#0E1217',
                                font=dict(color='#F5F8FA', family='Inter'),
                                height=400
                            )
                            
                            st.plotly_chart(fig_box, use_container_width=True)
                        
        except Exception as e:
            st.error(f"Error in analysis: {str(e)}")


def render_advanced_customer_analytics(services):
    st.markdown('<p class="section-header">👥 CUSTOMER INTELLIGENCE SUITE</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Analysis Controls")
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Segmentation", "Credit Score Analysis", "Account Distribution", "High-Value Analysis"]
        )
        
        if analysis_mode == "Credit Score Analysis":
            min_score = st.slider("Min Credit Score", 300, 850, 600)
            max_score = st.slider("Max Credit Score", 300, 850, 800)
        
        metrics_display = st.multiselect(
            "Display Metrics",
            ["Mean", "Median", "Std Dev", "Min", "Max", "Count"],
            default=["Mean", "Count"]
        )
    
    with col2:
        try:
            if analysis_mode == "Segmentation":
                segments = services['customer'].get_all_segments()
                
                if segments:
                    segment_data = []
                    for segment in segments:
                        count = services['customer'].count_by_segment(segment)
                        segment_data.append({'Segment': segment, 'Count': count})
                    
                    df_segments = pd.DataFrame(segment_data)
                    
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=df_segments['Segment'],
                            values=df_segments['Count'],
                            hole=0.4,
                            marker=dict(
                                colors=['#4A90E2', '#0F9960', '#F29D49', '#D13212', '#8B572A'],
                                line=dict(color='#383F47', width=2)
                            ),
                            textinfo='label+percent+value',
                            textfont=dict(color='#F5F8FA')
                        )
                    ])
                    
                    fig.update_layout(
                        title="Customer Segmentation Distribution",
                        plot_bgcolor='#0E1217',
                        paper_bgcolor='#0E1217',
                        font=dict(color='#F5F8FA', family='Inter'),
                        height=450
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_segments, use_container_width=True, hide_index=True)
            
            elif analysis_mode == "Credit Score Analysis":
                customers = services['customer'].get_by_credit_score_range(min_score, max_score)
                
                if customers:
                    scores = [c.credit_score for c in customers if c.credit_score]
                    
                    if scores:
                        stats = {
                            'mean': np.mean(scores),
                            'median': np.median(scores),
                            'std': np.std(scores),
                            'min': np.min(scores),
                            'max': np.max(scores),
                            'count': len(scores)
                        }
                        
                        st.markdown("#### Statistical Summary")
                        stat_cols = st.columns(len(metrics_display))
                        for idx, metric in enumerate(metrics_display):
                            with stat_cols[idx]:
                                metric_key = metric.lower().replace(" ", "_")
                                if metric_key == "std_dev":
                                    metric_key = "std"
                                value = stats.get(metric_key, 0)
                                st.metric(metric, f"{value:,.2f}" if metric_key != 'count' else f"{value:,.0f}")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Histogram(
                            x=scores,
                            nbinsx=30,
                            marker=dict(
                                color='#4A90E2',
                                line=dict(color='#383F47', width=1)
                            )
                        ))
                        
                        fig.update_layout(
                            title=f"Credit Score Distribution ({min_score}-{max_score})",
                            xaxis_title="Credit Score",
                            yaxis_title="Number of Customers",
                            plot_bgcolor='#0E1217',
                            paper_bgcolor='#0E1217',
                            font=dict(color='#F5F8FA', family='Inter'),
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_mode == "Account Distribution":
                customer_accounts = services['customer'].get_customers_by_account_count(min_accounts=1)
                
                if customer_accounts:
                    account_counts = [item['account_count'] for item in customer_accounts]
                    
                    stats = {
                        'mean': np.mean(account_counts),
                        'median': np.median(account_counts),
                        'std': np.std(account_counts),
                        'min': np.min(account_counts),
                        'max': np.max(account_counts),
                        'count': len(account_counts)
                    }
                    
                    st.markdown("#### Statistical Summary")
                    stat_cols = st.columns(len(metrics_display))
                    for idx, metric in enumerate(metrics_display):
                        with stat_cols[idx]:
                            metric_key = metric.lower().replace(" ", "_")
                            if metric_key == "std_dev":
                                metric_key = "std"
                            value = stats.get(metric_key, 0)
                            st.metric(metric, f"{value:,.2f}")
                    
                    df_dist = pd.DataFrame({
                        'Customer': [item['customer'].full_name for item in customer_accounts[:20]],
                        'Accounts': [item['account_count'] for item in customer_accounts[:20]],
                        'Credit Score': [item['customer'].credit_score or 0 for item in customer_accounts[:20]]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_dist['Customer'],
                            y=df_dist['Accounts'],
                            marker=dict(
                                color=df_dist['Accounts'],
                                colorscale='Viridis',
                                showscale=True
                            ),
                            text=df_dist['Accounts'],
                            textposition='outside'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Accounts per Customer (Top 20)",
                        xaxis_title="Customer",
                        yaxis_title="Number of Accounts",
                        plot_bgcolor='#0E1217',
                        paper_bgcolor='#0E1217',
                        font=dict(color='#F5F8FA', family='Inter'),
                        height=450
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(
                        df_dist.style.format({'Credit Score': '{:.0f}'}),
                        use_container_width=True,
                        hide_index=True
                    )
        
        except Exception as e:
            st.error(f"Error in customer analysis: {str(e)}")


def render_branch_analytics(services):
    st.markdown('<p class="section-header">🏢 BRANCH PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Configuration")
        
        view_type = st.radio(
            "View Type",
            ["Account Distribution", "Regional Analysis", "Performance Metrics"]
        )
        
        sort_by = st.selectbox(
            "Sort By",
            ["Account Count", "Branch Name", "Region"]
        )
        
        show_stats = st.checkbox("Show Statistical Summary", value=True)
    
    with col2:
        try:
            branches = services['branch'].get_branches_by_account_count(min_accounts=0)
            
            if branches:
                df_branches = pd.DataFrame([
                    {
                        'Branch': item['branch'].branch_name,
                        'Code': item['branch'].branch_code,
                        'Region': item['branch'].region or 'N/A',
                        'Accounts': item['account_count']
                    }
                    for item in branches
                ])
                
                if show_stats:
                    account_counts = [item['account_count'] for item in branches]
                    stats = {
                        'mean': np.mean(account_counts),
                        'median': np.median(account_counts),
                        'std': np.std(account_counts),
                        'min': np.min(account_counts),
                        'max': np.max(account_counts),
                        'sum': np.sum(account_counts)
                    }
                    
                    st.markdown("#### Statistical Overview")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Mean", f"{stats['mean']:.1f}")
                    col_b.metric("Median", f"{stats['median']:.0f}")
                    col_c.metric("Std Dev", f"{stats['std']:.1f}")
                    col_d.metric("Total", f"{stats['sum']:.0f}")
                
                if view_type == "Account Distribution":
                    fig = go.Figure(data=[
                        go.Bar(
                            x=df_branches['Branch'],
                            y=df_branches['Accounts'],
                            marker=dict(
                                color=df_branches['Accounts'],
                                colorscale='Electric',
                                showscale=True
                            ),
                            text=df_branches['Accounts'],
                            textposition='outside'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Account Distribution by Branch",
                        xaxis_title="Branch",
                        yaxis_title="Number of Accounts",
                        plot_bgcolor='#0E1217',
                        paper_bgcolor='#0E1217',
                        font=dict(color='#F5F8FA', family='Inter'),
                        height=450
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                elif view_type == "Regional Analysis":
                    region_summary = df_branches.groupby('Region').agg({
                        'Accounts': ['sum', 'mean', 'count']
                    }).reset_index()
                    region_summary.columns = ['Region', 'Total Accounts', 'Avg Accounts', 'Branch Count']
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=region_summary['Region'],
                        y=region_summary['Total Accounts'],
                        name='Total Accounts',
                        marker=dict(color='#4A90E2')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=region_summary['Region'],
                        y=region_summary['Avg Accounts'],
                        name='Average Accounts',
                        yaxis='y2',
                        mode='lines+markers',
                        marker=dict(color='#0F9960', size=10),
                        line=dict(width=3)
                    ))
                    
                    fig.update_layout(
                        title="Regional Performance Overview",
                        xaxis_title="Region",
                        yaxis_title="Total Accounts",
                        yaxis2=dict(
                            title="Average Accounts per Branch",
                            overlaying='y',
                            side='right',
                            showgrid=False
                        ),
                        plot_bgcolor='#0E1217',
                        paper_bgcolor='#0E1217',
                        font=dict(color='#F5F8FA', family='Inter'),
                        height=450,
                        legend=dict(x=0.02, y=0.98)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(
                        region_summary.style.format({
                            'Total Accounts': '{:,.0f}',
                            'Avg Accounts': '{:,.1f}',
                            'Branch Count': '{:,.0f}'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                
                st.markdown("#### Detailed Branch Data")
                st.dataframe(
                    df_branches.sort_values(sort_by.replace(' ', '_') if sort_by != "Account Count" else "Accounts", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        
        except Exception as e:
            st.error(f"Error in branch analysis: {str(e)}")


def render_balance_analytics(services):
    st.markdown('<p class="section-header">💰 BALANCE ANALYTICS SUITE</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Analysis Parameters")
        
        account_id = st.number_input("Account ID", min_value=1, value=1, step=1)
        
        date_range = st.date_input(
            "Date Range",
            value=(date.today() - timedelta(days=90), date.today()),
            max_value=date.today()
        )
        
        metrics_to_calc = st.multiselect(
            "Calculate Metrics",
            ["Mean", "Median", "Std Dev", "Min", "Max", "Trend"],
            default=["Mean", "Min", "Max", "Trend"]
        )
        
        show_trend = st.checkbox("Show Trend Line", value=True)
    
    with col2:
        try:
            if len(date_range) == 2:
                balances = services['daily_balance'].get_by_date_range(
                    account_id=account_id,
                    start_date=date_range[0],
                    end_date=date_range[1]
                )
                
                if balances:
                    balance_values = [b.ending_balance for b in balances]
                    dates = [b.balance_date for b in balances]
                    
                    stats = {
                        'mean': np.mean(balance_values),
                        'median': np.median(balance_values),
                        'std': np.std(balance_values),
                        'min': np.min(balance_values),
                        'max': np.max(balance_values)
                    }
                    
                    if "Trend" in metrics_to_calc and len(balance_values) > 1:
                        trend = np.polyfit(range(len(balance_values)), balance_values, 1)[0]
                        stats['trend'] = trend
                    
                    st.markdown("#### Statistical Summary")
                    display_metrics = [m for m in metrics_to_calc if m != "Trend"]
                    if display_metrics:
                        stat_cols = st.columns(len(display_metrics))
                        for idx, metric in enumerate(display_metrics):
                            with stat_cols[idx]:
                                metric_key = metric.lower().replace(" ", "_")
                                if metric_key == "std_dev":
                                    metric_key = "std"
                                value = stats.get(metric_key, 0)
                                st.metric(metric, f"${value:,.2f}")
                    
                    if "Trend" in metrics_to_calc and 'trend' in stats:
                        trend_dir = "↑" if stats['trend'] > 0 else "↓"
                        st.metric("Daily Trend", f"${abs(stats['trend']):,.2f} {trend_dir}")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=balance_values,
                        mode='lines+markers',
                        name='Balance',
                        line=dict(color='#4A90E2', width=2),
                        marker=dict(size=6),
                        fill='tozeroy',
                        fillcolor='rgba(74, 144, 226, 0.1)'
                    ))
                    
                    if show_trend and len(balance_values) > 1:
                        z = np.polyfit(range(len(balance_values)), balance_values, 1)
                        p = np.poly1d(z)
                        trend_line = [p(i) for i in range(len(balance_values))]
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=trend_line,
                            mode='lines',
                            name='Trend',
                            line=dict(color='#0F9960', width=2, dash='dash')
                        ))
                    
                    fig.update_layout(
                        title=f"Balance History - Account {account_id}",
                        xaxis_title="Date",
                        yaxis_title="Balance ($)",
                        plot_bgcolor='#0E1217',
                        paper_bgcolor='#0E1217',
                        font=dict(color='#F5F8FA', family='Inter'),
                        height=450,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    df_balances = pd.DataFrame({
                        'Date': dates,
                        'Balance': balance_values
                    })
                    
                    st.markdown("#### Balance Data")
                    st.dataframe(
                        df_balances.style.format({'Balance': '${:,.2f}'}),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No balance data found for this account and date range")
        
        except Exception as e:
            st.error(f"Error in balance analysis: {str(e)}")


def render_account_explorer(services):
    st.markdown('<p class="section-header">🔍 ACCOUNT EXPLORER</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        search_type = st.selectbox(
            "Search By",
            ["Account Number", "Customer Email", "Account ID", "Branch Code"]
        )
    
    with col2:
        search_query = st.text_input("Search Query")
    
    with col3:
        if st.button("🔎 Search", use_container_width=True):
            try:
                if search_type == "Account Number" and search_query:
                    account = services['account'].get_acc_by_number(search_query)
                    if account:
                        st.session_state['selected_account'] = account
                elif search_type == "Account ID" and search_query:
                    account = services['account'].get_acc_by_id(int(search_query))
                    if account:
                        st.session_state['selected_account'] = account
                elif search_type == "Customer Email" and search_query:
                    customer = services['customer'].get_by_email(search_query)
                    if customer:
                        accounts = services['account'].get_accounts_by_customer(customer.id)
                        if accounts:
                            st.session_state['selected_account'] = accounts[0]
                            st.session_state['customer_accounts'] = accounts
                elif search_type == "Branch Code" and search_query:
                    branch = services['branch'].get_by_code(search_query)
                    if branch:
                        accounts = services['account'].get_accounts_by_branch(branch.id)
                        if accounts:
                            st.session_state['branch_accounts'] = accounts
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    if 'selected_account' in st.session_state:
        account = st.session_state['selected_account']
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.markdown(f"""
            <div class="analysis-panel">
                <h3>Account Information</h3>
                <p><strong>Account Number:</strong> {account.account_number}</p>
                <p><strong>Type:</strong> {account.account_type}</p>
                <p><strong>Status:</strong> {'🟢 Active' if account.is_active else '🔴 Inactive'}</p>
                <p><strong>Customer:</strong> {account.customer.full_name if account.customer else 'N/A'}</p>
                <p><strong>Email:</strong> {account.customer.email if account.customer else 'N/A'}</p>
                <p><strong>Branch:</strong> {account.branch.branch_name if account.branch else 'N/A'}</p>
                <p><strong>Branch Code:</strong> {account.branch.branch_code if account.branch else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            try:
                latest_balance = services['daily_balance'].get_latest_balance(account.id)
                if latest_balance:
                    st.metric(
                        "Current Balance",
                        f"${latest_balance.ending_balance:,.2f}",
                        delta=f"As of {latest_balance.balance_date}"
                    )
                
                transaction_count = services['transaction'].count_by_account(account.id)
                st.metric("Total Transactions", f"{transaction_count:,}")
                
                if account.customer and account.customer.credit_score:
                    st.metric("Credit Score", f"{account.customer.credit_score}")
            except Exception as e:
                st.error(f"Error loading account metrics: {str(e)}")
        
        recent_transactions = services['transaction'].get_by_account(account.id, pagination=10)
        
        if recent_transactions:
            st.markdown("#### Recent Transactions")
            df_transactions = pd.DataFrame([
                {
                    'Date': t.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'Amount': t.amount,
                    'Category': t.category,
                    'Merchant': t.merchant_name or 'N/A'
                }
                for t in recent_transactions
            ])
            
            st.dataframe(
                df_transactions.style.format({'Amount': '${:,.2f}'}),
                use_container_width=True,
                hide_index=True
            )
    
    if 'customer_accounts' in st.session_state:
        st.markdown("#### All Customer Accounts")
        accounts = st.session_state['customer_accounts']
        df_accounts = pd.DataFrame([
            {
                'Account Number': a.account_number,
                'Type': a.account_type,
                'Status': 'Active' if a.is_active else 'Inactive',
                'Branch': a.branch.branch_name if a.branch else 'N/A'
            }
            for a in accounts
        ])
        st.dataframe(df_accounts, use_container_width=True, hide_index=True)
    
    if 'branch_accounts' in st.session_state:
        st.markdown("#### Branch Accounts")
        accounts = st.session_state['branch_accounts']
        st.metric("Total Accounts in Branch", len(accounts))
        df_accounts = pd.DataFrame([
            {
                'Account Number': a.account_number,
                'Type': a.account_type,
                'Customer': a.customer.full_name if a.customer else 'N/A'
            }
            for a in accounts[:20]
        ])
        st.dataframe(df_accounts, use_container_width=True, hide_index=True)


def render_sidebar(services):
    with st.sidebar:
        st.markdown("## ⚙️ CONTROL PANEL")
        
        st.markdown("---")
        
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
        
        if st.button("📊 Export Report", use_container_width=True):
            st.info("Export functionality - Coming soon")
        
        st.markdown("---")
        
        st.markdown("### 🔧 Global Filters")
        
        try:
            regions = services['branch'].get_all_regions()
            if regions:
                selected_region = st.selectbox("Region", ["All"] + regions, key="global_region")
        except:
            pass
        
        try:
            segments = services['customer'].get_all_segments()
            if segments:
                selected_segment = st.selectbox("Customer Segment", ["All"] + segments, key="global_segment")
        except:
            pass
        
        account_type_filter = st.multiselect(
            "Account Types",
            ["SAVINGS", "CHECKING"],
            default=["SAVINGS", "CHECKING"]
        )
        
        st.markdown("---")
        
        st.markdown("### ℹ️ System Status")
        
        try:
            total_customers = services['customer'].count_all()
            total_accounts = services['account'].count_all()
            
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-item-label">Database Status</div>
                <div class="stat-item-value">🟢</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Total Records:** {total_customers + total_accounts:,}")
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
        except:
            st.markdown("**Status:** 🔴 Error")
        
        st.markdown("---")
        
        st.markdown("### 📚 Resources")
        st.markdown("[Documentation](#)")
        st.markdown("[API Reference](#)")
        st.markdown("[Support](#)")


def main() -> None:
    load_custom_css()
    
    try:
        services = get_services()
        
        render_sidebar(services)
        render_header()
        
        render_kpi_metrics(services)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Transaction Analytics",
            "👥 Customer Intelligence",
            "🏢 Branch Performance",
            "💰 Balance Analytics",
            "🔍 Account Explorer"
        ])
        
        with tab1:
            render_advanced_transaction_analytics(services)
        
        with tab2:
            render_advanced_customer_analytics(services)
        
        with tab3:
            render_branch_analytics(services)
        
        with tab4:
            render_balance_analytics(services)
        
        with tab5:
            render_account_explorer(services)
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please ensure the database is properly configured and contains data.")


if __name__ == '__main__':
    main()
