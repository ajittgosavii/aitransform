import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json

# Page configuration
st.set_page_config(
    page_title="AI Platform - Transform Phase Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling and better tab visibility
st.markdown("""
<style>
    /* Main headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #88C0D0;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.1rem;
        color: #D8DEE9;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    /* Enhanced Tab Styling - Much more visible */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(46, 52, 64, 0.4);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: #3B4252;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        color: #D8DEE9;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #434C5E;
        border-color: #88C0D0;
        color: #ECEFF4;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stTabs [aria-selected="true"] {
        background-color: #5E81AC !important;
        color: #ECEFF4 !important;
        border-color: #88C0D0 !important;
        box-shadow: 0 4px 12px rgba(94, 129, 172, 0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f35 0%, #2E3440 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #5E81AC;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Agent status badges */
    .agent-status {
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 0.3rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .status-active {
        background-color: #A3BE8C;
        color: #2E3440;
    }
    .status-idle {
        background-color: #EBCB8B;
        color: #2E3440;
    }
    .status-processing {
        background-color: #88C0D0;
        color: #2E3440;
    }
    
    /* Alert boxes */
    .alert-critical {
        background-color: #BF616A;
        color: #fff;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 5px solid #A93F47;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .alert-warning {
        background-color: #D08770;
        color: #fff;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 5px solid #B8694E;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .alert-info {
        background-color: #5E81AC;
        color: #fff;
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 5px solid #476890;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Sidebar improvements */
    section[data-testid="stSidebar"] {
        background-color: #2E3440;
        border-right: 2px solid #434C5E;
    }
    
    /* Better button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Improved metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Professional spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_decisions' not in st.session_state:
    st.session_state.agent_decisions = []
if 'cost_savings' not in st.session_state:
    st.session_state.cost_savings = 0
if 'actions_executed' not in st.session_state:
    st.session_state.actions_executed = 0
if 'anomalies_detected' not in st.session_state:
    st.session_state.anomalies_detected = 0
if 'mode' not in st.session_state:
    st.session_state.mode = 'demo'  # 'demo' or 'live'
if 'aws_connected' not in st.session_state:
    st.session_state.aws_connected = False

# AWS Connection Functions
@st.cache_resource
def get_aws_session():
    """Get AWS session with credentials from Streamlit secrets or environment"""
    try:
        # Try to create session with credentials from Streamlit secrets
        if hasattr(st, 'secrets') and 'aws' in st.secrets:
            session = boto3.Session(
                aws_access_key_id=st.secrets['aws']['access_key_id'],
                aws_secret_access_key=st.secrets['aws']['secret_access_key'],
                region_name=st.secrets['aws'].get('region', 'us-east-1')
            )
        else:
            # Fall back to default credentials (IAM role, environment, or .aws/credentials)
            session = boto3.Session()
        
        # Test the connection
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        st.session_state.aws_connected = True
        return session
    except (NoCredentialsError, ClientError) as e:
        st.session_state.aws_connected = False
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_real_aws_accounts():
    """Fetch real AWS accounts from Organizations"""
    try:
        session = get_aws_session()
        if not session:
            return None
        
        org = session.client('organizations')
        paginator = org.get_paginator('list_accounts')
        accounts = []
        
        for page in paginator.paginate():
            accounts.extend(page['Accounts'])
        
        return pd.DataFrame(accounts)
    except Exception as e:
        st.error(f"Error fetching AWS accounts: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_real_cost_data(days=90):
    """Fetch real cost data from Cost Explorer"""
    try:
        session = get_aws_session()
        if not session:
            return None
        
        ce = session.client('ce')
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        
        dates = []
        costs = []
        for item in response['ResultsByTime']:
            dates.append(pd.to_datetime(item['TimePeriod']['Start']))
            costs.append(float(item['Total']['UnblendedCost']['Amount']))
        
        return pd.DataFrame({'Date': dates, 'Cost': costs})
    except Exception as e:
        st.error(f"Error fetching cost data: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_real_compliance_data():
    """Fetch real compliance data from AWS Config"""
    try:
        session = get_aws_session()
        if not session:
            return None
        
        config = session.client('config')
        response = config.describe_compliance_by_config_rule()
        
        compliance_data = []
        for rule in response['ComplianceByConfigRules']:
            compliance_data.append({
                'RuleName': rule['ConfigRuleName'],
                'ComplianceType': rule.get('Compliance', {}).get('ComplianceType', 'UNKNOWN')
            })
        
        return pd.DataFrame(compliance_data)
    except Exception as e:
        st.error(f"Error fetching compliance data: {str(e)}")
        return None

# Helper functions for data generation
@st.cache_data
def generate_account_data(num_accounts=640, mode='demo'):
    """Generate simulated AWS account data or fetch real data"""
    # Try to fetch real data if in live mode
    if mode == 'live':
        real_data = fetch_real_aws_accounts()
        if real_data is not None:
            # Enrich real data with additional metrics
            real_data['MonthlyCost'] = real_data.apply(lambda x: round(random.uniform(5000, 500000), 2), axis=1)
            real_data['Resources'] = real_data.apply(lambda x: random.randint(50, 5000), axis=1)
            real_data['SecurityScore'] = real_data.apply(lambda x: random.randint(65, 100), axis=1)
            real_data['ComplianceStatus'] = real_data.apply(lambda x: random.choice(['Compliant', 'Warning', 'Critical']), axis=1)
            return real_data
    
    # Generate simulated data
    accounts = []
    for i in range(num_accounts):
        accounts.append({
            'AccountId': f'123456789{str(i).zfill(3)}',
            'AccountName': f'Portfolio-{i//100}-Account-{i%100}',
            'Region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']),
            'MonthlyCost': round(random.uniform(5000, 500000), 2),
            'Resources': random.randint(50, 5000),
            'SecurityScore': random.randint(65, 100),
            'ComplianceStatus': random.choice(['Compliant', 'Warning', 'Critical'])
        })
    return pd.DataFrame(accounts)

@st.cache_data
def generate_cost_trend_data(days=90, mode='demo'):
    """Generate cost trend data or fetch real data"""
    # Try to fetch real data if in live mode
    if mode == 'live':
        real_data = fetch_real_cost_data(days)
        if real_data is not None:
            # Add baseline and optimized projections
            real_data['ActualCost'] = real_data['Cost']
            real_data['Baseline'] = real_data['Cost'] * 1.1
            real_data['Optimized'] = real_data['Cost']
            return real_data
    
    # Generate simulated data
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_cost = 2500000
    trend = np.linspace(0, 300000, days)
    noise = np.random.normal(0, 50000, days)
    costs = base_cost + trend + noise
    
    # Add optimization impact after day 60
    optimization_effect = np.zeros(days)
    optimization_effect[60:] = np.linspace(0, -400000, days-60)
    costs += optimization_effect
    
    return pd.DataFrame({
        'Date': dates,
        'ActualCost': costs,
        'Baseline': base_cost + trend + noise,
        'Optimized': costs
    })

def generate_agent_activity():
    """Generate recent agent activity"""
    agents = ['Cost Optimization', 'Commitment', 'Anomaly Detection', 'Forecast', 'Storage', 'Placement']
    actions = [
        'Right-sized EC2 instance in prod-account-042',
        'Purchased Savings Plan for compute workload',
        'Detected unusual spend pattern in dev-account-128',
        'Forecasted 15% increase in Q4 spend',
        'Migrated cold data to Glacier',
        'Optimized EBS volume placement'
    ]
    
    activities = []
    for _ in range(10):
        activities.append({
            'Timestamp': datetime.now() - timedelta(minutes=random.randint(1, 120)),
            'Agent': random.choice(agents),
            'Action': random.choice(actions),
            'Impact': f'${random.randint(1000, 50000):,}',
            'Status': random.choice(['✅ Completed', '🔄 In Progress', '⏳ Pending Approval'])
        })
    
    return pd.DataFrame(activities).sort_values('Timestamp', ascending=False)

def simulate_claude_reasoning(scenario):
    """Simulate Claude 4 reasoning for a decision"""
    reasoning_templates = {
        'cost_optimization': """
**Analysis Context:**
- Instance type: t3.2xlarge
- Utilization: 25% CPU, 40% Memory (last 30 days)
- Current cost: $4,380/month
- Running 24/7 in production account

**Decision Reasoning:**
After analyzing CloudWatch metrics and historical patterns, I've identified this instance is significantly over-provisioned. The workload characteristics suggest:

1. **Peak utilization never exceeds 35% CPU**
2. **Memory consumption stable at 40-45%**
3. **Network I/O minimal (<100 Mbps)**

**Recommended Action:**
Right-size to t3.large (50% reduction in resources)

**Risk Assessment:**
- Low risk: Recommended size still provides 2x headroom
- Testing: Recommend 48-hour pilot in dev environment
- Rollback plan: Snapshot available, 5-minute recovery

**Expected Impact:**
- Monthly savings: $2,190 (50% reduction)
- Annual savings: $26,280
- Performance impact: None expected
- Confidence level: 94%

**Autonomous Decision:** APPROVED - Execute in next maintenance window
        """,
        'anomaly': """
**Anomaly Detected: Unusual Spending Pattern**

**Event Details:**
- Account: prod-data-science-087
- Service: SageMaker
- Normal daily spend: $3,200
- Current daily spend: $28,400 (+787%)
- Duration: 3 days

**Root Cause Analysis:**
1. New training job launched with ml.p4d.24xlarge instances
2. Job running 24/7 (typically batch jobs run 4-8 hours)
3. No corresponding ticket in ServiceNow

**AI Assessment:**
- Pattern: Consistent with accidental "always-on" configuration
- Risk: High - Could cost $840K+ if continues
- Urgency: Critical - Immediate action required

**Recommended Actions:**
1. Alert DevOps team via Slack (HIGH priority)
2. Contact account owner
3. If no response in 30 minutes, auto-stop non-critical instances
4. Create ServiceNow incident

**Confidence:** 98% - High certainty anomaly requires intervention
        """,
        'commitment': """
**Savings Plan Analysis**

**Current State:**
- On-demand spend: $125,000/month on EC2
- Steady-state workload: 85% stable, 15% variable
- Current coverage: 45% (existing RIs expiring)

**Claude Analysis:**
Analyzing 12 months of usage patterns:
- Consistent baseline: ~$106,000/month compute
- Predictable workload in production accounts
- Low variance across regions (US-East-1: 70%, US-West-2: 30%)

**Recommendation:**
Purchase 3-year Compute Savings Plan:
- Commitment: $95,000/month
- Coverage: 76% of baseline
- Discount: 54% vs on-demand
- Flexibility: Covers EC2, Fargate, Lambda

**Financial Impact:**
- Monthly savings: $24,700
- Annual savings: $296,400
- 3-year total: $889,200
- ROI: 237% over commitment period
- Payback period: 4.2 months

**Risk Factors:**
- Low: Workload stable for 18+ months
- Commitment level: Conservative (76% coverage)
- Escape clause: Can resell on AWS Marketplace

**Autonomous Decision:** RECOMMEND - Requires CFO approval (>$200K impact)
        """
    }
    
    return reasoning_templates.get(scenario, "Analysis in progress...")

# Main app header with professional styling
st.markdown("""
<div style="text-align: center; padding: 1rem 0 2rem 0; border-bottom: 2px solid #434C5E; margin-bottom: 2rem;">
    <div class="main-header">🤖 AI-Powered Cloud Operations Platform</div>
    <div class="sub-header">Transform Phase | AWS Bedrock + Claude 4 | 640+ AWS Accounts | Autonomous Operations</div>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced professional design
with st.sidebar:
    # Header with icon
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=70)
    with col2:
        st.markdown("### Control Center")
    
    st.markdown("---")
    
    # MODE TOGGLE - Demo vs Live AWS
    st.markdown("#### 🎮 Data Source")
    mode_options = {
        "🎬 Demo Mode": "demo",
        "🔴 Live AWS": "live"
    }
    selected_mode = st.radio(
        "Select data source:",
        options=list(mode_options.keys()),
        index=0 if st.session_state.mode == 'demo' else 1,
        help="Demo Mode: Simulated data for presentations\nLive AWS: Real data from your AWS accounts",
        label_visibility="collapsed"
    )
    st.session_state.mode = mode_options[selected_mode]
    
    # Show AWS connection status if in live mode
    if st.session_state.mode == 'live':
        aws_session = get_aws_session()
        if aws_session:
            st.success("✅ AWS Connected")
            try:
                sts = aws_session.client('sts')
                identity = sts.get_caller_identity()
                st.caption(f"🔑 Account: {identity['Account']}")
            except:
                pass
        else:
            st.error("❌ AWS Not Connected")
            with st.expander("📖 Connection Guide"):
                st.info("""
                **To connect AWS:**
                1. Add credentials to Streamlit secrets
                2. Use IAM role (if on AWS)
                3. Configure ~/.aws/credentials
                """)
    else:
        st.info("📊 Using simulated demo data")
    
    st.markdown("---")
    st.markdown("#### System Status")
    st.success("🟢 All Systems Operational")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Uptime", "99.97%", delta="0.02%")
    with col2:
        st.metric("Agents", "6/6", delta="0")
    
    st.markdown("---")
    st.markdown("#### 📊 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Accounts", "640", delta="+3")
        st.metric("Monthly", "$2.8M", delta="-$89K")
    with col2:
        st.metric("Savings", f"${st.session_state.cost_savings:,}", delta="+12%")
        st.metric("Actions", st.session_state.actions_executed, delta="+5")
    
    st.markdown("---")
    st.markdown("#### 🎮 Demo Controls")
    
    if st.button("🎯 Cost Optimization", use_container_width=True, type="primary"):
        st.session_state.actions_executed += 1
        st.session_state.cost_savings += random.randint(2000, 15000)
        st.success("✅ Optimization executed!")
        time.sleep(0.5)
        st.rerun()
    
    if st.button("⚠️ Anomaly Detection", use_container_width=True):
        st.session_state.anomalies_detected += 1
        st.warning("⚡ Anomaly detected!")
        time.sleep(0.5)
        st.rerun()
    
    if st.button("🔄 Reset Demo", use_container_width=True):
        st.session_state.cost_savings = 0
        st.session_state.actions_executed = 0
        st.session_state.anomalies_detected = 0
        st.session_state.agent_decisions = []
        st.rerun()


# Add visual separation before tabs
st.markdown("<br>", unsafe_allow_html=True)

# Main content tabs with better labels
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "🤖 AI Agents", 
    "💰 FinOps Intelligence",
    "🛡️ Compliance",
    "📈 Analytics",
    "📋 Audit Trail"
])

with tab1:
    st.header("Real-Time Operations Dashboard")
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Actions Executed (24h)", 
            st.session_state.actions_executed,
            delta="+12 vs yesterday",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Cost Savings (30d)", 
            f"${st.session_state.cost_savings:,}",
            delta="+$89K vs last month",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Anomalies Detected", 
            st.session_state.anomalies_detected,
            delta="-2 vs yesterday",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Avg Response Time", 
            "1.2s",
            delta="-0.3s improvement",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Cost trend chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💵 Cost Trend & Optimization Impact")
        cost_data = generate_cost_trend_data(mode=st.session_state.mode)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cost_data['Date'],
            y=cost_data['Baseline'],
            name='Baseline (No AI)',
            line=dict(color='#BF616A', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=cost_data['Date'],
            y=cost_data['Optimized'],
            name='AI-Optimized',
            line=dict(color='#A3BE8C', width=3),
            fill='tonexty'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            xaxis_title='Date',
            yaxis_title='Daily Cost ($)',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("📊 **AI Impact:** $487K saved in last 30 days through autonomous optimizations")
    
    with col2:
        st.subheader("🎯 Agent Activity")
        
        agent_statuses = [
            ("Cost Optimization", "🟢 Active", 23),
            ("Commitment Agent", "🟡 Idle", 8),
            ("Anomaly Detection", "🔵 Processing", 15),
            ("Forecast Agent", "🟢 Active", 12),
            ("Storage Optimizer", "🟢 Active", 31),
            ("Placement Agent", "🟡 Idle", 6)
        ]
        
        for agent, status, actions in agent_statuses:
            st.markdown(f"""
            <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid #5E81AC;'>
                <strong>{agent}</strong><br/>
                <small>{status} | {actions} actions today</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("🔔 Recent Agent Activity")
    activity_df = generate_agent_activity()
    
    # Style the dataframe
    st.dataframe(
        activity_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": st.column_config.DatetimeColumn(
                "Timestamp",
                format="MMM DD, HH:mm"
            ),
            "Impact": st.column_config.TextColumn(
                "Impact",
                width="small"
            )
        }
    )

with tab2:
    st.header("🤖 AI Agents - Autonomous Decision Making")
    
    st.markdown("""
    This platform uses **6 specialized AI agents** powered by AWS Bedrock and Claude 4 Sonnet for autonomous cloud operations.
    Each agent has domain-specific knowledge, decision-making capabilities, and can execute actions autonomously within defined guardrails.
    """)
    
    st.markdown("---")
    
    # Agent selector
    agent_choice = st.selectbox(
        "Select Agent to Explore:",
        ["Cost Optimization Agent", "Commitment Agent", "Anomaly Detection Agent", 
         "Forecast Agent", "Storage Optimizer", "Placement Agent"]
    )
    
    # Simulate decision-making
    st.subheader(f"💡 {agent_choice} - Decision Simulation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Agent Configuration")
        st.code("""
Agent: Cost Optimization
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 5 minutes
Trigger: EventBridge (hourly)
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.3 (deterministic)
Tools: EC2 API, RDS API, Cost Explorer
        """, language="yaml")
        
        st.markdown("### Autonomous Capabilities")
        st.success("✅ Right-sizing (<$10K impact)")
        st.success("✅ Idle resource termination")
        st.success("✅ Storage tier optimization")
        st.warning("⚠️ Commitment purchases (requires approval)")
    
    with col2:
        st.markdown("### Live Decision Scenario")
        
        scenario_type = st.radio(
            "Select Scenario:",
            ["Cost Optimization", "Anomaly Detection", "Commitment Analysis"],
            horizontal=True
        )
        
        if st.button("🚀 Run AI Analysis", use_container_width=True):
            with st.spinner("Claude 4 analyzing scenario..."):
                time.sleep(2)
                
                if scenario_type == "Cost Optimization":
                    st.markdown(simulate_claude_reasoning('cost_optimization'))
                elif scenario_type == "Anomaly Detection":
                    st.markdown(simulate_claude_reasoning('anomaly'))
                else:
                    st.markdown(simulate_claude_reasoning('commitment'))
                
                st.success("✅ Analysis Complete - Decision logged to audit trail")
    
    st.markdown("---")
    
    # Agent performance metrics
    st.subheader("📊 Agent Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Decisions/Day", "1,247", "+89 vs yesterday")
    with col2:
        st.metric("Success Rate", "98.7%", "+0.2%")
    with col3:
        st.metric("Avg Decision Time", "1.3s", "-0.1s")
    
    # Agent decision distribution
    fig = go.Figure(data=[
        go.Bar(
            x=['Cost Opt', 'Commit', 'Anomaly', 'Forecast', 'Storage', 'Placement'],
            y=[412, 89, 156, 201, 289, 100],
            marker_color=['#A3BE8C', '#EBCB8B', '#BF616A', '#88C0D0', '#B48EAD', '#5E81AC']
        )
    ])
    fig.update_layout(
        title="Decisions by Agent (Last 24h)",
        template='plotly_dark',
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("💰 FinOps Intelligence & Cost Optimization")
    
    # Create sub-tabs for FinOps
    finops_tab1, finops_tab2, finops_tab3, finops_tab4 = st.tabs([
        "💵 Cost Overview",
        "🤖 AI/ML Workload Costs",
        "⚠️ Anomaly Detection",
        "📊 Optimization Opportunities"
    ])
    
    with finops_tab1:
        st.subheader("Cost Distribution & Trends")
        
        # Cost breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Cost Distribution by Service")
            
            services = ['EC2', 'RDS', 'S3', 'SageMaker', 'Lambda', 'Bedrock', 'EKS', 'Data Transfer', 'Other']
            costs = [850000, 420000, 280000, 340000, 180000, 125000, 350000, 290000, 165000]
            
            fig = go.Figure(data=[go.Pie(
                labels=services,
                values=costs,
                hole=0.4,
                marker_colors=['#A3BE8C', '#88C0D0', '#EBCB8B', '#B48EAD', '#5E81AC', '#D08770', '#81A1C1', '#BF616A', '#4C566A']
            )])
            fig.update_layout(template='plotly_dark', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Monthly Spend Breakdown")
            
            st.metric("Total Monthly Spend", "$2.8M", "+12% vs last month")
            
            spend_breakdown = [
                ("Compute (EC2, EKS)", "$1.2M", "43%"),
                ("AI/ML (SageMaker, Bedrock)", "$465K", "17%"),
                ("Database (RDS, DynamoDB)", "$420K", "15%"),
                ("Storage (S3, EBS, EFS)", "$350K", "13%"),
                ("Networking", "$290K", "10%"),
                ("Other Services", "$75K", "2%")
            ]
            
            for category, cost, pct in spend_breakdown:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.6rem; border-radius: 5px; margin: 0.3rem 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span><strong>{category}</strong></span>
                        <span style='color: #A3BE8C;'>{cost}</span>
                    </div>
                    <small style='color: #88C0D0;'>{pct} of total spend</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Commitment analysis
        st.subheader("📊 Commitment Utilization & Recommendations")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current RI Coverage", "45%", "-5% (expiring soon)")
        with col2:
            st.metric("Savings Plan Coverage", "28%", "+8% this month")
        with col3:
            st.metric("On-Demand Spend", "$1.2M/month", "-$180K vs last month")
        
        # Utilization chart
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        ri_util = np.random.normal(85, 5, 30)
        sp_util = np.random.normal(92, 3, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=ri_util, name='RI Utilization', line=dict(color='#88C0D0')))
        fig.add_trace(go.Scatter(x=dates, y=sp_util, name='Savings Plan Utilization', line=dict(color='#A3BE8C')))
        fig.add_hline(y=90, line_dash="dash", line_color="#EBCB8B", annotation_text="Target: 90%")
        fig.update_layout(
            template='plotly_dark',
            height=300,
            yaxis_title='Utilization %',
            yaxis_range=[70, 100],
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with finops_tab2:
        st.subheader("🤖 AI/ML Workload Cost Analysis")
        
        st.markdown("""
        **Comprehensive cost tracking for AI/ML workloads** including SageMaker, Bedrock, GPU instances, 
        and data processing pipelines.
        """)
        
        # AI/ML cost metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total AI/ML Spend", "$465K/month", "+24% MoM")
        with col2:
            st.metric("SageMaker", "$340K", "+18%")
        with col3:
            st.metric("Bedrock (Claude 4)", "$125K", "+45%")
        with col4:
            st.metric("GPU Instances", "$89K", "+12%")
        
        st.markdown("---")
        
        # AI/ML Service Breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### AI/ML Spend by Service")
            
            dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
            sagemaker_cost = 280000 + np.cumsum(np.random.normal(800, 200, 90))
            bedrock_cost = 65000 + np.cumsum(np.random.normal(700, 150, 90))
            gpu_cost = 75000 + np.cumsum(np.random.normal(200, 100, 90))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=sagemaker_cost,
                name='SageMaker',
                line=dict(color='#B48EAD', width=2),
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=bedrock_cost,
                name='Bedrock',
                line=dict(color='#88C0D0', width=2),
                stackgroup='one'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=gpu_cost,
                name='GPU Instances',
                line=dict(color='#EBCB8B', width=2),
                stackgroup='one'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                yaxis_title='Cumulative Cost ($)',
                xaxis_title='Date',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Cost Drivers")
            
            st.warning("""
            **⚠️ Rapid Growth Areas:**
            
            **Bedrock (+45% MoM)**
            - Claude 4 API usage: +67%
            - New AI agents deployed: 6
            - Avg daily cost: $4,167
            
            **SageMaker (+18% MoM)**
            - Training jobs: +23%
            - ml.p4d.24xlarge hours: +34%
            - Inference endpoints: +12%
            
            **GPU Instances (+12% MoM)**
            - p3.8xlarge: 234 hours/day
            - g5.12xlarge: 189 hours/day
            - Mostly dev/test workloads
            """)
        
        st.markdown("---")
        
        # SageMaker Detailed Breakdown
        st.markdown("### 🧠 SageMaker Cost Breakdown")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Training Jobs")
            st.metric("Monthly Cost", "$198K", "+23%")
            
            training_data = pd.DataFrame({
                'Instance Type': ['ml.p4d.24xlarge', 'ml.p3.16xlarge', 'ml.g5.12xlarge', 'ml.g4dn.12xlarge'],
                'Hours/Month': [1245, 892, 567, 423],
                'Cost': [67890, 48234, 32145, 18234],
                'Jobs': [145, 234, 345, 456]
            })
            
            st.dataframe(training_data, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Inference Endpoints")
            st.metric("Monthly Cost", "$89K", "+15%")
            
            st.markdown("""
            **Active Endpoints: 45**
            
            - Production: 28 endpoints
            - Staging: 12 endpoints
            - Dev: 5 endpoints
            
            **Instance Types:**
            - ml.m5.xlarge: 18 endpoints
            - ml.c5.2xlarge: 15 endpoints
            - ml.g4dn.xlarge: 12 endpoints
            
            **Auto-scaling:** 67% enabled
            """)
        
        with col3:
            st.markdown("#### Data Processing")
            st.metric("Monthly Cost", "$53K", "+12%")
            
            st.markdown("""
            **Processing Jobs: 1,247**
            
            - Feature engineering: 589 jobs
            - Data validation: 423 jobs
            - Model evaluation: 235 jobs
            
            **Storage:**
            - S3 training data: 45TB
            - Model artifacts: 12TB
            - Feature store: 8TB
            """)
        
        st.markdown("---")
        
        # Bedrock Usage
        st.markdown("### 🤖 AWS Bedrock Usage & Costs")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Bedrock usage trend
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            input_tokens = np.random.normal(45000000, 5000000, 30)
            output_tokens = np.random.normal(12000000, 2000000, 30)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=dates, y=input_tokens/1000000,
                name='Input Tokens (M)',
                marker_color='#88C0D0'
            ))
            
            fig.add_trace(go.Bar(
                x=dates, y=output_tokens/1000000,
                name='Output Tokens (M)',
                marker_color='#A3BE8C'
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                title='Bedrock Token Usage (Daily)',
                yaxis_title='Tokens (Millions)',
                barmode='group',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Bedrock Details")
            
            st.info("""
            **Claude 4 Sonnet Usage**
            
            **Daily Metrics:**
            - API calls: 1.2M requests
            - Input tokens: 45M tokens
            - Output tokens: 12M tokens
            - Avg cost/day: $4,167
            
            **Use Cases:**
            - Cost optimization agent
            - Security analysis
            - Anomaly detection
            - Report generation
            - Natural language queries
            
            **Model Configuration:**
            - Provisioned throughput: 10K TPS
            - On-demand overflow: Yes
            """)
        
        st.markdown("---")
        
        # GPU Instance Analysis
        st.markdown("### 🎮 GPU Instance Cost Analysis")
        
        gpu_data = pd.DataFrame({
            'Instance Type': ['p4d.24xlarge', 'p3.16xlarge', 'p3.8xlarge', 'g5.12xlarge', 'g4dn.12xlarge'],
            'Hourly_Cost': [32.77, 24.48, 12.24, 5.67, 3.91],
            'Hours_Month': [234, 345, 567, 423, 678],
            'Monthly_Cost': [7668, 8446, 6940, 2398, 2651],
            'Utilization': [89, 76, 82, 65, 71]
        })
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                gpu_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Hourly_Cost": st.column_config.NumberColumn("$/Hour", format="$%.2f"),
                    "Hours_Month": st.column_config.NumberColumn("Hours/Month"),
                    "Monthly_Cost": st.column_config.NumberColumn("Monthly Cost", format="$%d"),
                    "Utilization": st.column_config.ProgressColumn("Utilization %", min_value=0, max_value=100)
                }
            )
        
        with col2:
            st.success("""
            **💡 Optimization Opportunity**
            
            **Right-sizing GPU Instances:**
            - p3.16xlarge at 76% util
            - Recommend: p3.8xlarge
            - Savings: $2,234/month
            
            **Spot Instances:**
            - ML training suitable
            - Potential savings: 70%
            - Estimated: $18K/month
            
            **Total AI/ML Savings:**
            **$20.2K/month identified**
            """)
        
        st.markdown("---")
        
        # AI-generated ML cost insights
        st.subheader("🤖 Claude-Generated ML Cost Insights")
        
        st.info("""
        **AI/ML Workload Cost Analysis** (Generated by Claude 4)
        
        Based on 90 days of usage analysis across AI/ML services:
        
        1. **SageMaker Training Optimization**:
           - Your ml.p4d.24xlarge instances run 1,245 hours/month at $32.77/hour
           - GPU utilization shows average 89% (good), but jobs often complete early
           - **Recommendation**: Implement automatic job termination when training plateaus
           - **Expected savings**: $12K/month
        
        2. **Bedrock Cost Trajectory**:
           - 45% month-over-month growth is unsustainable without optimization
           - Current trajectory: $180K/month by Q1 2025
           - Most tokens consumed by report generation (can be optimized)
           - **Recommendation**: Implement response caching for repeated queries
           - **Expected savings**: $35K/month at current scale
        
        3. **GPU Instance Strategy**:
           - 67% of GPU hours are for dev/test workloads
           - These workloads can tolerate interruptions
           - **Recommendation**: Migrate dev/test to Spot Instances
           - **Expected savings**: $18K/month (70% discount)
        
        4. **SageMaker Inference**:
           - Only 67% of endpoints have auto-scaling enabled
           - During off-peak hours, instances idle at 15-20% utilization
           - **Recommendation**: Enable auto-scaling on all prod endpoints
           - **Expected savings**: $8K/month
        
        5. **Data Storage**:
           - 45TB of training data in S3 Standard
           - Access patterns show 80% of data not accessed in 90 days
           - **Recommendation**: Implement lifecycle policy to Intelligent-Tiering
           - **Expected savings**: $5K/month
        
        **Total AI/ML Optimization Potential: $78K/month**
        
        **Confidence Level**: 92% | **Implementation Priority**: High
        """)
    
    with finops_tab3:
        st.subheader("⚠️ AI-Powered Cost Anomaly Detection")
        
        st.markdown("""
        **Real-time anomaly detection** using machine learning to identify unusual spending patterns, 
        budget overruns, and unexpected cost spikes across all AWS services.
        """)
        
        # Anomaly metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Anomalies", "8", "-4 resolved")
        with col2:
            st.metric("Total Cost Impact", "$87K", "Last 7 days")
        with col3:
            st.metric("Auto-Resolved", "23", "This week")
        with col4:
            st.metric("Detection Accuracy", "96.8%", "+1.2%")
        
        st.markdown("---")
        
        # Current Anomalies
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔴 Active Cost Anomalies")
            
            active_anomalies = [
                ("CRITICAL", "SageMaker Training Spike", "prod-ml-training-087", "$28.4K/day", "+787%", "3 days", 
                 "ml.p4d.24xlarge instance running 24/7, typically batch jobs run 4-8 hours"),
                ("HIGH", "Bedrock Token Surge", "ai-agents-production", "$8.2K/day", "+245%", "2 days",
                 "Unusual token consumption from anomaly detection agent, possible infinite loop"),
                ("HIGH", "Data Transfer Spike", "prod-data-pipeline-042", "$4.8K/day", "+420%", "1 day",
                 "Cross-region data transfer to eu-west-1 from backup job misconfiguration"),
                ("MEDIUM", "EC2 Unexpected Usage", "dev-sandbox-156", "$2.1K/day", "+180%", "5 days",
                 "Developer left 15x c5.9xlarge instances running over weekend"),
                ("MEDIUM", "RDS Storage Growth", "analytics-db-021", "$1.9K/day", "+95%", "7 days",
                 "Database size doubled, logs not being rotated properly")
            ]
            
            for severity, title, account, cost, increase, duration, detail in active_anomalies:
                if severity == "CRITICAL":
                    color = "#BF616A"
                elif severity == "HIGH":
                    color = "#D08770"
                else:
                    color = "#EBCB8B"
                
                st.markdown(f"""
                <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; border-left: 5px solid {color};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <strong style='color: {color}; font-size: 1.1rem;'>{severity}</strong>
                            <strong style='font-size: 1.1rem;'> | {title}</strong>
                        </div>
                        <div style='text-align: right;'>
                            <span style='color: #A3BE8C; font-size: 1.3rem; font-weight: bold;'>{cost}</span><br/>
                            <span style='color: {color};'>{increase} increase</span>
                        </div>
                    </div>
                    <div style='margin-top: 0.5rem;'>
                        <small><strong>Account:</strong> {account}</small><br/>
                        <small><strong>Duration:</strong> {duration}</small><br/>
                        <small style='color: #D8DEE9;'>{detail}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎯 Detection Model")
            
            st.success("""
            **AI Anomaly Detection**
            
            **Model Architecture:**
            - LSTM neural network
            - 90-day training window
            - Hourly predictions
            - 96.8% accuracy
            
            **Features Used:**
            - Historical spend patterns
            - Day of week/hour trends
            - Service-specific behavior
            - Account activity level
            - Regional patterns
            
            **Detection Criteria:**
            - >3 std deviations
            - Sustained for >2 hours
            - Context-aware thresholds
            - Business calendar aware
            
            **Actions:**
            - Auto-alert DevOps team
            - Create ServiceNow ticket
            - Suggest remediation
            - Auto-stop if criteria met
            """)
        
        st.markdown("---")
        
        # Anomaly visualization
        st.markdown("### 📊 Cost Anomaly Timeline")
        
        # Generate anomaly data
        dates = pd.date_range(end=datetime.now(), periods=168, freq='H')  # 7 days hourly
        baseline = np.random.normal(120000, 5000, 168)
        actual = baseline.copy()
        
        # Add anomalies
        actual[60:84] = baseline[60:84] * 4.2  # SageMaker spike
        actual[120:144] = baseline[120:144] * 2.8  # Bedrock surge
        actual[150:156] = baseline[150:156] * 3.5  # Data transfer
        
        fig = go.Figure()
        
        # Expected baseline
        fig.add_trace(go.Scatter(
            x=dates, y=baseline,
            name='Expected (Baseline)',
            line=dict(color='#88C0D0', width=1, dash='dash'),
            opacity=0.7
        ))
        
        # Actual spend
        fig.add_trace(go.Scatter(
            x=dates, y=actual,
            name='Actual Spend',
            line=dict(color='#A3BE8C', width=2),
            fill='tonexty',
            fillcolor='rgba(163, 190, 140, 0.1)'
        ))
        
        # Highlight anomalies
        anomaly_mask = actual > baseline * 2
        fig.add_trace(go.Scatter(
            x=dates[anomaly_mask],
            y=actual[anomaly_mask],
            mode='markers',
            name='Anomalies Detected',
            marker=dict(color='#BF616A', size=10, symbol='x')
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=350,
            yaxis_title='Hourly Cost ($)',
            xaxis_title='Date/Time',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # AI Reasoning Example
        st.markdown("### 🤖 Claude Anomaly Analysis Example")
        
        with st.expander("View Detailed AI Reasoning for SageMaker Anomaly", expanded=False):
            st.markdown("""
            **Anomaly ID:** ANO-2024-11-23-00142  
            **Detection Time:** 2024-11-23 18:34:12 UTC  
            **Severity:** CRITICAL  
            
            ---
            
            **Claude 4 Analysis:**
            
            **Event Details:**
            - Account: prod-ml-training-087
            - Service: SageMaker
            - Normal daily spend: $3,200
            - Current daily spend: $28,400 (+787%)
            - Duration: 3 days
            - Total excess cost: $75,600
            
            **Root Cause Analysis:**
            
            I've identified an ml.p4d.24xlarge training instance (job ID: sm-train-20241120-1534) that has been 
            running continuously for 72 hours. Based on historical patterns, this team's training jobs typically 
            complete in 4-8 hours.
            
            **Evidence:**
            1. CloudWatch metrics show flat GPU utilization at 23% (unusually low)
            2. Training loss hasn't improved in 48 hours (plateaued)
            3. No corresponding ServiceNow ticket for extended training
            4. Instance launched on Friday 6:34 PM (after business hours)
            5. Similar pattern occurred 3 months ago (ANO-2024-08-15-00087)
            
            **Probable Cause:**
            The training script likely hit an edge case and is stuck in a loop, or the developer forgot to set 
            early stopping criteria. The Friday evening launch time suggests this was started before the weekend 
            and left running unattended.
            
            **Business Impact:**
            - Cost impact: $75,600 (and growing at $28,400/day)
            - Wastes 72 hours of GPU capacity ($2,360/hour)
            - Blocks other teams from GPU access
            - Risk: Will continue until manually stopped
            
            **Recommended Actions:**
            
            **Immediate (Within 1 hour):**
            1. ✅ Alert data science team lead via Slack (sent 18:34 UTC)
            2. ✅ Create HIGH priority ServiceNow incident (INC0089234)
            3. ⏳ If no response in 30 minutes: Auto-stop training job
            4. ⏳ Send summary to FinOps team and account owner
            
            **Preventive Measures:**
            1. Implement mandatory max_runtime parameter (suggest: 12 hours for this team)
            2. Add CloudWatch alarm for >8 hour training jobs
            3. Enable SageMaker automatic job termination on plateau
            4. Require approval for p4d instances (>$30/hour)
            
            **Expected Outcome:**
            - Immediate: Stop runaway job, prevent additional $28K/day spend
            - Long-term: Prevent 90% of similar anomalies (based on historical data)
            
            **Confidence Level:** 98% - High certainty this requires immediate intervention
            
            **Compliance Note:**
            This incident demonstrates need for preventive controls per FinOps best practices. 
            Recommend implementing AWS Budgets with automatic actions for similar scenarios.
            
            ---
            
            **Action Timeline:**
            - 18:34 UTC: Anomaly detected by AI
            - 18:34 UTC: Slack alert sent to #ml-training channel
            - 18:35 UTC: ServiceNow incident INC0089234 created
            - 18:42 UTC: Data science lead acknowledged
            - 18:47 UTC: Training job stopped manually
            - 18:50 UTC: Post-mortem scheduled for Monday
            
            **Status:** ✅ RESOLVED - Manual intervention completed
            """)
        
        st.markdown("---")
        
        # Anomaly statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📈 Detection Stats (30 Days)")
            st.metric("Anomalies Detected", "247")
            st.metric("Auto-Resolved", "189", "76.5%")
            st.metric("Required Human Review", "58", "23.5%")
            st.metric("False Positives", "9", "3.6%")
        
        with col2:
            st.markdown("### 💰 Cost Impact Prevented")
            st.metric("Total Excess Cost Detected", "$1.2M")
            st.metric("Cost Prevented", "$987K", "82%")
            st.metric("Avg Time to Detection", "1.8 hours")
            st.metric("Avg Time to Resolution", "4.2 hours")
        
        with col3:
            st.markdown("### 🎯 Top Anomaly Types")
            
            anomaly_types = [
                ("ML Training Overruns", 89, "36%"),
                ("Forgotten Resources", 67, "27%"),
                ("Misconfigured Auto-Scaling", 45, "18%"),
                ("Data Transfer Spikes", 28, "11%"),
                ("Other", 18, "8%")
            ]
            
            for atype, count, pct in anomaly_types:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.4rem; border-radius: 3px; margin: 0.2rem 0;'>
                    <strong>{atype}</strong>: {count} ({pct})
                </div>
                """, unsafe_allow_html=True)
    
    with finops_tab4:
        st.subheader("📊 Optimization Opportunities")
        
        opportunities = [
            ("Right-sizing EC2 Instances", "$124K/month", "🟢 High Confidence", "687 instances identified"),
            ("ML Training Job Optimization", "$78K/month", "🟢 High Confidence", "SageMaker + GPU instances"),
            ("Reserved Instance Coverage", "$89K/month", "🟢 High Confidence", "Stable workload coverage"),
            ("Idle Resource Cleanup", "$67K/month", "🟢 High Confidence", "1,247 idle resources"),
            ("S3 Lifecycle Policies", "$43K/month", "🟡 Medium Confidence", "45TB candidate data"),
            ("Bedrock Response Caching", "$35K/month", "🟢 High Confidence", "Repeated queries"),
            ("EBS Volume Optimization", "$28K/month", "🟡 Medium Confidence", "Oversized volumes"),
            ("Spot Instance Migration", "$18K/month", "🟢 High Confidence", "Dev/test GPU workloads")
        ]
        
        st.markdown("### 💡 Top Optimization Recommendations")
        
        total_savings = sum([int(opp[1].replace('$','').replace('K/month','')) for opp in opportunities])
        st.success(f"**Total Monthly Savings Potential: ${total_savings}K** ({total_savings*12}K annually)")
        
        for opp, savings, confidence, detail in opportunities:
            confidence_color = "#A3BE8C" if "High" in confidence else "#EBCB8B"
            st.markdown(f"""
            <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid {confidence_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='font-size: 1.1rem;'>{opp}</strong><br/>
                        <small style='color: #D8DEE9;'>{detail}</small>
                    </div>
                    <div style='text-align: right;'>
                        <span style='color: #A3BE8C; font-size: 1.4rem; font-weight: bold;'>{savings}</span><br/>
                        <span style='font-size: 0.85rem;'>{confidence}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # AI-generated recommendations
        st.subheader("🤖 Claude-Generated Recommendations")
        st.info("""
        **Commitment Strategy Analysis** (Generated by Claude 4)
        
        Based on 90 days of usage analysis across 640 accounts:
        
        1. **Immediate Action**: Your Reserved Instances are expiring in 45 days. Current analysis suggests purchasing a 3-year Compute Savings Plan at $95K/month commitment will provide:
           - 54% discount vs on-demand
           - $296K annual savings
           - Flexible coverage across EC2, Fargate, Lambda
        
        2. **Forecasted Growth**: Your data science portfolio shows 12% month-over-month growth. Recommend split strategy:
           - 70% committed (Savings Plans)
           - 30% on-demand for burst capacity
        
        3. **Regional Optimization**: 85% of your compute runs in us-east-1. Consider zonal Reserved Instances for additional 5% savings.
        
        4. **ML Workload Optimization**: SageMaker and GPU instances represent $465K/month with high optimization potential:
           - Spot instances for training: $78K/month savings
           - Endpoint auto-scaling: $8K/month savings
           - Storage lifecycle policies: $5K/month savings
        
        **Confidence Level**: 94% | **Recommended Action**: Finance approval required (>$200K commitment)
        """)
        
        opportunities = [
            ("Right-sizing EC2 Instances", "$124K/month", "🟢 High Confidence"),
            ("Reserved Instance Coverage", "$89K/month", "🟢 High Confidence"),
            ("S3 Lifecycle Policies", "$43K/month", "🟡 Medium Confidence"),
            ("Idle Resource Cleanup", "$67K/month", "🟢 High Confidence"),
            ("EBS Volume Optimization", "$28K/month", "🟡 Medium Confidence")
        ]
        
        for opp, savings, confidence in opportunities:
            st.markdown(f"""
            <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid #A3BE8C;'>
                <strong>{opp}</strong><br/>
                <span style='color: #A3BE8C; font-size: 1.2rem;'>{savings}</span> | {confidence}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Commitment analysis
    st.subheader("📊 Commitment Utilization & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current RI Coverage", "45%", "-5% (expiring soon)")
    with col2:
        st.metric("Savings Plan Coverage", "28%", "+8% this month")
    with col3:
        st.metric("On-Demand Spend", "$1.2M/month", "-$180K vs last month")
    
    # Utilization chart
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    ri_util = np.random.normal(85, 5, 30)
    sp_util = np.random.normal(92, 3, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=ri_util, name='RI Utilization', line=dict(color='#88C0D0')))
    fig.add_trace(go.Scatter(x=dates, y=sp_util, name='Savings Plan Utilization', line=dict(color='#A3BE8C')))
    fig.add_hline(y=90, line_dash="dash", line_color="#EBCB8B", annotation_text="Target: 90%")
    fig.update_layout(
        template='plotly_dark',
        height=300,
        yaxis_title='Utilization %',
        yaxis_range=[70, 100],
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # AI-generated recommendations
    st.subheader("🤖 Claude-Generated Recommendations")
    st.info("""
    **Commitment Strategy Analysis** (Generated by Claude 4)
    
    Based on 90 days of usage analysis across 640 accounts:
    
    1. **Immediate Action**: Your Reserved Instances are expiring in 45 days. Current analysis suggests purchasing a 3-year Compute Savings Plan at $95K/month commitment will provide:
       - 54% discount vs on-demand
       - $296K annual savings
       - Flexible coverage across EC2, Fargate, Lambda
    
    2. **Forecasted Growth**: Your data science portfolio shows 12% month-over-month growth. Recommend split strategy:
       - 70% committed (Savings Plans)
       - 30% on-demand for burst capacity
    
    3. **Regional Optimization**: 85% of your compute runs in us-east-1. Consider zonal Reserved Instances for additional 5% savings.
    
    **Confidence Level**: 94% | **Recommended Action**: Finance approval required (>$200K commitment)
    """)

with tab4:
    st.header("🛡️ AWS Compliance Dashboard - Multi-Account View")
    
    st.markdown("""
    **Real-time compliance monitoring across 640+ AWS accounts** with automated remediation and continuous audit.
    Integrated with AWS Security Hub, Config, GuardDuty, and CloudTrail.
    """)
    
    # Top-level metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Overall Compliance", "97.8%", "+0.3% this week")
    with col2:
        st.metric("Compliant Accounts", "625/640", "+8 accounts")
    with col3:
        st.metric("Critical Findings", "12", "-18 remediated")
    with col4:
        st.metric("Config Rules", "1,247", "98.2% compliant")
    with col5:
        st.metric("Auto-Remediated", "156", "+23 today")
    
    st.markdown("---")
    
    # Create sub-tabs for different compliance views
    compliance_tab1, compliance_tab2, compliance_tab3, compliance_tab4, compliance_tab5 = st.tabs([
        "📊 Account Compliance Overview",
        "⚙️ AWS Config Rules",
        "🔍 Security Hub Findings",
        "🦠 Vulnerability Management",
        "🛡️ Compliance Frameworks"
    ])
    
    with compliance_tab1:
        st.subheader("Account-Level Compliance Status")
        
        # Portfolio breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Generate account compliance data
            portfolio_compliance = pd.DataFrame({
                'Portfolio': [f'Portfolio-{i}' for i in range(7)],
                'Total_Accounts': [95, 102, 88, 93, 87, 95, 80],
                'Compliant': [93, 100, 85, 91, 85, 93, 78],
                'Warning': [2, 2, 2, 2, 2, 2, 2],
                'Critical': [0, 0, 1, 0, 0, 0, 0]
            })
            
            portfolio_compliance['Compliance_Rate'] = (
                portfolio_compliance['Compliant'] / portfolio_compliance['Total_Accounts'] * 100
            ).round(1)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Compliant',
                x=portfolio_compliance['Portfolio'],
                y=portfolio_compliance['Compliant'],
                marker_color='#A3BE8C'
            ))
            
            fig.add_trace(go.Bar(
                name='Warning',
                x=portfolio_compliance['Portfolio'],
                y=portfolio_compliance['Warning'],
                marker_color='#EBCB8B'
            ))
            
            fig.add_trace(go.Bar(
                name='Critical',
                x=portfolio_compliance['Portfolio'],
                y=portfolio_compliance['Critical'],
                marker_color='#BF616A'
            ))
            
            fig.update_layout(
                barmode='stack',
                template='plotly_dark',
                height=350,
                xaxis_title='Portfolio',
                yaxis_title='Number of Accounts',
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Compliance Distribution")
            
            for idx, row in portfolio_compliance.iterrows():
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;'>
                    <strong>{row['Portfolio']}</strong><br/>
                    <div style='display: flex; justify-content: space-between;'>
                        <span>Rate: <strong style='color: #A3BE8C;'>{row['Compliance_Rate']}%</strong></span>
                        <span>{row['Compliant']}/{row['Total_Accounts']}</span>
                    </div>
                    {'<span style="color: #BF616A;">⚠️ Critical Issues</span>' if row['Critical'] > 0 else ''}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Account detail table
        st.subheader("📋 Account Compliance Details")
        
        # Generate detailed account data
        account_details = []
        statuses = ['Compliant', 'Compliant', 'Compliant', 'Compliant', 'Warning', 'Compliant', 'Critical']
        
        for i in range(20):  # Show first 20 accounts
            account_details.append({
                'Account ID': f'123456789{str(i).zfill(3)}',
                'Account Name': f'Portfolio-{i//100}-Account-{i%100}',
                'Compliance Status': statuses[i % len(statuses)],
                'Config Rules': f'{random.randint(180, 195)}/195',
                'Security Score': random.randint(85, 100),
                'Critical Findings': random.randint(0, 3),
                'Last Scan': f'{random.randint(1, 60)} min ago'
            })
        
        account_df = pd.DataFrame(account_details)
        
        # Color-code status
        def highlight_status(row):
            if row['Compliance Status'] == 'Critical':
                return ['background-color: #3B1E1E'] * len(row)
            elif row['Compliance Status'] == 'Warning':
                return ['background-color: #3B321E'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(
            account_df.style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True
        )
    
    with compliance_tab2:
        st.subheader("⚙️ AWS Config Rules Compliance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Rules", "195", "Org-wide deployment")
        with col2:
            st.metric("Compliant Resources", "1,247,892", "98.2%")
        with col3:
            st.metric("Non-Compliant", "23,156", "-8,421 this week")
        
        st.markdown("---")
        
        # Config rules by category
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### Config Rules by Category")
            
            config_categories = pd.DataFrame({
                'Category': ['Security', 'Cost Optimization', 'Reliability', 'Operational Excellence', 'Performance'],
                'Total_Rules': [68, 42, 35, 28, 22],
                'Compliant': [66, 41, 34, 28, 22],
                'Non_Compliant': [2, 1, 1, 0, 0]
            })
            
            config_categories['Compliance_Rate'] = (
                config_categories['Compliant'] / config_categories['Total_Rules'] * 100
            ).round(1)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Compliant',
                x=config_categories['Category'],
                y=config_categories['Compliant'],
                marker_color='#A3BE8C',
                text=config_categories['Compliance_Rate'].apply(lambda x: f'{x}%'),
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Non-Compliant',
                x=config_categories['Category'],
                y=config_categories['Non_Compliant'],
                marker_color='#BF616A'
            ))
            
            fig.update_layout(
                barmode='stack',
                template='plotly_dark',
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Top Non-Compliant Rules")
            
            top_violations = [
                ("s3-bucket-public-read-prohibited", 45, "Security"),
                ("encrypted-volumes", 38, "Security"),
                ("iam-password-policy", 28, "Security"),
                ("required-tags", 156, "Cost Optimization"),
                ("ec2-instance-managed-by-ssm", 89, "Operational")
            ]
            
            for rule, count, category in top_violations:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 3px solid #BF616A;'>
                    <strong>{rule}</strong><br/>
                    <small>{count} violations | {category}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Compliance trend
        st.markdown("### Config Rules Compliance Trend (90 Days)")
        
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        compliance_trend = 95 + np.cumsum(np.random.normal(0.03, 0.5, 90))
        compliance_trend = np.clip(compliance_trend, 92, 99)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=compliance_trend,
            name='Compliance Rate',
            line=dict(color='#A3BE8C', width=3),
            fill='tozeroy',
            fillcolor='rgba(163, 190, 140, 0.2)'
        ))
        
        fig.add_hline(y=95, line_dash="dash", line_color="#EBCB8B", annotation_text="Target: 95%")
        
        fig.update_layout(
            template='plotly_dark',
            height=300,
            yaxis_range=[90, 100],
            yaxis_title='Compliance %',
            xaxis_title='Date',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Auto-remediation summary
        st.info("""
        **🤖 AI-Powered Auto-Remediation Active**
        
        156 Config rule violations auto-remediated today:
        - 45 S3 buckets: Public access blocked
        - 38 EBS volumes: Encryption enabled
        - 28 IAM policies: Password policy enforced
        - 45 EC2 instances: SSM agent installed
        
        All remediations logged with Claude reasoning in audit trail.
        """)
    
    with compliance_tab3:
        st.subheader("🔍 AWS Security Hub Findings")
        
        # Security Hub metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Findings", "1,847", "-234 this week")
        with col2:
            st.metric("Critical", "12", "-18", delta_color="inverse")
        with col3:
            st.metric("High", "89", "-45", delta_color="inverse")
        with col4:
            st.metric("Medium/Low", "1,746", "-171", delta_color="inverse")
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Findings by Service")
            
            findings_by_service = pd.DataFrame({
                'Service': ['IAM', 'S3', 'EC2', 'RDS', 'Lambda', 'CloudTrail', 'KMS', 'VPC'],
                'Critical': [3, 5, 2, 1, 1, 0, 0, 0],
                'High': [15, 28, 18, 12, 8, 4, 2, 2],
                'Medium': [45, 89, 67, 34, 28, 12, 8, 15],
                'Low': [156, 234, 198, 89, 67, 45, 23, 78]
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(name='Critical', x=findings_by_service['Service'], 
                                y=findings_by_service['Critical'], marker_color='#BF616A'))
            fig.add_trace(go.Bar(name='High', x=findings_by_service['Service'], 
                                y=findings_by_service['High'], marker_color='#D08770'))
            fig.add_trace(go.Bar(name='Medium', x=findings_by_service['Service'], 
                                y=findings_by_service['Medium'], marker_color='#EBCB8B'))
            fig.add_trace(go.Bar(name='Low', x=findings_by_service['Service'], 
                                y=findings_by_service['Low'], marker_color='#5E81AC'))
            
            fig.update_layout(
                barmode='stack',
                template='plotly_dark',
                height=350,
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Critical Findings")
            
            critical_findings = [
                ("IAM root user access key exists", "prod-security-042", "⏳ Manual review"),
                ("S3 bucket allows public access", "data-staging-087", "✅ Auto-fixed"),
                ("RDS instance not encrypted", "analytics-db-021", "✅ Auto-fixed"),
                ("EC2 instance missing security patches", "web-server-156", "🔄 Patching now"),
                ("IAM policy allows full admin access", "dev-sandbox-203", "⏳ Review required")
            ]
            
            for finding, account, status in critical_findings:
                color = "#BF616A"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 4px solid {color};'>
                    <strong style='font-size: 0.9rem;'>{finding}</strong><br/>
                    <small>{account}</small><br/>
                    <small>{status}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # GuardDuty integration
        st.markdown("### 🕵️ GuardDuty Threat Detection")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Threats", "8", "-12 resolved")
        with col2:
            st.metric("Suspicious Activity", "23", "Last 24h")
        with col3:
            st.metric("Auto-Blocked IPs", "156", "This week")
        
        guardduty_findings = [
            ("UnauthorizedAccess:EC2/SSHBruteForce", "prod-web-042", "🔴 Active", "8 attempts from 185.220.101.x"),
            ("CryptoCurrency:EC2/BitcoinTool", "dev-test-128", "✅ Blocked", "Instance terminated automatically"),
            ("Recon:EC2/PortProbeUnprotectedPort", "staging-api-067", "🟡 Monitoring", "Port 22 exposed"),
            ("UnauthorizedAccess:IAMUser/MaliciousIPCaller", "shared-services-021", "✅ Blocked", "IP blacklisted")
        ]
        
        for finding, account, status, detail in guardduty_findings:
            if "Active" in status:
                color = "#BF616A"
            elif "Blocked" in status:
                color = "#A3BE8C"
            else:
                color = "#EBCB8B"
            
            st.markdown(f"""
            <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid {color};'>
                <strong>{finding}</strong> {status}<br/>
                <small>Account: {account}</small><br/>
                <small style='color: #D8DEE9;'>{detail}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with compliance_tab4:
        st.subheader("🦠 Vulnerability Management - OS & Containers")
        
        st.markdown("""
        **Comprehensive vulnerability scanning** across Windows, Linux, and container workloads using AWS Inspector, 
        Systems Manager Patch Manager, and Amazon ECR scanning.
        """)
        
        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Vulnerabilities", "8,947", "-1,234 this week")
        with col2:
            st.metric("Critical (CVE)", "89", "-45", delta_color="inverse")
        with col3:
            st.metric("Unpatched Instances", "234", "-67", delta_color="inverse")
        with col4:
            st.metric("Container Vulns", "1,245", "-189", delta_color="inverse")
        with col5:
            st.metric("Patch Compliance", "94.3%", "+2.1%")
        
        st.markdown("---")
        
        # OS Vulnerability Breakdown
        st.markdown("### 🖥️ Operating System Vulnerabilities")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # OS vulnerability data
            os_vuln_data = pd.DataFrame({
                'OS': ['Amazon Linux 2', 'Ubuntu 20.04', 'Ubuntu 22.04', 'Windows Server 2019', 'Windows Server 2022', 'RHEL 8', 'CentOS 7'],
                'Instances': [1245, 892, 567, 423, 312, 234, 189],
                'Critical': [12, 8, 4, 23, 8, 6, 15],
                'High': [45, 34, 18, 89, 34, 28, 45],
                'Medium': [123, 89, 45, 234, 78, 67, 123],
                'Low': [345, 267, 156, 456, 234, 189, 278]
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(name='Critical', x=os_vuln_data['OS'], 
                                y=os_vuln_data['Critical'], marker_color='#BF616A'))
            fig.add_trace(go.Bar(name='High', x=os_vuln_data['OS'], 
                                y=os_vuln_data['High'], marker_color='#D08770'))
            fig.add_trace(go.Bar(name='Medium', x=os_vuln_data['OS'], 
                                y=os_vuln_data['Medium'], marker_color='#EBCB8B'))
            fig.add_trace(go.Bar(name='Low', x=os_vuln_data['OS'], 
                                y=os_vuln_data['Low'], marker_color='#5E81AC'))
            
            fig.update_layout(
                barmode='stack',
                template='plotly_dark',
                height=350,
                xaxis_tickangle=-45,
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                title='Vulnerabilities by Operating System'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Critical CVEs")
            
            critical_cves = [
                ("CVE-2024-1086", "Linux Kernel", "9.8", "✅ Patched: 98%"),
                ("CVE-2024-21626", "runc container", "8.6", "✅ Patched: 95%"),
                ("CVE-2024-0056", "Windows RCE", "9.8", "🔄 Patching: 67%"),
                ("CVE-2024-23897", "Log4j", "9.1", "✅ Patched: 100%"),
                ("CVE-2024-3094", "XZ Utils", "10.0", "✅ Patched: 99%")
            ]
            
            for cve, component, score, status in critical_cves:
                score_color = "#BF616A" if float(score) >= 9.0 else "#D08770"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 4px solid {score_color};'>
                    <strong>{cve}</strong><br/>
                    <small>{component}</small><br/>
                    <span style='color: {score_color}; font-weight: bold;'>CVSS: {score}</span><br/>
                    <small>{status}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Container Vulnerabilities
        st.markdown("### 🐳 Container Image Vulnerabilities")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Container vulnerability data
            container_data = pd.DataFrame({
                'Repository': ['web-frontend', 'api-gateway', 'auth-service', 'data-processor', 'ml-training', 'logging-agent'],
                'Images': [45, 34, 28, 23, 18, 12],
                'Critical': [3, 5, 2, 8, 12, 1],
                'High': [12, 15, 8, 23, 34, 5],
                'Medium': [34, 45, 28, 67, 89, 23],
                'Last_Scan': ['2h ago', '4h ago', '1h ago', '6h ago', '12h ago', '3h ago']
            })
            
            st.dataframe(
                container_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Images": st.column_config.NumberColumn("Images", width="small"),
                    "Critical": st.column_config.NumberColumn("Critical", width="small"),
                    "High": st.column_config.NumberColumn("High", width="small"),
                    "Medium": st.column_config.NumberColumn("Medium", width="small"),
                    "Last_Scan": st.column_config.TextColumn("Last Scan", width="small")
                }
            )
            
            st.info("""
            **🔍 Amazon ECR Image Scanning Active**
            
            - Scan on push enabled for all repositories
            - Enhanced scanning with Amazon Inspector
            - Base image vulnerability tracking
            - Automated remediation for known CVEs
            - Integration with CI/CD pipelines for blocking
            """)
        
        with col2:
            st.markdown("### Container Scan Results")
            
            # Pie chart for container vulnerabilities
            container_summary = pd.DataFrame({
                'Severity': ['Critical', 'High', 'Medium', 'Low'],
                'Count': [31, 97, 286, 831]
            })
            
            fig = go.Figure(data=[go.Pie(
                labels=container_summary['Severity'],
                values=container_summary['Count'],
                marker_colors=['#BF616A', '#D08770', '#EBCB8B', '#5E81AC'],
                hole=0.4
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=250,
                showlegend=True,
                title='Container Vulnerabilities'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Patch Management
        st.markdown("### 🔧 Patch Management & Remediation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Windows Patching")
            st.metric("Compliant Servers", "345/423", "81.6%")
            
            st.markdown("""
            **Last Patch Cycle:**
            - Deployed: 156 patches
            - Success rate: 94.2%
            - Failed: 9 servers (investigating)
            - Next cycle: Tonight 2:00 AM
            
            **Systems Manager:**
            - Patch baseline: Custom-Windows-Baseline
            - Maintenance window: Sun 02:00-04:00
            - Auto-reboot: Enabled with rollback
            """)
        
        with col2:
            st.markdown("#### Linux Patching")
            st.metric("Compliant Servers", "2,834/2,989", "94.8%")
            
            st.markdown("""
            **Last Patch Cycle:**
            - Deployed: 487 patches
            - Success rate: 97.1%
            - Failed: 12 servers (auto-retry scheduled)
            - Next cycle: Rolling (every 4 hours)
            
            **Systems Manager:**
            - Patch baseline: Custom-Linux-Baseline
            - Maintenance window: Rolling
            - Auto-reboot: Conditional
            """)
        
        with col3:
            st.markdown("#### Container Remediation")
            st.metric("Updated Images", "142/160", "88.8%")
            
            st.markdown("""
            **Auto-Remediation:**
            - Base images updated: 89
            - Rebuilt from source: 53
            - Pending rebuild: 18
            - Next scan: Continuous
            
            **ECR Policies:**
            - Critical vulns: Block deployment
            - High vulns: Alert + track
            - Lifecycle: Auto-delete old images
            """)
        
        st.markdown("---")
        
        # AWS Inspector Integration
        st.markdown("### 🔍 AWS Inspector Findings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Inspector findings trend
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            critical_trend = 120 - np.cumsum(np.random.uniform(0.5, 2, 30))
            high_trend = 340 - np.cumsum(np.random.uniform(2, 5, 30))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=critical_trend,
                name='Critical',
                line=dict(color='#BF616A', width=3),
                fill='tozeroy',
                fillcolor='rgba(191, 97, 106, 0.2)'
            ))
            
            fig.add_trace(go.Scatter(
                x=dates, y=high_trend,
                name='High',
                line=dict(color='#D08770', width=2)
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                title='Vulnerability Trend (30 Days)',
                xaxis_title='Date',
                yaxis_title='Finding Count',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Inspector Configuration")
            
            st.success("""
            **✅ Active Scanning:**
            - EC2 instances: 3,862 scanned
            - ECR repositories: 160 monitored
            - Lambda functions: 1,247 analyzed
            - Continuous monitoring enabled
            
            **Finding Types:**
            - Network reachability
            - Package vulnerabilities
            - Code vulnerabilities (Lambda)
            - Container image vulnerabilities
            
            **Auto-Remediation:**
            - Systems Manager automation
            - Lambda for container rebuilds
            - SNS notifications to DevOps
            - ServiceNow ticket creation
            """)
        
        st.markdown("---")
        
        # AI-Powered Vulnerability Prioritization
        st.markdown("### 🤖 AI-Powered Vulnerability Prioritization")
        
        st.info("""
        **Claude 4 Intelligent Risk Assessment**
        
        The AI platform analyzes vulnerabilities based on:
        
        1. **CVSS Score** - Base severity rating
        2. **Exploitability** - Known exploits in the wild
        3. **Asset Criticality** - Production vs. dev/test
        4. **Network Exposure** - Internet-facing vs. internal
        5. **Data Sensitivity** - PCI/HIPAA compliance requirements
        6. **Patch Availability** - Vendor patch released vs. workaround only
        7. **Business Impact** - Downtime risk, revenue impact
        
        **Example AI Reasoning:**
        
        *CVE-2024-0056 on prod-web-042 (Windows Server 2019):*
        - CVSS: 9.8 (Critical)
        - Internet-facing: Yes (port 443 exposed)
        - Handles: Payment processing (PCI scope)
        - Exploit available: Yes (Metasploit module exists)
        - Patch available: Yes (KB5034441)
        
        **AI Priority: CRITICAL - Patch within 24 hours**
        
        Recommended action: Deploy patch during next maintenance window (Tonight 2:00 AM) with 
        automated rollback enabled. Temporarily enable WAF rules for RCE protection until patched.
        
        *Actions taken:*
        - ✅ Maintenance window scheduled
        - ✅ WAF rules activated
        - ✅ Backup snapshot created
        - ✅ Rollback plan validated
        - 🔔 DevOps team notified via Slack
        """)
    
    with compliance_tab5:
        st.subheader("🏛️ Compliance Framework Status")
        
        st.markdown("""
        **Multi-framework compliance monitoring** with automated evidence collection and continuous assessment.
        """)
        
        # Framework overview
        frameworks_data = pd.DataFrame({
            'Framework': ['PCI DSS', 'HIPAA', 'SOC 2 Type II', 'GDPR', 'ISO 27001', 'NIST CSF'],
            'Compliance': [98.2, 96.8, 99.1, 97.3, 95.6, 98.4],
            'Controls': [312, 184, 64, 89, 114, 98],
            'Compliant': [306, 178, 63, 87, 109, 96],
            'In_Progress': [4, 4, 1, 2, 3, 2],
            'Non_Compliant': [2, 2, 0, 0, 2, 0]
        })
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=frameworks_data['Framework'],
                y=frameworks_data['Compliance'],
                marker_color=['#A3BE8C' if x >= 97 else '#EBCB8B' if x >= 95 else '#D08770' 
                             for x in frameworks_data['Compliance']],
                text=frameworks_data['Compliance'].apply(lambda x: f'{x}%'),
                textposition='outside'
            ))
            
            fig.add_hline(y=95, line_dash="dash", line_color="#BF616A", annotation_text="Minimum: 95%")
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                yaxis_range=[90, 102],
                yaxis_title='Compliance %',
                title='Framework Compliance Status'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Framework Details")
            
            for idx, row in frameworks_data.iterrows():
                compliance_color = "#A3BE8C" if row['Compliance'] >= 97 else "#EBCB8B" if row['Compliance'] >= 95 else "#D08770"
                
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;'>
                    <strong>{row['Framework']}</strong><br/>
                    <div style='font-size: 1.5rem; color: {compliance_color}; font-weight: bold;'>{row['Compliance']}%</div>
                    <div style='font-size: 0.85rem;'>
                        ✅ {row['Compliant']}/{row['Controls']} controls<br/>
                        🔄 {row['In_Progress']} in progress
                        {f"<br/>❌ {row['Non_Compliant']} non-compliant" if row['Non_Compliant'] > 0 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Evidence collection
        st.markdown("### 📁 Automated Evidence Collection")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("""
            **CloudTrail Logs**
            - 640 accounts monitored
            - 12 months retention
            - Real-time aggregation
            - S3 + Athena queryable
            """)
        
        with col2:
            st.info("""
            **Config Snapshots**
            - Resource configurations
            - Change history tracked
            - Compliance timeline
            - Point-in-time recovery
            """)
        
        with col3:
            st.warning("""
            **Security Hub Evidence**
            - Finding aggregation
            - Cross-account view
            - Remediation tracking
            - Audit-ready reports
            """)
        
        st.markdown("---")
        
        # Service Control Policies
        st.markdown("### 🔐 Service Control Policies (SCPs)")
        
        scp_data = pd.DataFrame({
            'Policy': ['DenyRootUser', 'RequireEncryption', 'AllowedRegions', 'RequireMFA', 'DenyPublicS3'],
            'Applied_OUs': [7, 7, 7, 6, 7],
            'Accounts_Covered': [640, 640, 640, 580, 640],
            'Violations_Blocked': [23, 89, 12, 45, 234],
            'Status': ['✅ Active', '✅ Active', '✅ Active', '✅ Active', '✅ Active']
        })
        
        st.dataframe(scp_data, use_container_width=True, hide_index=True)
        
        st.success("""
        **🛡️ Preventive Controls Active**
        
        Service Control Policies enforce security boundaries at the AWS Organizations level:
        - **Root user actions blocked** across all accounts
        - **Unencrypted storage prohibited** (EBS, S3, RDS)
        - **Geographic restrictions** enforced (US/EU regions only)
        - **MFA required** for sensitive operations
        - **Public S3 buckets prevented** organization-wide
        
        All SCP violations are logged and alerted in real-time.
        """)

with tab5:
    st.header("📈 Analytics & Predictive Insights")
    
    # Forecast
    st.subheader("🔮 AI-Powered Cost Forecast")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Generate forecast data
        past_dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        future_dates = pd.date_range(start=datetime.now(), periods=90, freq='D')
        
        past_cost = 2500000 + np.cumsum(np.random.normal(3000, 20000, 90))
        future_cost = past_cost[-1] + np.cumsum(np.random.normal(2000, 15000, 90))
        
        # Add seasonality
        future_cost += np.sin(np.linspace(0, 4*np.pi, 90)) * 50000
        
        # Confidence intervals
        upper_bound = future_cost + 100000
        lower_bound = future_cost - 100000
        
        fig = go.Figure()
        
        # Historical
        fig.add_trace(go.Scatter(
            x=past_dates, y=past_cost,
            name='Historical',
            line=dict(color='#88C0D0', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates, y=future_cost,
            name='Forecast',
            line=dict(color='#A3BE8C', width=2, dash='dash')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates[::-1]),
            y=list(upper_bound) + list(lower_bound[::-1]),
            fill='toself',
            fillcolor='rgba(163, 190, 140, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence',
            showlegend=True
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            xaxis_title='Date',
            yaxis_title='Total Cost ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Forecast Summary")
        st.metric("Q4 Projected Spend", "$8.4M", "+12% vs Q3")
        st.metric("Confidence Level", "87%")
        st.metric("Key Driver", "Data Science Growth")
        
        st.markdown("---")
        
        st.markdown("### Risk Factors")
        st.warning("⚠️ ML workload growth 18% MoM")
        st.info("ℹ️ Black Friday spike expected")
        st.success("✅ RI renewal optimized")
    
    st.markdown("---")
    
    # Trend analysis
    st.subheader("📊 Trend Analysis & Anomaly Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Service Growth Trends")
        
        services_trend = pd.DataFrame({
            'Service': ['EC2', 'RDS', 'S3', 'Lambda', 'EKS'],
            'Growth_30d': [5, -2, 12, 24, 15],
            'Trend': ['Stable', 'Declining', 'Growing', 'Rapid Growth', 'Growing']
        })
        
        fig = go.Figure(data=[
            go.Bar(
                x=services_trend['Service'],
                y=services_trend['Growth_30d'],
                marker_color=['#A3BE8C' if x > 0 else '#BF616A' for x in services_trend['Growth_30d']]
            )
        ])
        fig.update_layout(
            template='plotly_dark',
            height=300,
            yaxis_title='Growth %',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### AI-Generated Insights")
        
        st.info("""
        **Claude Analysis** (Last 7 days):
        
        1. **Lambda growth spike**: +24% attributed to new microservices deployment. Cost trajectory sustainable with current Savings Plan.
        
        2. **RDS decline**: -2% due to successful database consolidation project. Expected to stabilize.
        
        3. **S3 growth**: +12% from data lake expansion. Recommend implementing lifecycle policies for objects >90 days old.
        
        **Action Items**:
        - Monitor Lambda concurrency limits
        - Review S3 storage class distribution
        - Evaluate RDS instance right-sizing opportunities
        """)
    
    # Regional distribution
    st.subheader("🌍 Global Resource Distribution")
    
    region_data = pd.DataFrame({
        'Region': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'eu-central-1'],
        'Cost': [1200000, 680000, 420000, 310000, 190000],
        'Resources': [3245, 1876, 1234, 892, 567]
    })
    
    fig = px.bar(region_data, x='Region', y='Cost', color='Resources',
                 color_continuous_scale='tealgrn')
    fig.update_layout(template='plotly_dark', height=350)
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.header("📋 Audit Trail & Compliance Evidence")
    
    st.markdown("""
    Complete audit trail of all AI agent decisions with Claude reasoning, context, and outcomes. 
    All data retained for 7 years for compliance requirements.
    """)
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_agent = st.selectbox("Agent", ["All", "Cost Optimization", "Commitment", "Anomaly", "Forecast", "Storage", "Placement"])
    with col2:
        filter_status = st.selectbox("Status", ["All", "Completed", "In Progress", "Pending Approval", "Rolled Back"])
    with col3:
        filter_impact = st.selectbox("Impact", ["All", "High (>$10K)", "Medium ($1K-$10K)", "Low (<$1K)"])
    with col4:
        filter_date = st.date_input("Date Range", datetime.now() - timedelta(days=7))
    
    st.markdown("---")
    
    # Audit records
    st.subheader("📝 Decision Audit Log")
    
    audit_records = [
        {
            'Timestamp': datetime.now() - timedelta(hours=2),
            'Decision_ID': 'DEC-2024-11-23-00142',
            'Agent': 'Cost Optimization',
            'Action': 'Right-sized t3.2xlarge → t3.large',
            'Account': 'prod-web-042',
            'Impact': '$2,190/month',
            'Confidence': '94%',
            'Status': '✅ Completed',
            'Execution_Time': '1.3s'
        },
        {
            'Timestamp': datetime.now() - timedelta(hours=5),
            'Decision_ID': 'DEC-2024-11-23-00138',
            'Agent': 'Anomaly Detection',
            'Action': 'Detected unusual SageMaker spend',
            'Account': 'prod-ds-087',
            'Impact': '$25,200/day anomaly',
            'Confidence': '98%',
            'Status': '🔔 Alert Sent',
            'Execution_Time': '0.8s'
        },
        {
            'Timestamp': datetime.now() - timedelta(hours=8),
            'Decision_ID': 'DEC-2024-11-23-00129',
            'Agent': 'Storage Optimizer',
            'Action': 'Migrated 2.3TB to Glacier',
            'Account': 'backup-storage-021',
            'Impact': '$1,840/month',
            'Confidence': '99%',
            'Status': '✅ Completed',
            'Execution_Time': '2.1s'
        },
        {
            'Timestamp': datetime.now() - timedelta(hours=12),
            'Decision_ID': 'DEC-2024-11-23-00115',
            'Agent': 'Commitment',
            'Action': 'Recommended 3yr Savings Plan',
            'Account': 'portfolio-finance',
            'Impact': '$296,400/year',
            'Confidence': '91%',
            'Status': '⏳ Pending CFO Approval',
            'Execution_Time': '3.2s'
        },
        {
            'Timestamp': datetime.now() - timedelta(hours=18),
            'Decision_ID': 'DEC-2024-11-22-00298',
            'Agent': 'Security',
            'Action': 'Auto-remediated public S3 bucket',
            'Account': 'dev-sandbox-156',
            'Impact': 'Critical security fix',
            'Confidence': '100%',
            'Status': '✅ Completed',
            'Execution_Time': '0.5s'
        }
    ]
    
    audit_df = pd.DataFrame(audit_records)
    
    st.dataframe(
        audit_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": st.column_config.DatetimeColumn(
                "Timestamp",
                format="MMM DD, HH:mm:ss"
            ),
            "Impact": st.column_config.TextColumn("Impact", width="medium"),
            "Confidence": st.column_config.TextColumn("Confidence", width="small")
        }
    )
    
    st.markdown("---")
    
    # Detailed decision view
    st.subheader("🔍 Decision Details & Claude Reasoning")
    
    decision_id = st.selectbox(
        "Select Decision to View:",
        [record['Decision_ID'] for record in audit_records]
    )
    
    if st.button("📖 View Full Decision Context"):
        with st.expander("Complete Decision Record", expanded=True):
            st.markdown(f"""
            ### Decision ID: {decision_id}
            
            **Execution Metadata:**
            - Timestamp: {audit_records[0]['Timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}
            - Agent: {audit_records[0]['Agent']}
            - Model: Claude 4 Sonnet (anthropic.claude-4-sonnet-20250514)
            - Execution Time: {audit_records[0]['Execution_Time']}
            - Status: {audit_records[0]['Status']}
            
            ---
            
            **Input Context:**
            ```json
            {{
              "event_type": "cloudwatch_alarm",
              "resource": {{
                "instance_id": "i-0abc123def456",
                "instance_type": "t3.2xlarge",
                "account_id": "123456789042",
                "region": "us-east-1"
              }},
              "metrics": {{
                "cpu_utilization_avg": 25.3,
                "memory_utilization_avg": 42.1,
                "network_io_avg_mbps": 45.2,
                "disk_io_avg_iops": 120
              }},
              "timeframe": "last_30_days"
            }}
            ```
            
            ---
            
            **Claude 4 Reasoning:**
            {simulate_claude_reasoning('cost_optimization')}
            
            ---
            
            **Execution Result:**
            ```json
            {{
              "action_taken": "instance_resize",
              "original_type": "t3.2xlarge",
              "new_type": "t3.large",
              "success": true,
              "rollback_available": true,
              "snapshot_id": "snap-0def456abc789",
              "cost_impact": {{
                "monthly_before": 4380.00,
                "monthly_after": 2190.00,
                "savings": 2190.00
              }},
              "performance_verification": {{
                "cpu_headroom": "2.1x",
                "memory_headroom": "1.8x",
                "risk_level": "low"
              }}
            }}
            ```
            
            ---
            
            **Compliance & Audit:**
            - ✅ Action within autonomous approval threshold (<$10K/month)
            - ✅ Maintenance window respected (Sunday 02:00-04:00 UTC)
            - ✅ Rollback plan validated
            - ✅ All API calls logged to CloudTrail
            - ✅ Decision reasoning stored in S3 (7-year retention)
            - ✅ Notification sent to #cloud-ops Slack channel
            
            **Retrievable Data:**
            - CloudWatch Logs: `/aws/lambda/cost-optimization-agent`
            - S3 Archive: `s3://audit-trail/decisions/2024/11/23/{decision_id}.json`
            - DynamoDB: Table `agent-decisions`, PK `{decision_id}`
            - Athena Query: Available via `audit_trail` database
            """)
    
    st.markdown("---")
    
    # Export options
    st.subheader("📥 Export & Reporting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate Compliance Report", use_container_width=True):
            st.success("✅ Compliance report generated (PDF)")
            st.download_button(
                "Download Report",
                data="Mock report data",
                file_name="compliance_report_2024-11-23.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.success("✅ Audit log exported")
            st.download_button(
                "Download Excel",
                data=audit_df.to_csv(index=False),
                file_name="audit_log_2024-11-23.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🔍 Athena Query Template", use_container_width=True):
            st.code("""
SELECT 
  decision_id,
  agent_name,
  action_type,
  account_id,
  cost_impact,
  confidence_score,
  timestamp
FROM audit_trail.decisions
WHERE 
  date >= '2024-11-01'
  AND agent_name = 'Cost Optimization'
  AND cost_impact > 1000
ORDER BY timestamp DESC
LIMIT 100;
            """, language="sql")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #D8DEE9; padding: 2rem;'>
    <strong>AI-Powered Cloud Operations Platform</strong><br/>
    Built with AWS Bedrock, Claude 4 Sonnet, and Streamlit<br/>
    <small>Demo Version | For Client Presentation</small>
</div>
""", unsafe_allow_html=True)