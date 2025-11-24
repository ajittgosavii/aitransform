import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
import json

# Optional AWS imports - gracefully handle if not installed
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

# Page configuration
st.set_page_config(
    page_title="Tech Guardrails Platform | AI Cloud Operations",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ FIXED CSS - ALL TEXT VISIBLE ============
st.markdown("""
<style>
    /* ============ FORCE ALL TEXT WHITE ============ */
    .stApp, .main {
        background-color: #0F172A !important;
    }
    
    /* AGGRESSIVE: ALL TEXT WHITE */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stMarkdown li, .element-container, .stText, p, span, li {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    
    /* Labels */
    label, .stSelectbox label, .stRadio label, .stTextInput label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* ============ RADIO BUTTONS - CRITICAL FIX ============ */
    /* Target ALL radio button text elements */
    .stRadio {
        color: #FFFFFF !important;
    }
    .stRadio label {
        color: #FFFFFF !important;
    }
    .stRadio p {
        color: #FFFFFF !important;
    }
    .stRadio span {
        color: #FFFFFF !important;
    }
    .stRadio div {
        color: #FFFFFF !important;
    }
    
    /* Radio option text - multiple selectors for maximum coverage */
    [data-testid="stRadio"] label {
        color: #FFFFFF !important;
    }
    [data-testid="stRadio"] p {
        color: #FFFFFF !important;
    }
    [data-testid="stRadio"] span {
        color: #FFFFFF !important;
    }
    
    /* BaseWeb radio component text */
    [data-baseweb="radio"] ~ div {
        color: #FFFFFF !important;
    }
    [data-baseweb="radio"] + div {
        color: #FFFFFF !important;
    }
    [data-baseweb="radio-group"] label {
        color: #FFFFFF !important;
    }
    [data-baseweb="radio-group"] p {
        color: #FFFFFF !important;
    }
    
    /* Role-based selectors */
    [role="radiogroup"] label {
        color: #FFFFFF !important;
    }
    [role="radiogroup"] p {
        color: #FFFFFF !important;
    }
    [role="radiogroup"] span {
        color: #FFFFFF !important;
    }
    [role="radiogroup"] div {
        color: #FFFFFF !important;
    }
    
    /* Markdown inside radio */
    .stRadio [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    
    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 2px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        height: 52px;
        background: linear-gradient(180deg, #334155 0%, #1E293B 100%);
        border-radius: 8px;
        padding: 12px 18px;
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF !important;
        border: 1px solid #475569;
        text-transform: uppercase;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(180deg, #475569 0%, #334155 100%);
        border-color: #10B981;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border-color: #34D399 !important;
    }
    
    /* ============ METRICS ============ */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #10B981 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    /* ============ SIDEBAR ============ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-right: 2px solid #334155;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* SIDEBAR RADIO BUTTONS - Force white text */
    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio p {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio div {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    
    /* ============ BUTTONS ============ */
    .stButton > button {
        border-radius: 8px;
        font-weight: 700;
        border: 2px solid #10B981;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
    }
    
    /* ============ SELECTBOX - BLACK TEXT ON WHITE ============ */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
    }
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div {
        color: #000000 !important;
    }
    .stSelectbox svg {
        fill: #000000 !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"], [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li:hover {
        background-color: #E2E8F0 !important;
    }
    [data-baseweb="menu"] [aria-selected="true"] {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
    }
    
    /* ============ RADIO - VISIBLE TEXT ============ */
    /* Radio container - keep transparent for sidebar */
    .stRadio > div {
        background-color: transparent !important;
        padding: 8px !important;
        border-radius: 8px !important;
    }
    
    /* Radio group label (the title above radio buttons) */
    .stRadio > label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* Each radio option container */
    .stRadio [role="radiogroup"] {
        gap: 8px !important;
    }
    
    /* Radio option labels - THE KEY FIX */
    .stRadio [role="radiogroup"] label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }
    
    .stRadio [role="radiogroup"] label p,
    .stRadio [role="radiogroup"] label span,
    .stRadio [role="radiogroup"] label div {
        color: #FFFFFF !important;
    }
    
    /* Radio button text specifically */
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }
    
    /* Horizontal radio buttons */
    .stRadio [data-baseweb="radio"] {
        background-color: transparent !important;
    }
    
    /* The actual text next to radio circle */
    .stRadio div[data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }
    .stRadio div[data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        margin: 0 !important;
    }
    
    /* ============ TEXT INPUT ============ */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #334155 !important;
    }
    
    /* ============ DATA TABLES ============ */
    .dataframe, .dataframe th, .dataframe td {
        color: #FFFFFF !important;
        background-color: #1E293B !important;
    }
    .dataframe th {
        background-color: #334155 !important;
    }
    
    /* ============ EXPANDERS ============ */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        color: #10B981 !important;
    }
    details, details * {
        color: #FFFFFF !important;
    }
    
    /* ============ CODE ============ */
    code, pre {
        background-color: #1E293B !important;
        color: #34D399 !important;
    }
    
    /* ============ ALERTS ============ */
    .stSuccess { background-color: #0D3D2E !important; border-left: 4px solid #22C55E !important; }
    .stWarning { background-color: #3D2E0D !important; border-left: 4px solid #F59E0B !important; }
    .stError { background-color: #3D0D0D !important; border-left: 4px solid #EF4444 !important; }
    .stInfo { background-color: #0D2D3D !important; border-left: 4px solid #3B82F6 !important; }
    
    /* ============ PROGRESS ============ */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10B981 0%, #34D399 100%) !important;
    }
    
    /* ============ LAYOUT ============ */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    hr { border-color: #334155 !important; }
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📊 Dashboard", 
    "🤖 AI Agents", 
    "🛡️ Security",
    "⚖️ Compliance",
    "⚙️ DevOps",
    "🗄️ Database",
    "💰 FinOps",
    "📋 Policy",
    "📈 Analytics",
    "📋 Audit"
])

with tab1:
    # ============ TECHGUARD RAILS - UNIFIED COMMAND CENTER ============
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 2.5rem; font-weight: 800; color: #10B981; margin-bottom: 8px;'>
            🛡️ TechGuard Rails Command Center
        </h1>
        <p style='font-size: 1.1rem; color: #94A3B8;'>
            Unified Operations Dashboard | 640+ AWS Accounts | 6 AI Agents | Real-Time Autonomous Operations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ TOP-LEVEL KPIs ============
    st.markdown("### 📊 Platform Overview")
    
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    with kpi1:
        st.metric("AWS Accounts", "640", delta="+3 this week")
    with kpi2:
        st.metric("AI Actions (24h)", str(st.session_state.actions_executed + 156), delta="+23%")
    with kpi3:
        st.metric("Cost Savings", f"${st.session_state.cost_savings + 487000:,}", delta="+$89K")
    with kpi4:
        st.metric("Threats Blocked", "47", delta="-8 vs yesterday", delta_color="inverse")
    with kpi5:
        st.metric("Compliance", "97.2%", delta="+0.4%")
    with kpi6:
        st.metric("Uptime", "99.97%", delta="+0.02%")
    
    st.markdown("---")
    
    # ============ ALL 6 AGENTS STATUS - SINGLE VIEW ============
    st.markdown("### 🤖 AI Agent Status - All Systems")
    
    agent_col1, agent_col2, agent_col3 = st.columns(3)
    
    with agent_col1:
        # Security Agent
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>🛡️ Security Agent</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Threats Blocked</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>47</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Response Time</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>1.2s</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Risk Score</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #22C55E;'>23/100</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Compliance Agent
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>⚖️ Compliance Agent</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Score</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>97.2%</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Violations Fixed</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>34</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Frameworks</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>5</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with agent_col2:
        # DevOps Agent
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>⚙️ DevOps Agent</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Pipelines</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>23</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Optimized</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>47</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Build Time</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>-45%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Database Agent
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>🗄️ Database Agent</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Access Requests</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>32</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Auto-Approved</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>28</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Active</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>18</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with agent_col3:
        # FinOps Agent
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>💰 FinOps Agent</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Monthly Spend</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>$2.8M</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Savings</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #22C55E;'>$487K</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Optimization</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>18.2%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Policy Engine
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #F1F5F9;'>📋 Policy Engine</span>
                <span style='background: #22C55E; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='margin-top: 12px; display: flex; gap: 20px;'>
                <div><span style='color: #94A3B8; font-size: 12px;'>Active Policies</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>87</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>AI-Generated</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>34</span></div>
                <div><span style='color: #94A3B8; font-size: 12px;'>Effectiveness</span><br/><span style='font-size: 1.5rem; font-weight: 700; color: #10B981;'>96.4%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ FINOPS & COST OVERVIEW ============
    st.markdown("### 💰 FinOps Intelligence - Cost & Savings Overview")
    
    fin_col1, fin_col2 = st.columns([2, 1])
    
    with fin_col1:
        # Cost trend chart
        cost_data = generate_cost_trend_data(mode=st.session_state.mode)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cost_data['Date'],
            y=cost_data['Baseline'],
            name='Baseline (No AI)',
            line=dict(color='#EF4444', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=cost_data['Date'],
            y=cost_data['Optimized'],
            name='AI-Optimized',
            line=dict(color='#10B981', width=3),
            fill='tonexty',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Date',
            yaxis_title='Daily Cost ($)',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            font=dict(color='#F1F5F9')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with fin_col2:
        st.markdown("#### 📈 Savings Breakdown")
        
        savings_data = {
            'Category': ['EC2 Rightsizing', 'Idle Resources', 'RI/Savings Plans', 'Storage Optimization', 'Other'],
            'Savings': [156000, 89000, 134000, 67000, 41000]
        }
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=savings_data['Category'],
            values=savings_data['Savings'],
            hole=.4,
            marker_colors=['#10B981', '#22C55E', '#34D399', '#6EE7B7', '#A7F3D0']
        )])
        fig_pie.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.3),
            font=dict(color='#F1F5F9')
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.success(f"**Total Savings (30d):** ${sum(savings_data['Savings']):,}")
    
    st.markdown("---")
    
    # ============ SECURITY & COMPLIANCE SUMMARY ============
    st.markdown("### 🛡️ Security & Compliance Summary")
    
    sec_col1, sec_col2, sec_col3 = st.columns(3)
    
    with sec_col1:
        st.markdown("#### Threat Detection")
        threat_data = {'Status': ['Blocked', 'Remediating', 'Pending'], 'Count': [42, 3, 2]}
        
        fig_bar = go.Figure(data=[go.Bar(
            x=threat_data['Status'],
            y=threat_data['Count'],
            marker_color=['#22C55E', '#F59E0B', '#EF4444']
        )])
        fig_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=250,
            font=dict(color='#F1F5F9')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with sec_col2:
        st.markdown("#### Compliance by Framework")
        frameworks = {'Framework': ['PCI DSS', 'HIPAA', 'SOC 2', 'ISO 27001', 'GDPR'], 
                     'Score': [96.5, 98.2, 94.8, 97.1, 99.0]}
        
        for fw, score in zip(frameworks['Framework'], frameworks['Score']):
            color = '#22C55E' if score >= 95 else '#F59E0B' if score >= 90 else '#EF4444'
            st.markdown(f"**{fw}**: {score}%")
            st.progress(score/100)
    
    with sec_col3:
        st.markdown("#### Recent Actions")
        recent_actions = [
            ("🛡️ Blocked S3 exposure", "2 min ago"),
            ("💰 Terminated idle RDS", "5 min ago"),
            ("⚖️ Fixed Config violation", "12 min ago"),
            ("🗄️ Granted DB access", "18 min ago"),
            ("📋 Deployed new policy", "25 min ago")
        ]
        
        for action, time in recent_actions:
            st.markdown(f"""
            <div style='background: #1E293B; padding: 10px 12px; border-radius: 6px; margin: 6px 0; border-left: 3px solid #10B981;'>
                <span style='color: #F1F5F9; font-weight: 500;'>{action}</span><br/>
                <small style='color: #64748B;'>{time}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ RECENT ACTIVITY TABLE ============
    st.markdown("### 📋 Recent Agent Activity Log")
    
    activity_df = generate_agent_activity()
    st.dataframe(
        activity_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": st.column_config.DatetimeColumn("Timestamp", format="MMM DD, HH:mm"),
            "Impact": st.column_config.TextColumn("Impact", width="small")
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

with tab7:
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

with tab9:
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

with tab10:
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

# ==================== TAB 3: SECURITY AGENT ====================
with tab3:
    st.header("🛡️ Security Agent")
    st.markdown("**Autonomous threat detection and remediation powered by Claude 4**")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Threats Detected (24h)", "47", delta="-8 vs yesterday")
    with col2:
        st.metric("Auto-Remediated", "42", delta="+5")
    with col3:
        st.metric("Risk Score", "23/100", delta="-12", delta_color="inverse")
    with col4:
        st.metric("Avg Response Time", "1.2s", delta="-0.3s")
    
    st.markdown("---")
    
    # Security sub-tabs
    sec_tab1, sec_tab2, sec_tab3, sec_tab4 = st.tabs([
        "🔍 Active Threats",
        "🛠️ Remediation Queue",
        "📊 Security Dashboard",
        "🤖 Claude Reasoning"
    ])
    
    with sec_tab1:
        st.subheader("🔍 Active Security Threats")
        
        # Generate threat data
        threat_types = ['Exposed S3 Bucket', 'Weak IAM Policy', 'Unpatched EC2', 
                       'Compromised Credentials', 'Suspicious API Activity', 'Port Scan Detected']
        severities = ['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low']
        
        threats_data = []
        for i in range(12):
            threats_data.append({
                'Timestamp': (datetime.now() - timedelta(minutes=random.randint(5, 1440))).strftime('%Y-%m-%d %H:%M'),
                'Threat_Type': random.choice(threat_types),
                'Severity': random.choice(severities),
                'Account': f'prod-{random.choice(["web", "api", "ml", "data"])}-{random.randint(1, 640):03d}',
                'Resource': f'arn:aws:ec2:us-east-1:{random.randint(100000000000, 999999999999)}:instance/i-{random.randint(10000000, 99999999)}',
                'Status': random.choice(['🔍 Detected', '🔄 Remediating', '⏳ Pending Approval', '✅ Resolved']),
                'Risk_Score': random.randint(3, 10)
            })
        
        threats_df = pd.DataFrame(threats_data).sort_values('Timestamp', ascending=False)
        st.dataframe(threats_df, use_container_width=True, hide_index=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🛡️ Auto-Remediate All Critical", key="sec_auto_remediate", type="primary"):
                st.success("✅ 5 critical threats queued for auto-remediation")
        with col2:
            if st.button("📊 Generate Security Report", key="sec_report"):
                st.info("📄 Security report generated and sent to security@company.com")
        with col3:
            if st.button("🔔 Escalate to SOC", key="sec_escalate"):
                st.warning("⚠️ High-priority threats escalated to Security Operations Center")
    
    with sec_tab2:
        st.subheader("🛠️ Remediation Queue")
        
        remediation_data = []
        actions = ['Auto-patch EC2', 'Revoke IAM Keys', 'Encrypt S3 Bucket', 'Isolate Instance', 'Update Security Group']
        for i in range(8):
            remediation_data.append({
                'Action_ID': f'REM-{random.randint(10000, 99999)}',
                'Action': random.choice(actions),
                'Target': f'prod-{random.choice(["web", "api"])}-{random.randint(1, 100):03d}',
                'Priority': random.choice(['🔴 Critical', '🟠 High', '🟡 Medium']),
                'ETA': f'{random.randint(1, 15)} min',
                'Status': random.choice(['⏳ Queued', '🔄 In Progress', '✅ Completed']),
                'Approved_By': random.choice(['Auto-approved', 'Claude AI', 'Security Team'])
            })
        
        st.dataframe(pd.DataFrame(remediation_data), use_container_width=True, hide_index=True)
    
    with sec_tab3:
        st.subheader("📊 Security Overview Dashboard")
        
        # Security metrics over time
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        threats_detected = [random.randint(20, 80) for _ in dates]
        threats_remediated = [int(t * random.uniform(0.85, 0.95)) for t in threats_detected]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=threats_detected, name='Detected',
                                line=dict(color='#FF6B6B', width=3)))
        fig.add_trace(go.Scatter(x=dates, y=threats_remediated, name='Remediated',
                                line=dict(color='#00FF88', width=3), fill='tonexty'))
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title='Security Threats: Detection vs Remediation (30 days)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Threat breakdown by type
        col1, col2 = st.columns(2)
        with col1:
            threat_counts = {'S3 Exposure': 23, 'IAM Issues': 45, 'Unpatched': 18, 'Credentials': 12, 'Network': 8}
            fig_pie = go.Figure(data=[go.Pie(labels=list(threat_counts.keys()), 
                                            values=list(threat_counts.values()),
                                            hole=.4)])
            fig_pie.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                                 title='Threats by Category')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### Security Health by Service")
            services = ['EC2', 'S3', 'IAM', 'RDS', 'Lambda', 'EKS']
            for svc in services:
                score = random.randint(85, 100)
                color = '#00FF88' if score >= 95 else '#FFD700' if score >= 85 else '#FF4444'
                st.markdown(f"**{svc}**: {score}% secure")
                st.progress(score/100)
    
    with sec_tab4:
        st.subheader("🤖 Claude AI Security Reasoning")
        
        with st.expander("📋 Example: Exposed S3 Bucket Detection & Remediation", expanded=True):
            st.markdown("""
### Scenario: Exposed S3 Bucket Detected

**Input Context:**
- Bucket: `prod-data-analytics-2024`
- Public read access enabled
- Contains 2,847 objects (127 GB)
- No encryption at rest
- Last accessed: 3 hours ago from unknown IP (45.33.32.156)

**Claude Analysis:**
```
SECURITY ASSESSMENT:
├── Data Classification: PII (Personal Identifiable Information detected)
├── Exposure Level: CRITICAL - Internet accessible
├── Affected Records: ~47,000 customer records
├── Compliance Impact: GDPR, PCI DSS violations likely
├── Active Threat: Unknown IP access suggests potential data exfiltration
└── Risk Score: 9/10 (Critical)
```

**Decision Process:**
1. ✅ Verified bucket contains PII through object sampling (names, emails, addresses)
2. ✅ Confirmed public access is NOT required (checked IAM policies, no legitimate use case)
3. ✅ Checked for active connections (none currently active)
4. ✅ Evaluated blast radius: Affects 47,000 customer records across 3 business units
5. ✅ Assessed regulatory impact: GDPR Article 33 notification may be required

**Decision:** `IMMEDIATE REMEDIATION REQUIRED`

**Actions Taken:**
1. 🔒 Removed public access (BlockPublicAcls enabled)
2. 🔐 Enabled default encryption (AES-256)
3. 📝 Enabled access logging to security-logs bucket
4. 🚨 Created Security Hub finding (CRITICAL)
5. 📧 Notified security team via SNS
6. 📊 Initiated incident response protocol
7. 🔍 Queued review of 3 similar buckets found

**Confidence Score:** 99%
**Execution Time:** 1.2s
""")
        
        with st.expander("📋 Example: Compromised IAM Credentials", expanded=False):
            st.markdown("""
### Scenario: Suspicious IAM Activity Detected

**Input Context:**
- User: `svc-deployment-prod`
- 847 API calls in last hour (normal: 50-100)
- New regions accessed: ap-southeast-1, eu-west-2 (never before)
- Actions: ListBuckets, GetObject (unusual for this service account)
- Source IP: 185.234.72.x (known VPN exit node)

**Claude Analysis:**
```
CREDENTIAL COMPROMISE INDICATORS:
├── API Volume: 8.5x normal (ANOMALY)
├── Geographic: 2 new regions (ANOMALY)
├── Behavior: Read-heavy pattern inconsistent with service purpose
├── IP Reputation: Associated with previous breaches
└── Risk Score: 8/10 (High)
```

**Decision:** `CREDENTIALS COMPROMISED - REVOKE IMMEDIATELY`

**Actions Taken:**
1. 🔑 Revoked all active sessions for user
2. 🚫 Deactivated access keys
3. 📝 Generated new credentials (stored in Secrets Manager)
4. 🔔 Alerted DevOps team for key rotation
5. 📊 Logged all affected resources for audit

**Confidence Score:** 97%
""")

# ==================== TAB 5: DEVOPS AGENT ====================
with tab5:
    st.header("⚙️ DevOps Agent")
    st.markdown("**CI/CD pipeline optimization and security scanning automation**")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pipelines Monitored", "23", delta="+2")
    with col2:
        st.metric("Optimizations (7d)", "47", delta="+12")
    with col3:
        st.metric("Avg Build Time", "6m 42s", delta="-3m 15s")
    with col4:
        st.metric("Security Scans", "156", delta="+23")
    
    st.markdown("---")
    
    # DevOps sub-tabs
    devops_tab1, devops_tab2, devops_tab3, devops_tab4 = st.tabs([
        "🔄 Pipeline Status",
        "⚡ Optimizations",
        "🔒 Security Scans",
        "🤖 Claude Reasoning"
    ])
    
    with devops_tab1:
        st.subheader("🔄 CI/CD Pipeline Status")
        
        repos = ['frontend-app', 'backend-api', 'ml-models', 'data-pipeline', 
                'mobile-app', 'infrastructure', 'auth-service', 'payment-service']
        
        pipeline_data = []
        for repo in repos:
            pipeline_data.append({
                'Repository': repo,
                'Branch': random.choice(['main', 'develop', 'release/v2.1']),
                'Status': random.choice(['✅ Success', '🔄 Running', '⚠️ Warning', '❌ Failed']),
                'Build_Time': f'{random.randint(3, 15)}m {random.randint(10, 59)}s',
                'Tests': f'{random.randint(90, 100)}% passed',
                'Coverage': f'{random.randint(75, 95)}%',
                'Security': random.choice(['✅ Clean', '⚠️ 2 Medium', '🔴 1 Critical']),
                'Last_Deploy': (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime('%Y-%m-%d %H:%M')
            })
        
        st.dataframe(pd.DataFrame(pipeline_data), use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⚡ Optimize All Pipelines", key="devops_optimize", type="primary"):
                st.success("✅ 5 pipelines optimized! Average build time reduced by 45%")
        with col2:
            if st.button("🔒 Run Security Scans", key="devops_scan"):
                st.info("🔍 Security scans initiated on all repositories")
        with col3:
            if st.button("📊 Performance Report", key="devops_report"):
                st.info("📄 Pipeline performance report generated")
    
    with devops_tab2:
        st.subheader("⚡ Optimization Recommendations")
        
        optimizations = [
            {"Pipeline": "backend-api", "Recommendation": "Enable parallel testing (4 runners)",
             "Impact": "-65% build time", "Effort": "Low", "Status": "⏳ Pending"},
            {"Pipeline": "frontend-app", "Recommendation": "Implement Docker layer caching",
             "Impact": "-40% build time", "Effort": "Low", "Status": "✅ Implemented"},
            {"Pipeline": "ml-models", "Recommendation": "Use spot instances for training",
             "Impact": "-70% cost", "Effort": "Medium", "Status": "🔄 In Progress"},
            {"Pipeline": "data-pipeline", "Recommendation": "Optimize dependency resolution",
             "Impact": "-30% build time", "Effort": "Low", "Status": "⏳ Pending"},
        ]
        
        for opt in optimizations:
            with st.expander(f"📋 {opt['Pipeline']}: {opt['Recommendation']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Expected Impact", opt['Impact'])
                with col2:
                    st.metric("Effort", opt['Effort'])
                with col3:
                    st.write(f"**Status:** {opt['Status']}")
                
                if opt['Status'] == '⏳ Pending':
                    if st.button(f"✅ Implement", key=f"impl_{opt['Pipeline']}"):
                        st.success(f"Optimization implemented for {opt['Pipeline']}")
    
    with devops_tab3:
        st.subheader("🔒 Security Scan Results")
        
        scan_results = []
        vuln_types = ['Dependency CVE', 'Hardcoded Secret', 'Insecure Config', 'Outdated Package']
        for i in range(10):
            scan_results.append({
                'Repository': random.choice(repos),
                'Scanner': random.choice(['KICS', 'GHAS', 'Snyk', 'Trivy']),
                'Finding': random.choice(vuln_types),
                'Severity': random.choice(['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low']),
                'CVE': f'CVE-2024-{random.randint(10000, 99999)}' if random.random() > 0.5 else 'N/A',
                'Status': random.choice(['⏳ Open', '🔄 In Progress', '✅ Fixed']),
                'Age': f'{random.randint(1, 30)} days'
            })
        
        st.dataframe(pd.DataFrame(scan_results), use_container_width=True, hide_index=True)
    
    with devops_tab4:
        st.subheader("🤖 Claude AI DevOps Reasoning")
        
        with st.expander("📋 Example: Pipeline Optimization Analysis", expanded=True):
            st.markdown("""
### Scenario: Backend API Pipeline Optimization

**Input Context:**
- Repository: backend-api
- Average build time: 14m 32s
- Test execution: 9m 15s (63% of total)
- Docker build: 3m 10s
- Deployment: 2m 7s

**Claude Analysis:**
```
PERFORMANCE BOTTLENECKS IDENTIFIED:
├── Test Suite: Sequential execution (should be parallel)
│   └── 847 tests, all running sequentially
├── Docker Build: No layer caching
│   └── Rebuilding node_modules on every change
├── Dependency Install: Fresh install each build
│   └── 2m 30s for npm install
└── Test Strategy: Full suite on every commit
    └── Should use selective testing based on changed files
```

**Optimization Plan:**
1. **Enable Parallel Testing** (4 runners)
   - Current: 9m 15s → Expected: 2m 45s
   - Implementation: Update jest.config.js, add `--maxWorkers=4`

2. **Docker Layer Caching**
   - Current: 3m 10s → Expected: 45s
   - Implementation: Reorder Dockerfile, cache node_modules layer

3. **Intelligent Test Selection**
   - Only run tests affected by changed files
   - Full suite on PR merge only

4. **Dependency Caching**
   - Cache npm packages between builds
   - Expected savings: 2m 15s

**Expected Results:**
- Build time: 14m 32s → **5m 05s** (-65%)
- Cost savings: $2,400/month (fewer build minutes)
- Developer productivity: +40% faster feedback

**Confidence Score:** 94%
""")

# ==================== TAB 6: DATABASE AGENT ====================
with tab6:
    st.header("🗄️ Database Agent")
    st.markdown("**Intelligent database access management and performance optimization**")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Access Requests (24h)", "32", delta="+7")
    with col2:
        st.metric("Auto-Approved", "28", delta="+5")
    with col3:
        st.metric("Active Sessions", "18", delta="+3")
    with col4:
        st.metric("Avg Approval Time", "1.5s", delta="-0.4s")
    
    st.markdown("---")
    
    # Database sub-tabs
    db_tab1, db_tab2, db_tab3, db_tab4 = st.tabs([
        "📋 Access Requests",
        "📊 Performance",
        "🔐 Active Sessions",
        "🤖 Claude Reasoning"
    ])
    
    with db_tab1:
        st.subheader("📋 Database Access Request Queue")
        
        databases = ['prod-postgres-01', 'prod-mysql-02', 'prod-aurora-03', 'prod-dynamodb-main']
        users = ['john.doe@company.com', 'jane.smith@company.com', 'bob.wilson@company.com', 
                'alice.chen@company.com', 'david.kumar@company.com']
        
        requests = []
        for i in range(10):
            requests.append({
                'Request_ID': f'DBR-{random.randint(10000, 99999)}',
                'User': random.choice(users),
                'Database': random.choice(databases),
                'Access_Type': random.choice(['Read-Only', 'Read-Write', 'Admin']),
                'Duration': random.choice(['1 hour', '4 hours', '1 day', '1 week']),
                'Justification': random.choice([
                    'Production bug investigation',
                    'Q4 revenue analysis',
                    'Schema migration',
                    'Performance tuning',
                    'Audit compliance check'
                ]),
                'Risk_Score': random.randint(2, 8),
                'Status': random.choice(['⏳ Pending', '✅ Approved', '❌ Denied', '🔄 Active'])
            })
        
        requests_df = pd.DataFrame(requests)
        st.dataframe(requests_df, use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Auto-Approve Low Risk", key="db_approve", type="primary"):
                st.success("✅ 4 low-risk requests approved with time-bound credentials")
        with col2:
            if st.button("🔍 Audit Active Sessions", key="db_audit"):
                st.info("📊 Session audit completed - all sessions compliant")
        with col3:
            if st.button("⚙️ Revoke Expired", key="db_revoke"):
                st.warning("⚠️ 3 expired sessions revoked")
    
    with db_tab2:
        st.subheader("📊 Database Performance Overview")
        
        # Performance metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Query performance over time
            hours = [f'{i}:00' for i in range(24)]
            query_times = [random.uniform(10, 100) for _ in hours]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hours, y=query_times, name='Avg Query Time (ms)',
                                    line=dict(color='#00D9FF', width=3), fill='tozeroy'))
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                             title='Average Query Time (24h)', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Connection pool usage
            connections = {'prod-postgres-01': 78, 'prod-mysql-02': 45, 
                          'prod-aurora-03': 92, 'prod-dynamodb-main': 34}
            
            fig = go.Figure(data=[go.Bar(x=list(connections.keys()), 
                                        y=list(connections.values()),
                                        marker_color='#00FF88')])
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                             title='Connection Pool Usage (%)', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Optimization recommendations
        st.subheader("💡 AI-Recommended Optimizations")
        optimizations = [
            {"Database": "prod-postgres-01", "Recommendation": "Add index on users.created_at", "Impact": "-40% query time"},
            {"Database": "prod-aurora-03", "Recommendation": "Scale read replicas to 3", "Impact": "-25% latency"},
            {"Database": "prod-mysql-02", "Recommendation": "Enable query caching", "Impact": "-30% load"},
        ]
        
        for opt in optimizations:
            st.info(f"**{opt['Database']}**: {opt['Recommendation']} (Expected: {opt['Impact']})")
    
    with db_tab3:
        st.subheader("🔐 Active Database Sessions")
        
        sessions = []
        for i in range(8):
            sessions.append({
                'Session_ID': f'SES-{random.randint(10000, 99999)}',
                'User': random.choice(users),
                'Database': random.choice(databases),
                'Started': (datetime.now() - timedelta(minutes=random.randint(5, 240))).strftime('%H:%M'),
                'Queries': random.randint(10, 500),
                'Data_Read': f'{random.randint(1, 100)} MB',
                'Expires_In': f'{random.randint(10, 180)} min',
                'Status': '🟢 Active'
            })
        
        st.dataframe(pd.DataFrame(sessions), use_container_width=True, hide_index=True)
    
    with db_tab4:
        st.subheader("🤖 Claude AI Database Access Reasoning")
        
        with st.expander("📋 Example: Access Request Evaluation", expanded=True):
            st.markdown("""
### Scenario: Database Access Request Evaluation

**Request Details:**
- User: john.doe@company.com (Senior Data Analyst)
- Database: prod-postgres-01 (customer analytics)
- Access Type: Read-Only
- Duration: 4 hours
- Justification: "Q4 revenue analysis for board presentation"

**Claude Analysis:**
```
ACCESS RISK EVALUATION:
├── User Profile
│   ├── Role: Senior Data Analyst (authorized for analytics data)
│   ├── History: 15 previous requests, 100% compliant
│   ├── Last Access: 3 days ago (normal pattern)
│   └── Security Training: Current (completed 2024-10-15)
│
├── Database Sensitivity
│   ├── Classification: Medium (aggregated data)
│   ├── PII Present: No (anonymized)
│   ├── Financial Data: Yes (revenue figures)
│   └── Compliance: SOC 2 applicable
│
├── Request Context
│   ├── Business Justification: Valid (board meeting in 6 hours)
│   ├── Time Sensitivity: High
│   ├── Alternative Options: Pre-built dashboard insufficient
│   └── Access Scope: Read-only (minimal risk)
│
└── Risk Score: 3/10 (Low)
```

**Decision:** `GRANT ACCESS - Time-bound with monitoring`

**Actions Taken:**
1. 🔑 Generated temporary IAM credentials (4h TTL)
2. 📊 Granted read-only access to analytics schema only
3. 📝 Enabled query logging for audit trail
4. ⏰ Scheduled automatic revocation at 18:00
5. 📧 Notified user of access grant via Slack
6. 🔔 Set up alert for unusual query patterns

**Security Controls Applied:**
- Access limited to `analytics` schema only
- No access to `users` or `payments` tables
- Query result set limited to 10,000 rows
- Export disabled (results stay in-platform)

**Confidence Score:** 96%
**Execution Time:** 1.5s
""")

# ==================== TAB 8: POLICY ENGINE ====================
with tab8:
    st.header("📋 Adaptive Policy Engine")
    st.markdown("**AI-powered policy generation and effectiveness tracking**")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Policies", "87", delta="+5")
    with col2:
        st.metric("AI-Generated", "34", delta="+8")
    with col3:
        st.metric("Effectiveness", "96.4%", delta="+1.2%")
    with col4:
        st.metric("Violations Prevented", "1,247", delta="+89")
    
    st.markdown("---")
    
    # Policy sub-tabs
    policy_tab1, policy_tab2, policy_tab3, policy_tab4 = st.tabs([
        "💡 Recommendations",
        "📋 Active Policies",
        "📊 Effectiveness",
        "🤖 Claude Reasoning"
    ])
    
    with policy_tab1:
        st.subheader("💡 AI-Generated Policy Recommendations")
        
        recommendations = [
            {
                "name": "S3 Bucket Encryption Enforcement",
                "description": "Prevent creation of unencrypted S3 buckets",
                "rationale": "23 unencrypted buckets created in past 30 days",
                "type": "Preventive (SCP)",
                "impact": "Medium",
                "effectiveness": "94%"
            },
            {
                "name": "IAM Password Rotation Policy",
                "description": "Enforce 90-day password rotation for all users",
                "rationale": "31% of users have passwords older than 180 days",
                "type": "Detective (Config Rule)",
                "impact": "Low",
                "effectiveness": "89%"
            },
            {
                "name": "EC2 Instance Tagging Requirement",
                "description": "Require cost-center and owner tags on all EC2 instances",
                "rationale": "156 untagged instances causing cost allocation issues",
                "type": "Preventive (SCP)",
                "impact": "Low",
                "effectiveness": "97%"
            },
            {
                "name": "Public RDS Prevention",
                "description": "Block creation of publicly accessible RDS instances",
                "rationale": "2 public RDS instances detected this month",
                "type": "Preventive (SCP)",
                "impact": "Critical",
                "effectiveness": "99%"
            }
        ]
        
        for i, policy in enumerate(recommendations):
            with st.expander(f"📜 {policy['name']}", expanded=(i==0)):
                st.markdown(f"**Description:** {policy['description']}")
                st.markdown(f"**Rationale:** {policy['rationale']}")
                st.markdown(f"**Type:** {policy['type']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Business Impact", policy['impact'])
                with col2:
                    st.metric("Expected Effectiveness", policy['effectiveness'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Deploy Policy", key=f"deploy_{i}", type="primary"):
                        st.success(f"✅ Policy '{policy['name']}' deployed to production OUs")
                with col2:
                    if st.button("🧪 A/B Test", key=f"test_{i}"):
                        st.info("🧪 A/B test initiated - will run for 7 days")
                with col3:
                    if st.button("📝 Review", key=f"review_{i}"):
                        st.info("📋 Policy sent to security team for review")
    
    with policy_tab2:
        st.subheader("📋 Active Policies Catalog")
        
        policies = []
        policy_types = ['SCP', 'Config Rule', 'OPA', 'GuardDuty Rule']
        for i in range(15):
            policies.append({
                'Policy_ID': f'POL-{random.randint(1000, 9999)}',
                'Name': random.choice([
                    'Require S3 Encryption', 'Block Public Access', 'Enforce MFA',
                    'Restrict Regions', 'Require Tagging', 'Prevent Root Usage'
                ]),
                'Type': random.choice(policy_types),
                'Scope': random.choice(['All Accounts', 'Production', 'Development', 'Sandbox']),
                'Violations_Blocked': random.randint(50, 500),
                'Effectiveness': f'{random.randint(85, 99)}%',
                'Status': random.choice(['✅ Active', '🔄 Testing', '⏸️ Paused'])
            })
        
        st.dataframe(pd.DataFrame(policies), use_container_width=True, hide_index=True)
    
    with policy_tab3:
        st.subheader("📊 Policy Effectiveness Dashboard")
        
        # Effectiveness over time
        weeks = [f'Week {i}' for i in range(1, 13)]
        effectiveness = [random.uniform(85, 99) for _ in weeks]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weeks, y=effectiveness, mode='lines+markers',
                                name='Policy Effectiveness %',
                                line=dict(color='#00FF88', width=3)))
        fig.add_hline(y=95, line_dash="dash", line_color="#FFD700", 
                     annotation_text="Target: 95%")
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                         title='Overall Policy Effectiveness (12 weeks)', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Policy performance breakdown
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top Performing Policies")
            top_policies = [
                ("Require S3 Encryption", "99%"),
                ("Block Public Access", "98%"),
                ("Enforce MFA", "97%"),
                ("Restrict Regions", "96%")
            ]
            for name, eff in top_policies:
                st.success(f"✅ {name}: {eff}")
        
        with col2:
            st.markdown("#### Policies Needing Attention")
            attention_policies = [
                ("EC2 Tagging", "78%"),
                ("Cost Allocation Tags", "72%")
            ]
            for name, eff in attention_policies:
                st.warning(f"⚠️ {name}: {eff}")
    
    with policy_tab4:
        st.subheader("🤖 Claude AI Policy Generation Reasoning")
        
        with st.expander("📋 Example: Policy Generation from Violation Patterns", expanded=True):
            st.markdown("""
### Scenario: Recurring Violation Pattern Detected

**Input Context:**
- Violation Type: Unencrypted S3 buckets
- Occurrences: 23 instances in past 30 days
- Affected Accounts: 12 different accounts
- Pattern: New buckets created without encryption enabled

**Claude Analysis:**
```
VIOLATION PATTERN ANALYSIS:
├── Trend: Increasing (+15% vs previous month)
├── Root Cause: No preventive control exists
│   └── Current policy: Detective only (Config rule)
├── Developer Awareness: 67% unaware of requirement
├── Manual Remediation: Taking avg 2-3 days per incident
└── Compliance Risk: PCI DSS, HIPAA violations possible
```

**Policy Generation:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedS3",
      "Effect": "Deny",
      "Action": "s3:CreateBucket",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

**Decision:** `GENERATE PREVENTIVE POLICY`

**Implementation Plan:**
1. 📋 Create SCP to deny unencrypted bucket creation
2. 🏷️ Add exception for dev/sandbox accounts (tag-based)
3. 🚀 Deploy to Production and Staging OUs
4. 📝 Update developer documentation
5. 📧 Send notification to all affected teams
6. 📊 Monitor for 7 days before full enforcement

**Expected Impact:**
- Violations prevented: 95%+
- Manual remediation: -90%
- Compliance risk: Eliminated

**Confidence Score:** 98%
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 24px; background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius: 12px; border: 1px solid #334155; margin-top: 20px;'>
    <div style='font-size: 1.3rem; font-weight: 700; color: #10B981; margin-bottom: 8px;'>🛡️ TechGuard Rails Platform</div>
    <div style='color: #CBD5E1; font-size: 0.95rem;'>Enterprise Cloud Operations | AWS Bedrock + Claude 4 | 640+ AWS Accounts | 6 AI Agents</div>
    <div style='color: #64748B; font-size: 0.85rem; margin-top: 8px;'>Version 2.0 | All Systems Operational | Transform Phase</div>
</div>
""", unsafe_allow_html=True)