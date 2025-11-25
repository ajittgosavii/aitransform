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
    /* ============ COMPLETELY FIX WHITE HEADER BAR ============ */
    /* Target EVERYTHING at the top */
    header, .stApp > header, header[data-testid="stHeader"] {
        background-color: #0F172A !important;
        background: #0F172A !important;
    }
    
    /* The main culprit - Streamlit's top bar */
    [data-testid="stHeader"] {
        background-color: #0F172A !important;
        background: #0F172A !important;
        border-bottom: none !important;
    }
    
    /* Toolbar area */
    [data-testid="stToolbar"] {
        background-color: #0F172A !important;
        background: #0F172A !important;
    }
    
    /* Deploy button area */
    .stDeployButton {
        background-color: #0F172A !important;
    }
    
    /* App view container header */
    [data-testid="stAppViewContainer"] > header {
        background-color: #0F172A !important;
        background: #0F172A !important;
    }
    
    /* Block container at top */
    .stApp [data-testid="stAppViewBlockContainer"] {
        background-color: #0F172A !important;
    }
    
    /* Any remaining white divs at top */
    .stApp > div:first-child {
        background-color: #0F172A !important;
    }
    
    /* Status widget (running indicator) */
    [data-testid="stStatusWidget"] {
        background-color: #0F172A !important;
    }
    
    /* Decoration - hamburger menu area */
    [data-testid="stDecoration"] {
        background-color: #0F172A !important;
        background: #0F172A !important;
        display: none !important;
    }
    
    /* The main wrapper */
    .main .block-container {
        background-color: #0F172A !important;
    }
    
    /* Root level */
    #root > div:first-child {
        background-color: #0F172A !important;
    }
    
    /* iframe parent if embedded */
    .stApp iframe {
        background-color: #0F172A !important;
    }
    
    /* ============ FORCE ALL TEXT WHITE ============ */
    .stApp, .main {
        background-color: #0F172A !important;
    }
    
    /* AGGRESSIVE: ALL TEXT WHITE - EXCEPT DROPDOWNS */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stMarkdown li, .element-container, .stText {
        color: #FFFFFF !important;
        opacity: 1 !important;
    }
    
    /* Body text - exclude popover/dropdown elements */
    .stApp p:not([data-baseweb] p):not([role="listbox"] p),
    .stApp span:not([data-baseweb] span):not([role="listbox"] span):not([role="option"] span),
    .stApp li:not([data-baseweb] li):not([role="listbox"] li):not([role="option"]) {
        color: #FFFFFF !important;
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
    
    /* ============ SIDEBAR - FORCE VISIBLE ============ */
    /* Ensure sidebar is visible and expanded */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%) !important;
        border-right: 3px solid #10B981 !important;
        min-width: 320px !important;
        width: 320px !important;
    }
    
    /* Sidebar collapse button - make it visible */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        color: #10B981 !important;
        background: #1E293B !important;
        border: 2px solid #10B981 !important;
    }
    
    /* Sidebar expand button when collapsed */
    button[kind="header"] {
        background: #10B981 !important;
        color: #FFFFFF !important;
    }
    
    /* Force sidebar to be visible */
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* ALL sidebar text white */
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Sidebar headers */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #10B981 !important;
        font-weight: 700 !important;
    }
    
    /* SIDEBAR RADIO BUTTONS - Force visible */
    section[data-testid="stSidebar"] .stRadio {
        background-color: rgba(30, 41, 59, 0.8) !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] .stRadio p {
        color: #FFFFFF !important;
        font-size: 14px !important;
    }
    section[data-testid="stSidebar"] .stRadio span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio div {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar metrics */
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #10B981 !important;
        font-size: 1.5rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #FFFFFF !important;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar info/success/warning boxes */
    section[data-testid="stSidebar"] .stAlert {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid #10B981 !important;
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
    
    /* ============ DROPDOWN MENU - CRITICAL FIX ============ */
    /* Popover container */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }
    
    /* Menu container */
    [data-baseweb="menu"] {
        background-color: #FFFFFF !important;
    }
    
    /* All list items in menu - BLACK TEXT */
    [data-baseweb="menu"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    [data-baseweb="menu"] li * {
        color: #000000 !important;
    }
    [data-baseweb="menu"] li span {
        color: #000000 !important;
    }
    [data-baseweb="menu"] li div {
        color: #000000 !important;
    }
    [data-baseweb="menu"] li p {
        color: #000000 !important;
    }
    
    /* Hover state */
    [data-baseweb="menu"] li:hover {
        background-color: #E2E8F0 !important;
        color: #000000 !important;
    }
    [data-baseweb="menu"] li:hover * {
        color: #000000 !important;
    }
    
    /* Selected/highlighted item */
    [data-baseweb="menu"] [aria-selected="true"] {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
    }
    [data-baseweb="menu"] [aria-selected="true"] * {
        color: #FFFFFF !important;
    }
    
    /* Listbox specific (another Streamlit dropdown type) */
    [role="listbox"] {
        background-color: #FFFFFF !important;
    }
    [role="listbox"] [role="option"] {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    [role="listbox"] [role="option"] * {
        color: #000000 !important;
    }
    [role="listbox"] [role="option"]:hover {
        background-color: #E2E8F0 !important;
    }
    [role="listbox"] [aria-selected="true"] {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
    }
    
    /* Option container */
    [data-baseweb="select"] [role="option"] {
        color: #000000 !important;
    }
    [data-baseweb="select"] [role="option"] * {
        color: #000000 !important;
    }
    
    /* Dropdown list */
    ul[role="listbox"] li {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    ul[role="listbox"] li * {
        color: #000000 !important;
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
    
    /* ============ FINAL OVERRIDE - DROPDOWN ITEMS BLACK TEXT ============ */
    /* These are the nuclear options to force dropdown text black */
    div[data-baseweb="popover"] * {
        color: #000000 !important;
    }
    div[data-baseweb="popover"] li {
        color: #000000 !important;
        background: #FFFFFF !important;
    }
    div[data-baseweb="popover"] [role="option"] {
        color: #000000 !important;
        background: #FFFFFF !important;
    }
    div[data-baseweb="popover"] [role="option"] span {
        color: #000000 !important;
    }
    div[data-baseweb="popover"] [role="option"] div {
        color: #000000 !important;
    }
    
    /* Target the floating dropdown specifically */
    body > div[data-baseweb="popover"] {
        background: #FFFFFF !important;
    }
    body > div[data-baseweb="popover"] * {
        color: #000000 !important;
    }
    body > div[data-baseweb="popover"] [aria-selected="true"],
    body > div[data-baseweb="popover"] [aria-selected="true"] * {
        background: #10B981 !important;
        color: #FFFFFF !important;
    }
    
    /* SUPER AGGRESSIVE - Target ANY dropdown/listbox anywhere in the document */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [data-baseweb="list"],
    [data-baseweb="listbox"],
    [role="listbox"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [data-baseweb="list"] li,
    [data-baseweb="listbox"] li,
    [role="listbox"] li,
    [role="option"] {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    [data-baseweb="popover"] li span,
    [data-baseweb="popover"] li div,
    [data-baseweb="popover"] li p,
    [data-baseweb="menu"] li span,
    [data-baseweb="menu"] li div,
    [role="option"] span,
    [role="option"] div,
    [role="option"] p {
        color: #000000 !important;
    }
    
    /* Hover states */
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover {
        background-color: #E2E8F0 !important;
        color: #000000 !important;
    }
    
    /* Selected states */
    [aria-selected="true"] {
        background-color: #10B981 !important;
    }
    [aria-selected="true"],
    [aria-selected="true"] span,
    [aria-selected="true"] div {
        color: #FFFFFF !important;
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

# Sidebar with enhanced professional design
with st.sidebar:
    # Header with icon
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h2 style='color: #10B981; margin: 0;'>🛡️ TechGuard Rails</h2>
        <p style='color: #94A3B8; font-size: 12px; margin: 5px 0 0 0;'>Control Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # MODE TOGGLE - Demo vs Live AWS - PROMINENT
    st.markdown("#### 🎮 Data Source")
    
    # Create a more visible mode selector
    st.markdown("""
    <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; border-radius: 8px; padding: 10px; margin-bottom: 10px;'>
        <p style='color: #10B981; font-size: 12px; margin: 0; text-align: center;'>Select Mode Below</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Show current mode status prominently
    if st.session_state.mode == 'demo':
        st.markdown("""
        <div style='background: #3B82F6; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 10px 0;'>
            <strong>📊 DEMO MODE ACTIVE</strong><br/>
            <small>Using simulated data</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show AWS connection status if in live mode
        aws_session = get_aws_session()
        if aws_session:
            st.markdown("""
            <div style='background: #22C55E; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 10px 0;'>
                <strong>✅ AWS CONNECTED</strong><br/>
                <small>Live data active</small>
            </div>
            """, unsafe_allow_html=True)
            try:
                sts = aws_session.client('sts')
                identity = sts.get_caller_identity()
                st.caption(f"🔑 Account: {identity['Account']}")
            except:
                pass
        else:
            st.markdown("""
            <div style='background: #EF4444; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 10px 0;'>
                <strong>❌ AWS NOT CONNECTED</strong><br/>
                <small>Check credentials</small>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("📖 Connection Guide"):
                st.info("""
                **To connect AWS:**
                1. Add credentials to Streamlit secrets
                2. Use IAM role (if on AWS)
                3. Configure ~/.aws/credentials
                """)
    
    st.markdown("---")
    
    # System Status
    st.markdown("#### ⚡ System Status")
    st.markdown("""
    <div style='background: rgba(34, 197, 94, 0.2); border: 1px solid #22C55E; border-radius: 8px; padding: 10px; text-align: center;'>
        <span style='color: #22C55E; font-weight: 700;'>🟢 All Systems Operational</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Uptime", "99.97%", delta="0.02%")
    with col2:
        st.metric("Agents", "6/6", delta="0")
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("#### 📊 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Accounts", "640", delta="+3")
        st.metric("Monthly", "$2.8M", delta="-$89K")
    with col2:
        st.metric("Savings", f"${st.session_state.cost_savings:,}", delta="+12%")
        st.metric("Actions", st.session_state.actions_executed, delta="+5")
    
    st.markdown("---")
    
    # Demo Controls
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
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <small style='color: #64748B;'>TechGuard Rails v2.0</small><br/>
        <small style='color: #64748B;'>640 AWS Accounts | 6 Agents</small>
    </div>
    """, unsafe_allow_html=True)


# Add visual separation before tabs
st.markdown("<br>", unsafe_allow_html=True)

# ============ MAIN PAGE HEADER WITH MODE TOGGLE ============
header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

with header_col1:
    st.markdown("""
    <div style='padding: 10px 0;'>
        <h2 style='color: #10B981; margin: 0; font-size: 1.8rem;'>🛡️ Tech Guardrails Platform</h2>
        <p style='color: #94A3B8; margin: 5px 0 0 0; font-size: 14px;'>AI-Powered Cloud Operations | 640+ AWS Accounts</p>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # MODE TOGGLE - Always visible on main page
    mode_choice = st.radio(
        "🎮 Data Mode:",
        ["🎬 Demo", "🔴 Live AWS"],
        index=0 if st.session_state.mode == 'demo' else 1,
        horizontal=True,
        key="main_mode_toggle"
    )
    st.session_state.mode = 'demo' if "Demo" in mode_choice else 'live'

with header_col3:
    # Status indicator
    if st.session_state.mode == 'demo':
        st.markdown("""
        <div style='background: #3B82F6; color: white; padding: 12px 16px; border-radius: 8px; text-align: center; margin-top: 10px;'>
            <strong>📊 DEMO MODE</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: #22C55E; color: white; padding: 12px 16px; border-radius: 8px; text-align: center; margin-top: 10px;'>
            <strong>🔴 LIVE AWS</strong>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Main content tabs with better labels
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "📊 Dashboard", 
    "🤖 AI Agents", 
    "🛡️ Security",
    "⚖️ Compliance",
    "⚙️ DevOps",
    "🗄️ Database",
    "💰 FinOps",
    "📋 Policy",
    "📈 Analytics",
    "📋 Audit",
    "🏗️ Account Lifecycle"
])

with tab1:
    # ============ DASHBOARD - KEY METRICS ============
    # (Main header is already shown above tabs)
    
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
            marker_colors=['#10B981', '#22C55E', '#34D399', '#6EE7B7', '#A7F3D0'],
            textinfo='percent',
            textfont=dict(color='#FFFFFF', size=12),
            insidetextfont=dict(color='#FFFFFF'),
            outsidetextfont=dict(color='#FFFFFF')
        )])
        fig_pie.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            showlegend=True,
            legend=dict(
                orientation='h', 
                yanchor='bottom', 
                y=-0.3,
                font=dict(color='#FFFFFF', size=11),
                bgcolor='rgba(0,0,0,0)'
            ),
            font=dict(color='#FFFFFF')
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
        
        for action, time_str in recent_actions:
            st.markdown(f"""
            <div style='background: #1E293B; padding: 10px 12px; border-radius: 6px; margin: 6px 0; border-left: 3px solid #10B981;'>
                <span style='color: #F1F5F9; font-weight: 500;'>{action}</span><br/>
                <small style='color: #64748B;'>{time_str}</small>
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
    
    st.markdown("---")
    
    # ============ TECHGUARD RAILS - POLICY & SECURITY TOOLS ============
    st.markdown("### 🔧 TechGuard Rails - Policy & Security Tools")
    
    st.markdown("""
    <p style='color: #94A3B8; font-size: 14px;'>
    Real-time status of IaC security scanners, policy engines, and guardrails protecting 640+ AWS accounts.
    </p>
    """, unsafe_allow_html=True)
    
    # Tools status in 4 columns
    tools_col1, tools_col2, tools_col3, tools_col4 = st.columns(4)
    
    with tools_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>🔍 KICS</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Keeping IaC Secure</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Scans Today: <span style='color: #10B981; font-weight: 700;'>847</span></div>
                <div style='color: #F1F5F9;'>Issues Found: <span style='color: #F59E0B; font-weight: 700;'>23</span></div>
                <div style='color: #F1F5F9;'>Auto-Fixed: <span style='color: #22C55E; font-weight: 700;'>18</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>🛡️ Checkov</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>IaC Security Scanner</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Policies: <span style='color: #10B981; font-weight: 700;'>2,500+</span></div>
                <div style='color: #F1F5F9;'>Pass Rate: <span style='color: #22C55E; font-weight: 700;'>94.7%</span></div>
                <div style='color: #F1F5F9;'>Blocked PRs: <span style='color: #EF4444; font-weight: 700;'>12</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tools_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>⚖️ OPA/Rego</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Open Policy Agent</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Policies: <span style='color: #10B981; font-weight: 700;'>156</span></div>
                <div style='color: #F1F5F9;'>Decisions/hr: <span style='color: #10B981; font-weight: 700;'>12.4K</span></div>
                <div style='color: #F1F5F9;'>Denials: <span style='color: #EF4444; font-weight: 700;'>847</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>🔒 tfsec</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Terraform Security</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Modules Scanned: <span style='color: #10B981; font-weight: 700;'>234</span></div>
                <div style='color: #F1F5F9;'>Critical: <span style='color: #EF4444; font-weight: 700;'>3</span></div>
                <div style='color: #F1F5F9;'>High: <span style='color: #F59E0B; font-weight: 700;'>12</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tools_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>📋 AWS SCPs</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ENFORCED</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Service Control Policies</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Active SCPs: <span style='color: #10B981; font-weight: 700;'>47</span></div>
                <div style='color: #F1F5F9;'>OUs Protected: <span style='color: #10B981; font-weight: 700;'>12</span></div>
                <div style='color: #F1F5F9;'>Denials (24h): <span style='color: #EF4444; font-weight: 700;'>1,247</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>⚙️ AWS Config</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Config Rules</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Rules Active: <span style='color: #10B981; font-weight: 700;'>89</span></div>
                <div style='color: #F1F5F9;'>Compliant: <span style='color: #22C55E; font-weight: 700;'>97.2%</span></div>
                <div style='color: #F1F5F9;'>Auto-Remediated: <span style='color: #10B981; font-weight: 700;'>156</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tools_col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>🔐 Sentinel</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>HashiCorp Policy as Code</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Policies: <span style='color: #10B981; font-weight: 700;'>67</span></div>
                <div style='color: #F1F5F9;'>TF Runs: <span style='color: #10B981; font-weight: 700;'>1,847</span></div>
                <div style='color: #F1F5F9;'>Blocked: <span style='color: #EF4444; font-weight: 700;'>34</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 4px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                <span style='font-size: 1rem; font-weight: 700; color: #F1F5F9;'>🛡️ GuardDuty</span>
                <span style='background: #22C55E; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700;'>ACTIVE</span>
            </div>
            <div style='color: #94A3B8; font-size: 11px;'>Threat Detection</div>
            <div style='margin-top: 10px; font-size: 12px;'>
                <div style='color: #F1F5F9;'>Findings (24h): <span style='color: #F59E0B; font-weight: 700;'>23</span></div>
                <div style='color: #F1F5F9;'>High Severity: <span style='color: #EF4444; font-weight: 700;'>2</span></div>
                <div style='color: #F1F5F9;'>Auto-Resolved: <span style='color: #22C55E; font-weight: 700;'>18</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ GUARDRAILS ENFORCEMENT SUMMARY ============
    st.markdown("### 🚧 Guardrails Enforcement Summary")
    
    guard_col1, guard_col2, guard_col3 = st.columns(3)
    
    with guard_col1:
        st.markdown("#### IaC Security (Pre-Deploy)")
        iac_tools = [
            ("KICS", "847 scans", "99.2%", "#22C55E"),
            ("Checkov", "1,234 scans", "94.7%", "#22C55E"),
            ("tfsec", "456 scans", "97.8%", "#22C55E"),
            ("Trivy", "789 scans", "96.3%", "#22C55E"),
            ("Snyk IaC", "234 scans", "95.1%", "#22C55E")
        ]
        for tool, scans, rate, color in iac_tools:
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155;'>
                <span style='color: #F1F5F9; font-weight: 600;'>{tool}</span>
                <span style='color: #94A3B8;'>{scans}</span>
                <span style='color: {color}; font-weight: 700;'>{rate}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with guard_col2:
        st.markdown("#### Policy Engines (Runtime)")
        policy_tools = [
            ("OPA/Rego", "12.4K decisions/hr", "Active", "#22C55E"),
            ("AWS SCPs", "47 policies", "Enforced", "#22C55E"),
            ("Sentinel", "67 policies", "Active", "#22C55E"),
            ("Config Rules", "89 rules", "97.2%", "#22C55E"),
            ("CloudFormation Guard", "34 rules", "Active", "#22C55E")
        ]
        for tool, metric, status, color in policy_tools:
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155;'>
                <span style='color: #F1F5F9; font-weight: 600;'>{tool}</span>
                <span style='color: #94A3B8;'>{metric}</span>
                <span style='color: {color}; font-weight: 700;'>{status}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with guard_col3:
        st.markdown("#### Detection & Response")
        detection_tools = [
            ("GuardDuty", "640 accounts", "Active", "#22C55E"),
            ("Security Hub", "23 integrations", "Active", "#22C55E"),
            ("Inspector", "1,247 assessments", "Active", "#22C55E"),
            ("Macie", "PII scanning", "Active", "#22C55E"),
            ("CloudTrail", "All regions", "Enabled", "#22C55E")
        ]
        for tool, metric, status, color in detection_tools:
            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155;'>
                <span style='color: #F1F5F9; font-weight: 600;'>{tool}</span>
                <span style='color: #94A3B8;'>{metric}</span>
                <span style='color: {color}; font-weight: 700;'>{status}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============ POLICY VIOLATIONS BLOCKED TODAY ============
    st.markdown("### 🚫 Policy Violations Blocked Today")
    
    violations_data = pd.DataFrame({
        'Tool': ['OPA', 'SCPs', 'KICS', 'Checkov', 'Sentinel', 'Config Rules', 'tfsec', 'GuardDuty'],
        'Violations_Blocked': [847, 1247, 156, 89, 34, 67, 23, 45],
        'Category': ['Runtime', 'AWS Native', 'IaC Scan', 'IaC Scan', 'TF Policy', 'AWS Native', 'IaC Scan', 'Detection']
    })
    
    fig_violations = go.Figure(data=[
        go.Bar(
            x=violations_data['Tool'],
            y=violations_data['Violations_Blocked'],
            marker_color=['#8B5CF6', '#3B82F6', '#10B981', '#22C55E', '#F59E0B', '#06B6D4', '#34D399', '#EF4444'],
            text=violations_data['Violations_Blocked'],
            textposition='auto',
            textfont=dict(color='#FFFFFF', size=12, family='Arial Black')
        )
    ])
    fig_violations.update_layout(
        title=dict(text="Violations Blocked by Tool (Last 24h)", font=dict(color='#FFFFFF', size=16)),
        template='plotly_dark',
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        xaxis=dict(tickfont=dict(color='#FFFFFF', size=11)),
        yaxis=dict(tickfont=dict(color='#FFFFFF'), title=dict(text='Violations Blocked', font=dict(color='#FFFFFF')))
    )
    st.plotly_chart(fig_violations, use_container_width=True)

with tab2:
    st.header("🤖 AI Agents - Autonomous Decision Making")
    
    st.markdown("""
    This platform uses **6 specialized AI agents** powered by AWS Bedrock and Claude 4 Sonnet for autonomous cloud operations.
    Each agent has domain-specific knowledge, decision-making capabilities, and can execute actions autonomously within defined guardrails.
    """)
    
    st.markdown("---")
    
    # ============ ALL 6 TECHGUARD RAILS AGENTS ============
    st.subheader("🛡️ TechGuard Rails - 6 AI Agents Overview")
    
    # Agent selector - NOW WITH ALL 6 TECHGUARD RAILS AGENTS
    agent_choice = st.selectbox(
        "Select Agent to Explore:",
        ["🛡️ Security Agent", "⚖️ Compliance Agent", "⚙️ DevOps Agent", 
         "🗄️ Database Agent", "💰 FinOps Agent", "📋 Policy Engine"]
    )
    
    st.markdown("---")
    
    # Display agent details based on selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Agent Configuration")
        
        if "Security" in agent_choice:
            st.code("""
Agent: Security Agent
Runtime: Lambda Python 3.12
Memory: 1024MB
Timeout: 5 minutes
Trigger: EventBridge (real-time) + CloudTrail
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.2 (deterministic)
Tools: GuardDuty API, Security Hub, IAM API,
       S3 API, Config API, Inspector API
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Block public S3 buckets")
            st.success("✅ Revoke compromised credentials")
            st.success("✅ Isolate compromised instances")
            st.success("✅ Auto-patch critical vulnerabilities")
            st.warning("⚠️ Security group changes (requires approval)")
            
        elif "Compliance" in agent_choice:
            st.code("""
Agent: Compliance Agent
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 10 minutes
Trigger: Config Rules + EventBridge (hourly)
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.1 (deterministic)
Tools: AWS Config, Security Hub, Audit Manager,
       CloudTrail, Organizations API
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Auto-remediate Config violations")
            st.success("✅ Generate compliance reports")
            st.success("✅ Tag non-compliant resources")
            st.success("✅ Enable required encryption")
            st.warning("⚠️ Policy exceptions (requires approval)")
            
        elif "DevOps" in agent_choice:
            st.code("""
Agent: DevOps Agent
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 15 minutes
Trigger: CodePipeline + GitHub Webhooks
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.3
Tools: CodePipeline, CodeBuild, ECR,
       GitHub API, Terraform, CloudFormation
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Optimize CI/CD pipelines")
            st.success("✅ Auto-fix build failures")
            st.success("✅ Security scan remediation")
            st.success("✅ Infrastructure drift detection")
            st.warning("⚠️ Production deployments (requires approval)")
            
        elif "Database" in agent_choice:
            st.code("""
Agent: Database Agent
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 5 minutes
Trigger: EventBridge + IAM Events
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.2 (deterministic)
Tools: RDS API, DynamoDB API, IAM API,
       Secrets Manager, CloudWatch Logs
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Grant time-limited DB access")
            st.success("✅ Auto-revoke expired sessions")
            st.success("✅ Performance optimization")
            st.success("✅ Automated backup verification")
            st.warning("⚠️ Schema changes (requires approval)")
            
        elif "FinOps" in agent_choice:
            st.code("""
Agent: FinOps Agent
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 5 minutes
Trigger: EventBridge (hourly) + Cost Anomaly
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.3
Tools: Cost Explorer, EC2 API, RDS API,
       Savings Plans API, Reserved Instance API
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Right-size instances (<$10K)")
            st.success("✅ Terminate idle resources")
            st.success("✅ Storage tier optimization")
            st.success("✅ Anomaly detection & alerts")
            st.warning("⚠️ RI/SP purchases (requires approval)")
            
        else:  # Policy Engine
            st.code("""
Agent: Policy Engine
Runtime: Lambda Python 3.12
Memory: 512MB
Timeout: 5 minutes
Trigger: EventBridge + CloudFormation hooks
Model: Claude 4 Sonnet
Context Window: 200K tokens
Temperature: 0.1 (deterministic)
Tools: Organizations API, SCP API, Config,
       CloudFormation, Service Catalog
            """, language="yaml")
            st.markdown("### Autonomous Capabilities")
            st.success("✅ Generate policies from patterns")
            st.success("✅ A/B test policy effectiveness")
            st.success("✅ Auto-update guardrails")
            st.success("✅ Exception management")
            st.warning("⚠️ SCP deployment (requires approval)")
    
    with col2:
        st.markdown("### Live Decision Scenario")
        
        # Dynamic scenarios based on agent
        if "Security" in agent_choice:
            scenarios = ["Exposed S3 Bucket", "Compromised Credentials", "Unpatched EC2"]
        elif "Compliance" in agent_choice:
            scenarios = ["PCI DSS Violation", "Encryption Missing", "Tagging Non-Compliance"]
        elif "DevOps" in agent_choice:
            scenarios = ["Pipeline Optimization", "Build Failure", "Security Scan Finding"]
        elif "Database" in agent_choice:
            scenarios = ["Access Request", "Performance Issue", "Session Audit"]
        elif "FinOps" in agent_choice:
            scenarios = ["Cost Optimization", "Anomaly Detection", "Commitment Analysis"]
        else:
            scenarios = ["Policy Generation", "Violation Pattern", "Effectiveness Review"]
        
        scenario_type = st.radio(
            "Select Scenario:",
            scenarios,
            horizontal=True
        )
        
        if st.button("🚀 Run AI Analysis", use_container_width=True):
            with st.spinner("Claude 4 analyzing scenario..."):
                time.sleep(2)
                
                # Generate agent-specific reasoning
                if "Security" in agent_choice:
                    if scenario_type == "Exposed S3 Bucket":
                        st.markdown("""
**🛡️ Security Agent - Exposed S3 Bucket**

```
THREAT ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource: s3://prod-data-analytics-2024
Issue: Public access enabled, PII detected
Risk Score: 9/10 (CRITICAL)

CONTEXT GATHERED:
• Bucket contains 2,847 objects (127GB)
• 47,000+ customer records with PII
• Created 3 hours ago by dev-team-lead
• No encryption enabled

DECISION: IMMEDIATE REMEDIATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Block public access ✅ EXECUTED
Action 2: Enable AES-256 encryption ✅ EXECUTED
Action 3: Enable access logging ✅ EXECUTED
Action 4: Create Security Hub finding ✅ EXECUTED
Action 5: Notify security team ✅ EXECUTED

Total Response Time: 1.2 seconds
```
                        """)
                    elif scenario_type == "Compromised Credentials":
                        st.markdown("""
**🛡️ Security Agent - Compromised Credentials**

```
CREDENTIAL THREAT ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alert Source: AWS GuardDuty
Finding: UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration
User: svc-deployment-prod
Risk Score: 10/10 (CRITICAL)

CONTEXT GATHERED:
• Credentials used from IP: 185.143.xx.xx (Russia)
• Normal usage: us-east-1, us-west-2 only
• 47 API calls in last 5 minutes
• Attempted actions: ListBuckets, GetObject, CreateUser

DECISION: IMMEDIATE LOCKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Disable IAM user ✅ EXECUTED (0.3s)
Action 2: Revoke all active sessions ✅ EXECUTED
Action 3: Rotate all associated keys ✅ EXECUTED
Action 4: Block source IP in WAF ✅ EXECUTED
Action 5: Trigger incident response runbook ✅ EXECUTED
Action 6: Page on-call security engineer ✅ EXECUTED

Threat Contained: 4.7 seconds
```
                        """)
                    else:  # Unpatched EC2
                        st.markdown("""
**🛡️ Security Agent - Unpatched EC2 Instance**

```
VULNERABILITY ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instance: i-0a1b2c3d4e5f (prod-web-server-03)
Finding: CVE-2024-6387 (regreSSHion)
CVSS Score: 8.1 (HIGH)
Exposure: Internet-facing (port 22 open)

CONTEXT GATHERED:
• Instance running Amazon Linux 2023
• OpenSSH version: 8.7p1 (vulnerable)
• Patch available: openssh-8.7p1-8.amzn2023
• Workload: Production API server
• Traffic: 12,000 req/min

DECISION: SCHEDULED PATCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Add to WAF rate limiting ✅ EXECUTED
Action 2: Restrict SSH to bastion only ✅ EXECUTED
Action 3: Create patching ticket (P1) ✅ EXECUTED
Action 4: Schedule maintenance window ✅ Tonight 2AM EST
Action 5: Prepare rollback AMI ✅ EXECUTED
Action 6: Notify application team ✅ EXECUTED

Risk Mitigated: 94% | Full patch: 6 hours
```
                        """)
                elif "Compliance" in agent_choice:
                    if scenario_type == "PCI DSS Violation":
                        st.markdown("""
**⚖️ Compliance Agent - PCI DSS Violation**

```
COMPLIANCE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Framework: PCI DSS 4.0
Violation: Requirement 3.4.1 - Data encryption
Resource: rds:prod-payments-db
Risk: HIGH

CONTEXT GATHERED:
• Database stores cardholder data
• Encryption at rest: DISABLED
• Last audit: 45 days ago
• Compliance score impact: -2.3%

DECISION: AUTO-REMEDIATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Enable RDS encryption ✅ SCHEDULED
Action 2: Update Config rule status ✅ EXECUTED
Action 3: Generate evidence artifact ✅ EXECUTED
Action 4: Update compliance dashboard ✅ EXECUTED

Compliance Score: 94.8% → 97.1%
```
                        """)
                    elif scenario_type == "Encryption Missing":
                        st.markdown("""
**⚖️ Compliance Agent - Encryption Missing**

```
ENCRYPTION COMPLIANCE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frameworks Affected: SOC 2, HIPAA, ISO 27001
Resource: ebs-vol-0abc123def456
Type: EBS Volume (500GB gp3)
Attached To: i-prod-healthcare-app-01
Risk: CRITICAL

CONTEXT GATHERED:
• Volume contains PHI (Protected Health Info)
• Created 2 days ago during migration
• Encryption was not enabled at creation
• Cannot enable encryption on existing volume
• Workload: 24/7 production application

DECISION: MIGRATE TO ENCRYPTED VOLUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Create encrypted snapshot ✅ IN PROGRESS
Action 2: Create new encrypted volume ✅ PENDING
Action 3: Schedule migration window ✅ Saturday 3AM
Action 4: Update HIPAA evidence log ✅ EXECUTED
Action 5: Notify compliance officer ✅ EXECUTED

Compliance Gap: Resolved in 72 hours
```
                        """)
                    else:  # Tagging Non-Compliance
                        st.markdown("""
**⚖️ Compliance Agent - Tagging Non-Compliance**

```
TAGGING COMPLIANCE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Policy: Mandatory Resource Tagging
Resources Scanned: 12,847
Non-Compliant: 234 resources (1.8%)
Risk: MEDIUM

NON-COMPLIANT BREAKDOWN:
• Missing 'Environment' tag: 89 resources
• Missing 'CostCenter' tag: 156 resources
• Missing 'Owner' tag: 67 resources
• Invalid tag values: 23 resources

TOP OFFENDING ACCOUNTS:
1. dev-sandbox-team-a (78 resources)
2. prod-data-analytics (52 resources)
3. staging-platform (41 resources)

DECISION: AUTO-TAG + NOTIFY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Apply default tags to dev resources ✅ EXECUTED
Action 2: Generate owner report for prod ✅ EXECUTED
Action 3: Send Slack notification to teams ✅ EXECUTED
Action 4: Create Jira tickets for manual review ✅ EXECUTED
Action 5: Schedule follow-up scan (7 days) ✅ EXECUTED

Expected Compliance: 98.5% after remediation
```
                        """)
                elif "DevOps" in agent_choice:
                    if scenario_type == "Pipeline Optimization":
                        st.markdown("""
**⚙️ DevOps Agent - Pipeline Optimization**

```
PIPELINE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pipeline: backend-api-main
Current Build Time: 14m 32s
Bottleneck: Test stage (9m 15s)

OPTIMIZATION OPPORTUNITIES:
• Tests running sequentially (847 tests)
• No Docker layer caching
• Fresh npm install each build

DECISION: OPTIMIZE PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Enable parallel testing (4 runners) ✅
Action 2: Configure Docker layer caching ✅
Action 3: Add npm dependency caching ✅
Action 4: Implement test splitting ✅

Expected Improvement: 14m 32s → 5m 05s (-65%)
Monthly Savings: $2,400 in build minutes
```
                        """)
                    elif scenario_type == "Build Failure":
                        st.markdown("""
**⚙️ DevOps Agent - Build Failure Analysis**

```
BUILD FAILURE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pipeline: frontend-webapp-prod
Build ID: #4521
Failed Stage: Unit Tests
Duration Before Failure: 6m 43s

ERROR DETECTED:
TypeError: Cannot read property 'map' of undefined
  at UserList.render (src/components/UserList.jsx:45)
  at processChild (node_modules/react-dom/...)

ROOT CAUSE ANALYSIS:
• Recent commit: a]9f2c3d by dev@company.com
• Changed: UserList component props
• Missing null check for users array
• 3 similar failures in last 24 hours

DECISION: AUTO-FIX + NOTIFY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Identify breaking commit ✅ EXECUTED
Action 2: Generate fix suggestion ✅ EXECUTED
Action 3: Create PR with fix ✅ PR #892 opened
Action 4: Notify developer via Slack ✅ EXECUTED
Action 5: Block merge to main ✅ EXECUTED

Suggested Fix: Add optional chaining (users?.map)
```
                        """)
                    else:  # Security Scan Finding
                        st.markdown("""
**⚙️ DevOps Agent - Security Scan Finding**

```
SECURITY SCAN ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scanner: Snyk + Trivy
Pipeline: microservices-deploy
Findings: 12 vulnerabilities detected

CRITICAL FINDINGS:
┌─────────────────────────────────────────────────┐
│ CVE-2024-1234 | lodash < 4.17.21 | CRITICAL    │
│ CVE-2024-5678 | axios < 1.6.0   | HIGH        │
│ CVE-2024-9012 | express < 4.18  | HIGH        │
└─────────────────────────────────────────────────┘

CONTEXT:
• 8 dependencies need updates
• 4 findings are in dev dependencies only
• No known exploits in production path
• Last security scan: 3 days ago

DECISION: REMEDIATE + GATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Block deployment (critical vuln) ✅ EXECUTED
Action 2: Auto-generate dependency PR ✅ PR #893
Action 3: Run compatibility tests ✅ IN PROGRESS
Action 4: Notify security team ✅ EXECUTED
Action 5: Update vulnerability dashboard ✅ EXECUTED

Pipeline Status: BLOCKED until PR merged
```
                        """)
                elif "Database" in agent_choice:
                    if scenario_type == "Access Request":
                        st.markdown("""
**🗄️ Database Agent - Access Request**

```
ACCESS REQUEST ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requester: john.doe@company.com
Database: prod-postgres-01
Access Type: Read-Only
Duration: 4 hours
Justification: "Q4 revenue analysis for board"

USER PROFILE:
• Role: Senior Data Analyst
• Previous requests: 15 (100% compliant)
• Manager: jane.smith@company.com
• Team: Business Intelligence

RISK ASSESSMENT: LOW (3/10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DECISION: GRANT ACCESS

Action 1: Generate temp credentials (4h TTL) ✅
Action 2: Restrict to analytics schema ✅
Action 3: Enable query logging ✅
Action 4: Set auto-revocation timer ✅
Action 5: Notify user via Slack ✅
```
                        """)
                    elif scenario_type == "Performance Issue":
                        st.markdown("""
**🗄️ Database Agent - Performance Issue**

```
PERFORMANCE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: prod-mysql-orders
Alert: High CPU utilization (94%)
Duration: Last 15 minutes
Impact: API latency increased 340%

QUERY ANALYSIS:
• Slow query detected (12.4s execution)
• Query: SELECT * FROM orders WHERE...
• Missing index on 'customer_id' column
• Full table scan: 2.3M rows
• Executed 847 times in last hour

ROOT CAUSE:
• New feature deployed 2 hours ago
• Query pattern not optimized
• No index coverage for new filter

DECISION: OPTIMIZE + ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Create index recommendation ✅ EXECUTED
Action 2: Apply index (online DDL) ✅ IN PROGRESS
Action 3: Kill long-running queries ✅ EXECUTED
Action 4: Enable query result caching ✅ EXECUTED
Action 5: Notify dev team ✅ EXECUTED

Expected Improvement: 12.4s → 0.02s (-99.8%)
```
                        """)
                    else:  # Session Audit
                        st.markdown("""
**🗄️ Database Agent - Session Audit**

```
SESSION AUDIT ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: prod-postgres-analytics
Audit Period: Last 24 hours
Total Sessions: 1,247
Flagged Sessions: 3

ANOMALY DETECTED:
┌─────────────────────────────────────────────────┐
│ Session ID: sess_8a7b6c5d                       │
│ User: svc-etl-pipeline                          │
│ Duration: 18 hours (unusual)                    │
│ Queries: 47,000+ (10x normal)                   │
│ Data Exported: 2.3GB                            │
└─────────────────────────────────────────────────┘

CONTEXT GATHERED:
• Service account for ETL jobs
• Normal runtime: 2-3 hours
• Query pattern: Sequential table scans
• No matching scheduled job found

RISK ASSESSMENT: MEDIUM (6/10)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DECISION: INVESTIGATE + CONTAIN

Action 1: Terminate suspicious session ✅ EXECUTED
Action 2: Rotate service account creds ✅ EXECUTED
Action 3: Export session logs ✅ EXECUTED
Action 4: Create Security Hub finding ✅ EXECUTED
Action 5: Page data engineering team ✅ EXECUTED

Status: Under investigation
```
                        """)
                elif "FinOps" in agent_choice:
                    if scenario_type == "Cost Optimization":
                        st.markdown(simulate_claude_reasoning('cost_optimization'))
                    elif scenario_type == "Anomaly Detection":
                        st.markdown(simulate_claude_reasoning('anomaly'))
                    else:  # Commitment Analysis
                        st.markdown(simulate_claude_reasoning('commitment'))
                else:
                    # Policy Engine scenarios - check which scenario is selected
                    if scenario_type == "Policy Generation":
                        st.markdown("""
**📋 Policy Engine - Policy Generation**

```
POLICY GENERATION REQUEST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Request Type: New Security Control
Target: EC2 Instance Metadata Service
Scope: All Production Accounts (127 accounts)

ANALYSIS:
• IMDSv1 vulnerable to SSRF attacks
• 340 instances currently using IMDSv1
• No existing preventive control
• AWS Best Practice: Enforce IMDSv2

GENERATED POLICY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Policy Type: Service Control Policy (SCP)
Policy Name: RequireIMDSv2

{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Condition": {
    "StringNotEquals": {
      "ec2:MetadataHttpTokens": "required"
    }
  }
}

DEPLOYMENT PLAN:
• Phase 1: Sandbox OUs (Day 1-7)
• Phase 2: Development OUs (Day 8-14)
• Phase 3: Production OUs (Day 15-21)

Confidence Score: 97%
```
                        """)
                    elif scenario_type == "Violation Pattern":
                        st.markdown("""
**📋 Policy Engine - Violation Pattern Analysis**

```
PATTERN ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Detected Pattern: Unencrypted S3 buckets
Occurrences: 23 in last 30 days
Affected Accounts: 12
Trend: Increasing (+15%)

ROOT CAUSE:
• No preventive control exists
• Only detective Config rule in place
• 67% of developers unaware of requirement

DECISION: GENERATE PREVENTIVE POLICY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Policy Type: Service Control Policy (SCP)
Target OUs: Production, Staging

Generated SCP:
{
  "Effect": "Deny",
  "Action": "s3:CreateBucket",
  "Condition": {
    "StringNotEquals": {
      "s3:x-amz-server-side-encryption": "AES256"
    }
  }
}

Expected Impact: 95%+ violations prevented
```
                        """)
                    else:  # Effectiveness Review
                        st.markdown("""
**📋 Policy Engine - Effectiveness Review**

```
POLICY EFFECTIVENESS ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Period: Last 30 Days
Policies Evaluated: 87 Active Policies
Overall Effectiveness: 96.4%

TOP PERFORMERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. RequireS3Encryption     - 99.2% (1,247 blocks)
2. DenyPublicRDS           - 98.8% (89 blocks)
3. EnforceMFA              - 97.5% (2,340 blocks)
4. RestrictRegions         - 96.1% (445 blocks)

NEEDS ATTENTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. EC2TaggingPolicy        - 78.3% (HIGH bypass rate)
   └─ Root Cause: Exception list too broad
   └─ Recommendation: Tighten exception criteria

2. CostAllocationTags      - 72.1% (MEDIUM bypass rate)
   └─ Root Cause: New accounts not included
   └─ Recommendation: Update OU attachment

DECISION: UPDATE 2 POLICIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Action 1: Revise EC2TaggingPolicy exceptions ✅
Action 2: Extend CostAllocationTags scope ✅
Action 3: Schedule re-evaluation in 7 days ✅

Projected Improvement: 96.4% → 98.1%
```
                        """)
                
                st.success("✅ Analysis Complete - Decision logged to audit trail")
    
    st.markdown("---")
    
    # ============ ALL 6 AGENTS STATUS GRID ============
    st.subheader("📊 All Agents Status & Performance")
    
    # 6 agent cards in 2 rows of 3
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    
    with row1_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>🛡️ Security Agent</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Threats Blocked: <span style='color: #10B981; font-weight: 700;'>47</span><br/>
                Response Time: <span style='color: #10B981; font-weight: 700;'>1.2s</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>156</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>⚖️ Compliance Agent</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Compliance Score: <span style='color: #10B981; font-weight: 700;'>97.2%</span><br/>
                Violations Fixed: <span style='color: #10B981; font-weight: 700;'>34</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>89</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>⚙️ DevOps Agent</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Pipelines Optimized: <span style='color: #10B981; font-weight: 700;'>47</span><br/>
                Build Time Saved: <span style='color: #10B981; font-weight: 700;'>-45%</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>201</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>🗄️ Database Agent</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Access Requests: <span style='color: #10B981; font-weight: 700;'>32</span><br/>
                Auto-Approved: <span style='color: #10B981; font-weight: 700;'>28</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>67</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>💰 FinOps Agent</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Cost Savings: <span style='color: #10B981; font-weight: 700;'>$487K</span><br/>
                Optimizations: <span style='color: #10B981; font-weight: 700;'>156</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>412</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border: 1px solid #334155; border-left: 4px solid #22C55E; border-radius: 8px; padding: 16px; margin: 8px 0;'>
            <div style='font-size: 1.1rem; font-weight: 700; color: #F1F5F9;'>📋 Policy Engine</div>
            <div style='color: #22C55E; font-size: 12px; font-weight: 600; margin: 4px 0;'>● ACTIVE</div>
            <div style='margin-top: 8px; font-size: 13px; color: #94A3B8;'>
                Active Policies: <span style='color: #10B981; font-weight: 700;'>87</span><br/>
                AI-Generated: <span style='color: #10B981; font-weight: 700;'>34</span><br/>
                Decisions Today: <span style='color: #10B981; font-weight: 700;'>45</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agent decision distribution chart
    st.subheader("📈 Agent Decision Distribution (Last 24h)")
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Security', 'Compliance', 'DevOps', 'Database', 'FinOps', 'Policy'],
            y=[156, 89, 201, 67, 412, 45],
            marker_color=['#EF4444', '#3B82F6', '#F59E0B', '#8B5CF6', '#10B981', '#EC4899'],
            text=[156, 89, 201, 67, 412, 45],
            textposition='auto',
            textfont=dict(color='#FFFFFF', size=14, family='Arial Black')
        )
    ])
    fig.update_layout(
        title=dict(text="Autonomous Decisions by Agent", font=dict(color='#FFFFFF', size=16)),
        template='plotly_dark',
        height=350,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        xaxis=dict(tickfont=dict(color='#FFFFFF', size=12)),
        yaxis=dict(tickfont=dict(color='#FFFFFF'), title=dict(text='Decisions', font=dict(color='#FFFFFF')))
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Decisions/Day", "970", "+89 vs yesterday")
    with col2:
        st.metric("Overall Success Rate", "98.7%", "+0.2%")
    with col3:
        st.metric("Avg Decision Time", "1.3s", "-0.1s")
    with col4:
        st.metric("Human Escalations", "12", "-3 vs yesterday")

with tab7:
    st.header("💰 FinOps Intelligence & Cost Optimization")
    
    # Create sub-tabs for FinOps
    finops_tab1, finops_tab2, finops_tab3, finops_tab4, finops_tab5, finops_tab6, finops_tab7, finops_tab8, finops_tab9 = st.tabs([
        "💵 Cost Overview",
        "🤖 AI/ML Costs",
        "⚠️ Anomalies",
        "📊 Optimization",
        "📈 Budget & Forecast",
        "🗑️ Waste Detection",
        "💳 Chargeback",
        "📉 Unit Economics",
        "🌱 Sustainability"
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
                marker_colors=['#A3BE8C', '#88C0D0', '#EBCB8B', '#B48EAD', '#5E81AC', '#D08770', '#81A1C1', '#BF616A', '#4C566A'],
                textinfo='percent',
                textfont=dict(color='#FFFFFF', size=11),
                insidetextfont=dict(color='#FFFFFF'),
                outsidetextfont=dict(color='#FFFFFF')
            )])
            fig.update_layout(
                template='plotly_dark', 
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#FFFFFF', size=11)),
                font=dict(color='#FFFFFF')
            )
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
    
    # ==================== FINOPS TAB 5: BUDGET & FORECASTING ====================
    with finops_tab5:
        st.subheader("📈 Budget Management & Forecasting")
        
        st.markdown("""
        **AI-powered budget tracking and spend forecasting** with variance analysis, 
        alerts, and predictive modeling across all portfolios and accounts.
        """)
        
        # Budget metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly Budget", "$3.2M", "FY2024-Q4")
        with col2:
            st.metric("Current Spend", "$2.8M", "87.5% utilized")
        with col3:
            st.metric("Forecasted EOY", "$3.1M", "-$100K under budget")
        with col4:
            st.metric("Budget Alerts", "3 Active", "2 Warning, 1 Critical")
        
        st.markdown("---")
        
        # Budget vs Actual by Portfolio
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Budget vs Actual by Portfolio")
            
            portfolios = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Management', 'Data Platform']
            budget = [850000, 620000, 480000, 520000, 380000, 350000]
            actual = [820000, 680000, 450000, 490000, 410000, 330000]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Budget',
                x=portfolios,
                y=budget,
                marker_color='#5E81AC',
                text=[f'${b/1000:.0f}K' for b in budget],
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            ))
            
            fig.add_trace(go.Bar(
                name='Actual',
                x=portfolios,
                y=actual,
                marker_color='#A3BE8C',
                text=[f'${a/1000:.0f}K' for a in actual],
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            ))
            
            # Add variance indicators
            for i, (b, a) in enumerate(zip(budget, actual)):
                variance = ((a - b) / b) * 100
                color = '#BF616A' if variance > 5 else '#A3BE8C' if variance < -5 else '#EBCB8B'
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                barmode='group',
                yaxis_title='Monthly Spend ($)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🚨 Budget Alerts")
            
            alerts = [
                ("🔴 CRITICAL", "Insurance Portfolio", "+9.7% over budget", "$680K vs $620K"),
                ("🟡 WARNING", "Wealth Management", "+7.9% over budget", "$410K vs $380K"),
                ("🟡 WARNING", "SageMaker Spend", "Approaching limit", "92% of ML budget"),
            ]
            
            for severity, area, issue, detail in alerts:
                color = "#BF616A" if "CRITICAL" in severity else "#EBCB8B"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid {color};'>
                    <strong style='color: {color};'>{severity}</strong><br/>
                    <strong>{area}</strong><br/>
                    <small>{issue}</small><br/>
                    <small style='color: #88C0D0;'>{detail}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### ✅ On Track")
            on_track = [
                ("Digital Banking", "-3.5%"),
                ("Payments", "-6.3%"),
                ("Capital Markets", "-5.8%"),
                ("Data Platform", "-5.7%")
            ]
            for portfolio, variance in on_track:
                st.success(f"**{portfolio}**: {variance} under budget")
        
        st.markdown("---")
        
        # Forecasting Section
        st.markdown("### 🔮 AI-Powered Spend Forecasting")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Generate historical and forecast data
            historical_dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
            forecast_dates = pd.date_range(start=datetime.now() + timedelta(days=1), periods=90, freq='D')
            
            # Historical spend with trend
            base_spend = 93000
            historical_spend = base_spend + np.cumsum(np.random.normal(100, 500, 90))
            
            # Forecast with confidence intervals
            forecast_base = historical_spend[-1]
            forecast_spend = forecast_base + np.cumsum(np.random.normal(150, 300, 90))
            forecast_upper = forecast_spend + np.linspace(5000, 25000, 90)
            forecast_lower = forecast_spend - np.linspace(5000, 25000, 90)
            
            fig = go.Figure()
            
            # Historical
            fig.add_trace(go.Scatter(
                x=historical_dates, y=historical_spend,
                name='Historical Spend',
                line=dict(color='#A3BE8C', width=2)
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=forecast_dates, y=forecast_spend,
                name='Forecasted Spend',
                line=dict(color='#88C0D0', width=2, dash='dash')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=list(forecast_dates) + list(forecast_dates[::-1]),
                y=list(forecast_upper) + list(forecast_lower[::-1]),
                fill='toself',
                fillcolor='rgba(136, 192, 208, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval'
            ))
            
            # Budget line
            budget_line = [105000] * len(historical_dates) + [105000] * len(forecast_dates)
            fig.add_trace(go.Scatter(
                x=list(historical_dates) + list(forecast_dates),
                y=budget_line,
                name='Monthly Budget',
                line=dict(color='#EBCB8B', width=2, dash='dot')
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                yaxis_title='Daily Spend ($)',
                xaxis_title='Date',
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Forecast Summary")
            
            st.info("""
            **Model**: ARIMA + ML Ensemble
            **Accuracy**: 94.2%
            **Last Updated**: 2 hours ago
            """)
            
            st.metric("30-Day Forecast", "$3.05M", "+8.9% MoM")
            st.metric("60-Day Forecast", "$3.18M", "+4.3% MoM")
            st.metric("90-Day Forecast", "$3.24M", "+1.9% MoM")
            
            st.markdown("---")
            
            st.markdown("**Key Drivers:**")
            st.markdown("""
            - 📈 ML workload growth (+12%)
            - 📈 New Bedrock agents (+3)
            - 📉 RI expiration offset
            - 📉 Optimization savings
            """)
        
        st.markdown("---")
        
        # Variance Analysis
        st.markdown("### 📉 Variance Analysis - Current Month")
        
        variance_data = pd.DataFrame({
            'Category': ['EC2 Compute', 'RDS Database', 'SageMaker', 'Bedrock', 'S3 Storage', 'Data Transfer', 'Lambda', 'EKS'],
            'Budget': [900000, 450000, 320000, 100000, 280000, 250000, 180000, 320000],
            'Actual': [850000, 420000, 340000, 125000, 280000, 290000, 175000, 350000],
            'Variance': [-50000, -30000, 20000, 25000, 0, 40000, -5000, 30000],
            'Variance %': ['-5.6%', '-6.7%', '+6.3%', '+25.0%', '0.0%', '+16.0%', '-2.8%', '+9.4%']
        })
        
        st.dataframe(
            variance_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Budget': st.column_config.NumberColumn('Budget', format='$%d'),
                'Actual': st.column_config.NumberColumn('Actual', format='$%d'),
                'Variance': st.column_config.NumberColumn('Variance', format='$%d')
            }
        )
    
    # ==================== FINOPS TAB 6: WASTE DETECTION ====================
    with finops_tab6:
        st.subheader("🗑️ Waste Detection & Idle Resources")
        
        st.markdown("""
        **Automated identification of cloud waste** including idle resources, orphaned assets, 
        and optimization opportunities across 640+ AWS accounts.
        """)
        
        # Waste summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Waste Identified", "$187K/month", "↓ $23K from last week")
        with col2:
            st.metric("Idle Resources", "1,847", "Ready for cleanup")
        with col3:
            st.metric("Auto-Cleaned", "342", "This week")
        with col4:
            st.metric("Waste Score", "7.2%", "Target: <5%")
        
        st.markdown("---")
        
        # Waste breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Waste by Category")
            
            waste_categories = ['Idle EC2', 'Unattached EBS', 'Old Snapshots', 'Unused EIPs', 'Idle RDS', 
                              'Orphaned LBs', 'Stale AMIs', 'Unused NAT GW']
            waste_amounts = [67000, 38000, 28000, 12000, 22000, 8000, 7000, 5000]
            waste_counts = [234, 567, 1245, 89, 45, 23, 156, 12]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=waste_categories,
                y=waste_amounts,
                marker_color=['#BF616A', '#D08770', '#EBCB8B', '#A3BE8C', '#88C0D0', '#5E81AC', '#B48EAD', '#81A1C1'],
                text=[f'${w/1000:.0f}K' for w in waste_amounts],
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                yaxis_title='Monthly Waste ($)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Quick Actions")
            
            if st.button("🧹 Clean Unattached EBS", use_container_width=True, type="primary"):
                st.success("✅ Initiated cleanup of 567 unattached EBS volumes")
            
            if st.button("🗑️ Delete Old Snapshots", use_container_width=True):
                st.success("✅ Queued 1,245 snapshots for deletion")
            
            if st.button("🔌 Release Unused EIPs", use_container_width=True):
                st.success("✅ Released 89 unused Elastic IPs")
            
            if st.button("⏹️ Stop Idle EC2", use_container_width=True):
                st.info("⚠️ Review required: 234 instances flagged")
            
            st.markdown("---")
            
            st.markdown("### 📅 Cleanup Schedule")
            st.markdown("""
            - **Daily**: EIP release, snapshot cleanup
            - **Weekly**: Idle EC2 review
            - **Monthly**: Full waste audit
            """)
        
        st.markdown("---")
        
        # Detailed waste table
        st.markdown("### 📋 Idle Resources Detail")
        
        idle_tab1, idle_tab2, idle_tab3, idle_tab4 = st.tabs([
            "💻 Idle EC2", "💾 Unattached EBS", "📸 Old Snapshots", "🔗 Other"
        ])
        
        with idle_tab1:
            idle_ec2 = []
            instance_types = ['t3.xlarge', 'm5.2xlarge', 'c5.4xlarge', 'r5.2xlarge', 't3.2xlarge']
            for i in range(15):
                idle_ec2.append({
                    'Instance ID': f'i-{random.randint(10000000, 99999999):08x}',
                    'Type': random.choice(instance_types),
                    'Account': f'prod-{random.choice(["banking", "payments", "insurance", "data"])}-{random.randint(1,99):03d}',
                    'Idle Days': random.randint(7, 90),
                    'CPU Avg': f'{random.uniform(0.5, 5):.1f}%',
                    'Monthly Cost': f'${random.randint(50, 800)}',
                    'Owner': random.choice(['dev-team', 'data-science', 'platform', 'unknown'])
                })
            
            st.dataframe(pd.DataFrame(idle_ec2), use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Idle EC2", "234 instances")
            with col2:
                st.metric("Monthly Waste", "$67,000")
            with col3:
                st.metric("Avg Idle Time", "34 days")
        
        with idle_tab2:
            unattached_ebs = []
            for i in range(15):
                unattached_ebs.append({
                    'Volume ID': f'vol-{random.randint(10000000, 99999999):08x}',
                    'Size': f'{random.choice([100, 200, 500, 1000, 2000])} GB',
                    'Type': random.choice(['gp3', 'gp2', 'io1', 'st1']),
                    'Account': f'prod-{random.choice(["banking", "payments", "insurance"])}-{random.randint(1,99):03d}',
                    'Unattached Days': random.randint(14, 180),
                    'Monthly Cost': f'${random.randint(10, 200)}',
                    'Last Attached To': f'i-{random.randint(10000000, 99999999):08x}'
                })
            
            st.dataframe(pd.DataFrame(unattached_ebs), use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unattached Volumes", "567 volumes")
            with col2:
                st.metric("Total Size", "245 TB")
            with col3:
                st.metric("Monthly Waste", "$38,000")
        
        with idle_tab3:
            old_snapshots = []
            for i in range(15):
                old_snapshots.append({
                    'Snapshot ID': f'snap-{random.randint(10000000, 99999999):08x}',
                    'Size': f'{random.choice([50, 100, 200, 500])} GB',
                    'Age': f'{random.randint(90, 365)} days',
                    'Account': f'prod-{random.choice(["banking", "payments", "insurance"])}-{random.randint(1,99):03d}',
                    'Description': random.choice(['Auto backup', 'Manual snapshot', 'Pre-migration', 'Unknown']),
                    'Monthly Cost': f'${random.randint(2, 25)}'
                })
            
            st.dataframe(pd.DataFrame(old_snapshots), use_container_width=True, hide_index=True)
            
            st.warning("""
            **⚠️ Recommendation**: Implement lifecycle policy to auto-delete snapshots older than 90 days 
            (excluding compliance-required backups). Expected savings: $28K/month.
            """)
        
        with idle_tab4:
            st.markdown("#### Other Waste Categories")
            
            other_waste = [
                ("Unused Elastic IPs", "89 IPs", "$12,000/month", "EIPs not attached to running instances"),
                ("Idle RDS Instances", "45 instances", "$22,000/month", "DB instances with <5% connections"),
                ("Orphaned Load Balancers", "23 ALBs/NLBs", "$8,000/month", "LBs with no healthy targets"),
                ("Stale AMIs", "156 AMIs", "$7,000/month", "AMIs not used in 180+ days"),
                ("Unused NAT Gateways", "12 NAT GWs", "$5,000/month", "NAT GWs with zero data processed")
            ]
            
            for resource, count, cost, description in other_waste:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong>{resource}</strong>
                        <span style='color: #A3BE8C;'>{cost}</span>
                    </div>
                    <small>{count} | {description}</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Claude Analysis
        st.markdown("### 🤖 Claude Waste Analysis")
        
        with st.expander("View AI-Generated Waste Report", expanded=False):
            st.markdown("""
**Weekly Waste Analysis Report** - Generated by Claude 4

**Executive Summary:**
Total identifiable waste: $187K/month across 1,847 resources. This represents 7.2% of total spend, 
above our 5% target. Week-over-week improvement of $23K due to automated cleanup actions.

**Top Findings:**

1. **Idle EC2 Instances ($67K/month)**
   - 234 instances averaging <5% CPU utilization
   - 67% are in development accounts (expected for weekends)
   - 33% in production accounts require investigation
   - **Recommendation**: Implement scheduled scaling for dev environments
   - **Confidence**: 94%

2. **Unattached EBS Volumes ($38K/month)**
   - 567 volumes totaling 245TB unattached storage
   - Average unattached duration: 45 days
   - 78% were created during instance terminations
   - **Recommendation**: Enable "Delete on Termination" by default
   - **Confidence**: 98%

3. **Snapshot Sprawl ($28K/month)**
   - 1,245 snapshots older than 90 days
   - No lifecycle policy in 45% of accounts
   - Many are pre-migration snapshots from 2023
   - **Recommendation**: Deploy organization-wide lifecycle policy
   - **Confidence**: 96%

**Automated Actions Taken This Week:**
- Released 89 unused Elastic IPs (saving $4K/month)
- Deleted 342 snapshots >180 days old (saving $8K/month)
- Stopped 23 dev instances over weekend (saving $2K)

**Projected Savings if All Recommendations Implemented:** $142K/month (76% of identified waste)
            """)
    
    # ==================== FINOPS TAB 7: SHOWBACK/CHARGEBACK ====================
    with finops_tab7:
        st.subheader("💳 Showback & Chargeback")
        
        st.markdown("""
        **Cost allocation and internal billing** - Track cloud spending by business unit, 
        application, team, and cost center with automated chargeback reports.
        """)
        
        # Chargeback metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Allocated", "$2.65M", "94.6% of spend")
        with col2:
            st.metric("Unallocated", "$150K", "5.4% - needs tagging")
        with col3:
            st.metric("Cost Centers", "47", "Active this month")
        with col4:
            st.metric("Chargeback Accuracy", "96.2%", "+1.8% improvement")
        
        st.markdown("---")
        
        # Cost allocation by business unit
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Cost Allocation by Business Unit")
            
            business_units = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 
                            'Wealth Management', 'Data Platform', 'Shared Services', 'Unallocated']
            bu_costs = [720000, 580000, 420000, 380000, 290000, 310000, 150000, 150000]
            bu_colors = ['#A3BE8C', '#88C0D0', '#EBCB8B', '#B48EAD', '#5E81AC', '#D08770', '#81A1C1', '#4C566A']
            
            fig = go.Figure(data=[go.Pie(
                labels=business_units,
                values=bu_costs,
                hole=0.4,
                marker_colors=bu_colors,
                textinfo='label+percent',
                textfont=dict(color='#FFFFFF', size=11),
                insidetextfont=dict(color='#FFFFFF'),
                outsidetextfont=dict(color='#FFFFFF')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#FFFFFF'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📋 Allocation Summary")
            
            for bu, cost in zip(business_units, bu_costs):
                pct = (cost / sum(bu_costs)) * 100
                color = "#BF616A" if bu == "Unallocated" else "#A3BE8C"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.5rem; border-radius: 5px; margin: 0.3rem 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span>{bu}</span>
                        <span style='color: {color};'>${cost/1000:.0f}K</span>
                    </div>
                    <small style='color: #88C0D0;'>{pct:.1f}% of total</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed chargeback table
        st.markdown("### 📋 Monthly Chargeback Report")
        
        chargeback_period = st.selectbox(
            "Select Period",
            ["November 2024", "October 2024", "September 2024", "Q3 2024"],
            key="chargeback_period"
        )
        
        chargeback_data = []
        cost_centers = ['CC-1001', 'CC-1002', 'CC-1003', 'CC-2001', 'CC-2002', 'CC-3001', 'CC-3002', 'CC-4001']
        teams = ['Core Banking', 'Mobile App', 'API Platform', 'Claims Processing', 'Underwriting', 
                'Payment Gateway', 'Fraud Detection', 'Trading Platform']
        
        for cc, team in zip(cost_centers, teams):
            chargeback_data.append({
                'Cost Center': cc,
                'Team': team,
                'Business Unit': random.choice(['Digital Banking', 'Insurance', 'Payments', 'Capital Markets']),
                'EC2': random.randint(50000, 200000),
                'RDS': random.randint(20000, 80000),
                'S3': random.randint(10000, 50000),
                'Other': random.randint(10000, 40000),
                'Total': 0
            })
        
        for row in chargeback_data:
            row['Total'] = row['EC2'] + row['RDS'] + row['S3'] + row['Other']
        
        df_chargeback = pd.DataFrame(chargeback_data)
        
        st.dataframe(
            df_chargeback,
            use_container_width=True,
            hide_index=True,
            column_config={
                'EC2': st.column_config.NumberColumn('EC2', format='$%d'),
                'RDS': st.column_config.NumberColumn('RDS', format='$%d'),
                'S3': st.column_config.NumberColumn('S3', format='$%d'),
                'Other': st.column_config.NumberColumn('Other', format='$%d'),
                'Total': st.column_config.NumberColumn('Total', format='$%d')
            }
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📧 Email Report", use_container_width=True):
                st.success("✅ Report sent to finance@company.com")
        with col2:
            if st.button("📥 Export CSV", use_container_width=True):
                st.success("✅ Downloaded chargeback_nov2024.csv")
        with col3:
            if st.button("📊 Export to SAP", use_container_width=True):
                st.success("✅ Exported to SAP FICO module")
        
        st.markdown("---")
        
        # Unallocated costs
        st.markdown("### ⚠️ Unallocated Costs - Action Required")
        
        unallocated = [
            ("i-0abc123def456", "EC2", "$4,200", "Missing 'CostCenter' tag", "prod-unknown-087"),
            ("arn:aws:rds:...", "RDS", "$2,800", "Missing 'Team' tag", "dev-sandbox-023"),
            ("prod-logs-bucket", "S3", "$1,500", "Missing 'BusinessUnit' tag", "logging-central"),
        ]
        
        for resource, service, cost, issue, account in unallocated:
            st.warning(f"""
            **{service}**: {resource}  
            Cost: {cost}/month | Issue: {issue} | Account: {account}
            """)
        
        st.info("""
        **💡 Tip**: Enable AWS Tag Policies in Organizations to enforce mandatory cost allocation tags 
        (CostCenter, Team, BusinessUnit, Environment) on all new resources.
        """)
    
    # ==================== FINOPS TAB 8: UNIT ECONOMICS ====================
    with finops_tab8:
        st.subheader("📉 Unit Economics & Efficiency Metrics")
        
        st.markdown("""
        **Track cost efficiency at the unit level** - cost per transaction, API call, user, 
        and business metric to understand true operational economics.
        """)
        
        # Unit economics metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cost per Transaction", "$0.0023", "-12% MoM")
        with col2:
            st.metric("Cost per API Call", "$0.00004", "-8% MoM")
        with col3:
            st.metric("Cost per Active User", "$0.42", "-5% MoM")
        with col4:
            st.metric("Efficiency Score", "94.2%", "+2.3%")
        
        st.markdown("---")
        
        # Unit cost trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Cost per Transaction Trend")
            
            dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
            cpt = 0.0032 - np.cumsum(np.random.normal(0.00003, 0.00005, 90))
            cpt = np.maximum(cpt, 0.0020)  # Floor value
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=cpt * 1000,  # Convert to millicents for readability
                name='Cost per Transaction (millicents)',
                line=dict(color='#A3BE8C', width=2),
                fill='tozeroy',
                fillcolor='rgba(163, 190, 140, 0.2)'
            ))
            
            fig.add_hline(y=2.0, line_dash="dash", line_color="#EBCB8B", 
                         annotation_text="Target: $0.002")
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                yaxis_title='Cost (millicents)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Cost per Active User Trend")
            
            dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
            cpu = 0.55 - np.cumsum(np.random.normal(0.001, 0.002, 90))
            cpu = np.maximum(cpu, 0.35)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=cpu,
                name='Cost per User',
                line=dict(color='#88C0D0', width=2),
                fill='tozeroy',
                fillcolor='rgba(136, 192, 208, 0.2)'
            ))
            
            fig.add_hline(y=0.40, line_dash="dash", line_color="#EBCB8B", 
                         annotation_text="Target: $0.40")
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                yaxis_title='Cost per User ($)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Unit economics by service
        st.markdown("### 📊 Unit Economics by Application")
        
        app_economics = pd.DataFrame({
            'Application': ['Mobile Banking', 'Payment Gateway', 'Fraud Detection', 'Trading Platform', 
                          'Customer Portal', 'API Gateway', 'Data Pipeline', 'ML Inference'],
            'Monthly Cost': [180000, 145000, 98000, 220000, 67000, 89000, 156000, 125000],
            'Transactions (M)': [89.2, 234.5, 67.8, 12.4, 45.6, 567.8, 23.4, 34.5],
            'Cost/Transaction': ['$0.0020', '$0.0006', '$0.0014', '$0.0177', '$0.0015', '$0.0002', '$0.0067', '$0.0036'],
            'MoM Change': ['-8%', '-12%', '-5%', '+3%', '-15%', '-18%', '-2%', '-9%'],
            'Efficiency': ['🟢 Good', '🟢 Excellent', '🟢 Good', '🟡 Fair', '🟢 Excellent', '🟢 Excellent', '🟡 Fair', '🟢 Good']
        })
        
        st.dataframe(
            app_economics,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Monthly Cost': st.column_config.NumberColumn('Monthly Cost', format='$%d'),
                'Transactions (M)': st.column_config.NumberColumn('Transactions (M)', format='%.1f')
            }
        )
        
        st.markdown("---")
        
        # Efficiency breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Efficiency Leaders")
            
            leaders = [
                ("API Gateway", "$0.0002/call", "High cache hit rate (94%)"),
                ("Payment Gateway", "$0.0006/txn", "Optimized Lambda concurrency"),
                ("Customer Portal", "$0.0015/session", "CDN optimization effective")
            ]
            
            for app, metric, reason in leaders:
                st.success(f"""
                **{app}**: {metric}  
                _{reason}_
                """)
        
        with col2:
            st.markdown("### ⚠️ Optimization Opportunities")
            
            opportunities = [
                ("Trading Platform", "$0.0177/txn", "Over-provisioned RDS instances"),
                ("Data Pipeline", "$0.0067/record", "Inefficient Spark jobs"),
                ("ML Inference", "$0.0036/prediction", "Consider SageMaker Serverless")
            ]
            
            for app, metric, reason in opportunities:
                st.warning(f"""
                **{app}**: {metric}  
                _{reason}_
                """)
        
        st.markdown("---")
        
        # Business metrics correlation
        st.markdown("### 📊 Cost vs Business Metrics")
        
        months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        revenue = [12.4, 13.1, 13.8, 14.2, 14.9, 15.6]
        cloud_cost = [2.4, 2.5, 2.6, 2.7, 2.75, 2.8]
        cost_ratio = [c/r*100 for c, r in zip(cloud_cost, revenue)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=months, y=revenue,
            name='Revenue ($M)',
            marker_color='#A3BE8C',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=months, y=cost_ratio,
            name='Cloud Cost Ratio (%)',
            line=dict(color='#BF616A', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=350,
            yaxis=dict(title='Revenue ($M)', side='left'),
            yaxis2=dict(title='Cloud Cost as % of Revenue', side='right', overlaying='y'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        **📈 Key Insight**: Cloud cost ratio improved from 19.4% to 17.9% over 6 months, 
        demonstrating increasing efficiency as revenue grows faster than infrastructure costs.
        """)
    
    # ==================== FINOPS TAB 9: SUSTAINABILITY ====================
    with finops_tab9:
        st.subheader("🌱 Sustainability & Carbon Footprint")
        
        st.markdown("""
        **Track and reduce your cloud carbon footprint** - Monitor CO2 emissions, 
        optimize for sustainability, and support ESG reporting requirements.
        """)
        
        # Sustainability metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Monthly CO2e", "847 tons", "-12% MoM")
        with col2:
            st.metric("Carbon Intensity", "0.32 kg/$ ", "-8% improved")
        with col3:
            st.metric("Renewable Energy", "67%", "+5% (AWS regions)")
        with col4:
            st.metric("Sustainability Score", "B+", "↑ from B")
        
        st.markdown("---")
        
        # Carbon emissions trend
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Carbon Emissions Trend")
            
            dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
            emissions = [1050, 1020, 980, 960, 940, 920, 900, 880, 870, 860, 850, 847]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=emissions,
                name='CO2e Emissions (tons)',
                line=dict(color='#A3BE8C', width=3),
                fill='tozeroy',
                fillcolor='rgba(163, 190, 140, 0.3)'
            ))
            
            fig.add_hline(y=750, line_dash="dash", line_color="#88C0D0", 
                         annotation_text="2025 Target: 750 tons")
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                yaxis_title='CO2e (metric tons)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 2025 Goals")
            
            goals = [
                ("Reduce emissions 25%", "847 → 750 tons", "67%"),
                ("100% renewable regions", "67% → 100%", "67%"),
                ("Carbon neutral by 2026", "In progress", "45%")
            ]
            
            for goal, detail, progress in goals:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0;'>
                    <strong>{goal}</strong><br/>
                    <small>{detail}</small>
                    <div style='background: #4C566A; border-radius: 3px; height: 8px; margin-top: 5px;'>
                        <div style='background: #A3BE8C; width: {progress}; height: 100%; border-radius: 3px;'></div>
                    </div>
                    <small style='color: #88C0D0;'>{progress} complete</small>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Emissions by service
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Emissions by Service")
            
            services = ['EC2', 'RDS', 'S3', 'SageMaker', 'Data Transfer', 'Other']
            service_emissions = [380, 180, 85, 120, 52, 30]
            
            fig = go.Figure(data=[go.Pie(
                labels=services,
                values=service_emissions,
                hole=0.4,
                marker_colors=['#BF616A', '#D08770', '#EBCB8B', '#A3BE8C', '#88C0D0', '#5E81AC'],
                textinfo='label+percent',
                textfont=dict(color='#FFFFFF')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Emissions by Region")
            
            regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
            region_emissions = [420, 210, 140, 77]
            renewable_pct = [52, 85, 78, 45]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=regions, y=region_emissions,
                name='CO2e (tons)',
                marker_color=['#D08770', '#A3BE8C', '#88C0D0', '#EBCB8B'],
                text=[f'{e} tons' for e in region_emissions],
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            ))
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                yaxis_title='CO2e (tons)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Green optimization recommendations
        st.markdown("### 🌿 Green Optimization Recommendations")
        
        green_recommendations = [
            ("Migrate us-east-1 workloads to us-west-2", "-85 tons/month", "🟢 High Impact",
             "us-west-2 has 85% renewable energy vs 52% in us-east-1"),
            ("Right-size over-provisioned EC2", "-42 tons/month", "🟢 High Impact",
             "Reduce compute waste and associated emissions"),
            ("Enable S3 Intelligent-Tiering", "-12 tons/month", "🟡 Medium Impact",
             "Reduce storage footprint and energy consumption"),
            ("Optimize SageMaker training jobs", "-28 tons/month", "🟢 High Impact",
             "Use Spot instances and efficient instance types"),
            ("Consolidate data transfer paths", "-8 tons/month", "🟡 Medium Impact",
             "Reduce cross-region data movement")
        ]
        
        for rec, impact, priority, detail in green_recommendations:
            color = "#A3BE8C" if "High" in priority else "#EBCB8B"
            st.markdown(f"""
            <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid {color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <strong>{rec}</strong>
                    <span style='color: #A3BE8C;'>{impact}</span>
                </div>
                <small>{priority} | {detail}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.success("""
        **🌍 Total Potential Reduction: 175 tons/month (21% of current emissions)**
        
        Implementing all recommendations would put you on track for 2025 sustainability goals.
        """)
        
        st.markdown("---")
        
        # ESG Report Export
        st.markdown("### 📄 ESG Reporting")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate ESG Report", use_container_width=True, type="primary"):
                st.success("✅ ESG report generated for Q4 2024")
        
        with col2:
            if st.button("📥 Export Carbon Data", use_container_width=True):
                st.success("✅ Downloaded carbon_footprint_2024.csv")
        
        with col3:
            if st.button("📧 Send to Sustainability Team", use_container_width=True):
                st.success("✅ Report sent to sustainability@company.com")
    
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
    compliance_tab1, compliance_tab2, compliance_tab3, compliance_tab4, compliance_tab5, compliance_tab6 = st.tabs([
        "📊 Account Compliance Overview",
        "⚙️ AWS Config Rules",
        "🔍 Security Hub Findings",
        "🦠 Vulnerability Management",
        "🏷️ Tagging Governance",
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
                hole=0.4,
                textinfo='percent',
                textfont=dict(color='#FFFFFF', size=11),
                insidetextfont=dict(color='#FFFFFF'),
                outsidetextfont=dict(color='#FFFFFF')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=250,
                showlegend=True,
                title=dict(text='Container Vulnerabilities', font=dict(color='#FFFFFF')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#FFFFFF', size=11)),
                font=dict(color='#FFFFFF')
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
    
    # ==================== COMPLIANCE TAB 5: TAGGING GOVERNANCE ====================
    with compliance_tab5:
        st.subheader("🏷️ Tagging Governance & Policy Enforcement")
        
        st.markdown("""
        **Enterprise-wide tag management** - Policy enforcement, compliance monitoring, 
        cost allocation accuracy, and automated remediation across 640+ AWS accounts.
        """)
        
        # Tagging metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Resources", "156,847", "Across 640 accounts")
        with col2:
            st.metric("Tag Compliance", "94.2%", "+2.1% this month")
        with col3:
            st.metric("Fully Tagged", "147,823", "All required tags")
        with col4:
            st.metric("Missing Tags", "9,024", "-1,234 remediated")
        with col5:
            st.metric("Cost Allocation", "96.8%", "Attributable spend")
        with col6:
            st.metric("Auto-Remediated", "3,456", "This month")
        
        st.markdown("---")
        
        # Tagging sub-tabs
        tag_tab1, tag_tab2, tag_tab3, tag_tab4, tag_tab5 = st.tabs([
            "📊 Compliance Dashboard",
            "📋 Tag Policies",
            "⚠️ Violations",
            "🔧 Auto-Remediation",
            "💰 Cost Allocation"
        ])
        
        with tag_tab1:
            st.markdown("### 📊 Tag Compliance Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Compliance by Required Tag")
                
                required_tags = ['Environment', 'CostCenter', 'Owner', 'Application', 'Portfolio', 'DataClassification']
                compliance_pct = [98.5, 96.2, 94.8, 92.1, 97.3, 88.4]
                
                fig = go.Figure(data=[go.Bar(
                    x=required_tags,
                    y=compliance_pct,
                    marker_color=['#A3BE8C' if c >= 95 else '#EBCB8B' if c >= 90 else '#BF616A' for c in compliance_pct],
                    text=[f'{c}%' for c in compliance_pct],
                    textposition='outside',
                    textfont=dict(color='#FFFFFF')
                )])
                
                fig.add_hline(y=95, line_dash="dash", line_color="#A3BE8C", annotation_text="Target: 95%")
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    yaxis_title='Compliance %',
                    yaxis_range=[0, 105],
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Compliance by Resource Type")
                
                resource_types = ['EC2', 'RDS', 'S3', 'Lambda', 'EBS', 'EKS', 'Other']
                type_compliance = [96.2, 94.8, 98.1, 89.3, 92.4, 95.7, 91.2]
                resource_counts = [12450, 2340, 8920, 45670, 23450, 890, 62127]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Compliance %',
                    x=resource_types,
                    y=type_compliance,
                    marker_color='#88C0D0',
                    text=[f'{c}%' for c in type_compliance],
                    textposition='outside',
                    textfont=dict(color='#FFFFFF'),
                    yaxis='y'
                ))
                
                fig.add_trace(go.Scatter(
                    name='Resource Count',
                    x=resource_types,
                    y=resource_counts,
                    mode='lines+markers',
                    line=dict(color='#A3BE8C', width=2),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    yaxis=dict(title='Compliance %', range=[0, 105]),
                    yaxis2=dict(title='Resource Count', overlaying='y', side='right'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Compliance by portfolio
            st.markdown("#### Compliance by Portfolio")
            
            portfolio_compliance = pd.DataFrame({
                'Portfolio': ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Management', 'Shared Services'],
                'Resources': [28450, 24320, 18920, 22670, 19450, 43037],
                'Compliant': [27856, 23105, 18541, 21987, 18563, 41234],
                'Non-Compliant': [594, 1215, 379, 683, 887, 1803],
                'Compliance %': ['97.9%', '95.0%', '98.0%', '97.0%', '95.4%', '95.8%'],
                'Trend': ['↑ +0.5%', '↑ +1.2%', '↔ 0%', '↑ +0.3%', '↓ -0.2%', '↑ +0.8%']
            })
            
            st.dataframe(portfolio_compliance, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Compliance trend
            st.markdown("#### Compliance Trend (12 Months)")
            
            months = pd.date_range(end=datetime.now(), periods=12, freq='M')
            overall_compliance = [87.2, 88.5, 89.1, 90.3, 91.2, 91.8, 92.4, 93.1, 93.5, 93.8, 94.0, 94.2]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=months, y=overall_compliance,
                mode='lines+markers',
                line=dict(color='#A3BE8C', width=3),
                fill='tozeroy',
                fillcolor='rgba(163, 190, 140, 0.2)',
                name='Overall Compliance'
            ))
            
            fig.add_hline(y=95, line_dash="dash", line_color="#EBCB8B", annotation_text="Target: 95%")
            
            fig.update_layout(
                template='plotly_dark',
                height=300,
                yaxis_title='Compliance %',
                yaxis_range=[80, 100],
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tag_tab2:
            st.markdown("### 📋 Tag Policies & Standards")
            
            st.markdown("#### Required Tags (Organization-Wide)")
            
            required_tag_policies = [
                {
                    "tag": "Environment",
                    "description": "Deployment environment",
                    "allowed_values": "Production, Staging, Development, Sandbox, DR",
                    "enforcement": "Strict",
                    "scope": "All resources"
                },
                {
                    "tag": "CostCenter",
                    "description": "Financial cost allocation",
                    "allowed_values": "CC-XXXX format (e.g., CC-1001)",
                    "enforcement": "Strict",
                    "scope": "All resources"
                },
                {
                    "tag": "Owner",
                    "description": "Resource owner email",
                    "allowed_values": "Valid company email",
                    "enforcement": "Strict",
                    "scope": "All resources"
                },
                {
                    "tag": "Application",
                    "description": "Application identifier",
                    "allowed_values": "APP-XXXX format",
                    "enforcement": "Strict",
                    "scope": "All resources"
                },
                {
                    "tag": "Portfolio",
                    "description": "Business portfolio",
                    "allowed_values": "Digital Banking, Insurance, Payments, Capital Markets, Wealth Management, Shared Services",
                    "enforcement": "Strict",
                    "scope": "All resources"
                },
                {
                    "tag": "DataClassification",
                    "description": "Data sensitivity level",
                    "allowed_values": "Public, Internal, Confidential, Restricted",
                    "enforcement": "Strict",
                    "scope": "Data resources (S3, RDS, DynamoDB)"
                },
            ]
            
            for policy in required_tag_policies:
                enforcement_color = "#A3BE8C" if policy['enforcement'] == "Strict" else "#EBCB8B"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid {enforcement_color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong style='font-size: 1.1rem; color: #88C0D0;'>{policy['tag']}</strong>
                        <span style='background: {enforcement_color}; color: #2E3440; padding: 2px 10px; border-radius: 10px; font-size: 0.8rem;'>{policy['enforcement']}</span>
                    </div>
                    <p style='margin: 0.5rem 0 0 0; color: #D8DEE9;'>{policy['description']}</p>
                    <small style='color: #88C0D0;'><strong>Allowed:</strong> {policy['allowed_values']}</small><br/>
                    <small style='color: #A3BE8C;'><strong>Scope:</strong> {policy['scope']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### AWS Tag Policies (Organization SCPs)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Active Tag Policies")
                
                active_policies = [
                    ("RequireEnvironmentTag", "All OUs", "✅ Active"),
                    ("RequireCostCenterTag", "All OUs", "✅ Active"),
                    ("RequireOwnerTag", "Production OU", "✅ Active"),
                    ("EnforceTagValues", "All OUs", "✅ Active"),
                    ("RequireDataClassification", "Data OU", "✅ Active"),
                ]
                
                for policy, scope, status in active_policies:
                    st.markdown(f"""
                    <div style='background: #2E3440; padding: 0.5rem 1rem; border-radius: 5px; margin: 0.3rem 0;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong>{policy}</strong>
                            <span style='color: #A3BE8C;'>{status}</span>
                        </div>
                        <small style='color: #88C0D0;'>Scope: {scope}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("##### Policy Actions")
                
                if st.button("➕ Create New Tag Policy", use_container_width=True):
                    st.info("📝 Opening tag policy editor...")
                
                if st.button("📋 Export Policy Report", use_container_width=True):
                    st.success("✅ Downloaded tag_policies_report.json")
                
                if st.button("🔄 Sync with AWS Organizations", use_container_width=True):
                    st.success("✅ Tag policies synced successfully")
                
                if st.button("📊 View Policy Effectiveness", use_container_width=True):
                    st.info("📈 Generating effectiveness report...")
        
        with tag_tab3:
            st.markdown("### ⚠️ Tag Violations")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Violations", "9,024", "-1,234 this week")
            with col2:
                st.metric("Critical (Prod)", "456", "Missing required tags")
            with col3:
                st.metric("Invalid Values", "1,234", "Non-compliant values")
            with col4:
                st.metric("Orphaned Resources", "567", "No owner tag")
            
            st.markdown("---")
            
            # Filter controls
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                viol_tag = st.selectbox("Tag", ["All Tags", "Environment", "CostCenter", "Owner", "Application", "DataClassification"])
            with col2:
                viol_type = st.selectbox("Violation Type", ["All", "Missing Tag", "Invalid Value", "Case Mismatch"])
            with col3:
                viol_portfolio = st.selectbox("Portfolio", ["All", "Digital Banking", "Insurance", "Payments", "Capital Markets"])
            with col4:
                viol_severity = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
            
            st.markdown("---")
            
            # Violations table
            violations = []
            resource_types_v = ['EC2', 'RDS', 'S3', 'Lambda', 'EBS']
            missing_tags_v = ['CostCenter', 'Owner', 'Environment', 'Application', 'DataClassification']
            
            for i in range(20):
                res_type = random.choice(resource_types_v)
                violations.append({
                    'Resource ID': f"{res_type.lower()}-{random.randint(10000, 99999)}",
                    'Resource Type': res_type,
                    'Account': f"prod-{random.choice(['banking', 'payments', 'insurance'])}-{random.randint(1,99):03d}",
                    'Missing/Invalid Tag': random.choice(missing_tags_v),
                    'Violation Type': random.choice(['Missing', 'Missing', 'Invalid Value', 'Case Mismatch']),
                    'Age': f"{random.randint(1, 90)} days",
                    'Severity': random.choice(['🔴 Critical', '🟠 High', '🟡 Medium', '🟢 Low']),
                    'Est. Cost Impact': f"${random.randint(10, 500)}/mo"
                })
            
            df_violations = pd.DataFrame(violations)
            st.dataframe(df_violations, use_container_width=True, hide_index=True, height=400)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔧 Auto-Remediate Selected", type="primary", use_container_width=True):
                    st.success("✅ Initiated remediation for selected resources")
            with col2:
                if st.button("📧 Notify Resource Owners", use_container_width=True):
                    st.success("✅ Notifications sent to 45 owners")
            with col3:
                if st.button("📥 Export Violations", use_container_width=True):
                    st.success("✅ Downloaded tag_violations.csv")
        
        with tag_tab4:
            st.markdown("### 🔧 Auto-Remediation Engine")
            
            st.markdown("""
            **Automated tag remediation** using AI-powered inference and rule-based defaults 
            to automatically fix missing or invalid tags.
            """)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Auto-Remediated (MTD)", "3,456", "+892 this week")
            with col2:
                st.metric("Success Rate", "98.7%", "+0.3%")
            with col3:
                st.metric("Pending Review", "123", "AI-uncertain")
            with col4:
                st.metric("Time Saved", "847 hours", "This month")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Remediation Rules")
                
                rules = [
                    ("Environment Tag", "Infer from account name/OU", "✅ Enabled", "98.5%"),
                    ("CostCenter Tag", "Map from account metadata", "✅ Enabled", "97.2%"),
                    ("Owner Tag", "Lookup from resource creator", "✅ Enabled", "94.8%"),
                    ("Application Tag", "Infer from resource naming", "✅ Enabled", "89.3%"),
                    ("Portfolio Tag", "Map from OU structure", "✅ Enabled", "99.1%"),
                    ("DataClassification", "AI content analysis", "⚠️ Review mode", "87.4%"),
                ]
                
                for rule, method, status, accuracy in rules:
                    status_color = "#A3BE8C" if "Enabled" in status else "#EBCB8B"
                    st.markdown(f"""
                    <div style='background: #2E3440; padding: 0.7rem 1rem; border-radius: 5px; margin: 0.3rem 0;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <strong>{rule}</strong>
                            <span style='color: {status_color};'>{status}</span>
                        </div>
                        <small style='color: #88C0D0;'>Method: {method} | Accuracy: {accuracy}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Recent Auto-Remediations")
                
                recent_remediations = [
                    ("ec2-45678", "Environment=Production", "Inferred from OU", "2 min ago"),
                    ("rds-12345", "CostCenter=CC-1001", "Account mapping", "5 min ago"),
                    ("s3-bucket-xyz", "Owner=jane.doe@co.com", "Creator lookup", "8 min ago"),
                    ("lambda-func-01", "Application=APP-2345", "Name pattern", "12 min ago"),
                    ("ebs-vol-789", "Portfolio=Payments", "OU structure", "15 min ago"),
                ]
                
                for resource, tag_applied, method, when in recent_remediations:
                    st.markdown(f"""
                    <div style='background: #2E3440; padding: 0.5rem 1rem; border-radius: 5px; margin: 0.3rem 0; border-left: 3px solid #A3BE8C;'>
                        <code>{resource}</code><br/>
                        <span style='color: #A3BE8C;'>+ {tag_applied}</span><br/>
                        <small style='color: #88C0D0;'>{method} | {when}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### 🤖 AI-Powered Tag Inference")
            
            st.info("""
            **Claude-Powered Tag Analysis**
            
            When rule-based remediation cannot determine a tag value with high confidence, 
            Claude AI analyzes:
            
            - Resource naming patterns and conventions
            - Associated resources and their tags
            - CloudTrail activity and resource creators
            - Cost allocation patterns
            - Network topology and VPC associations
            
            **Current Queue**: 123 resources pending AI review
            
            **Confidence Threshold**: 90% (below this, tags are queued for human review)
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 Run AI Analysis on Queue", type="primary", use_container_width=True):
                    st.success("✅ AI analysis started for 123 resources")
            with col2:
                if st.button("📋 Review AI Suggestions", use_container_width=True):
                    st.info("📝 Opening review queue...")
        
        with tag_tab5:
            st.markdown("### 💰 Cost Allocation & Attribution")
            
            st.markdown("""
            **Tag-based cost allocation accuracy** - Ensure every dollar of cloud spend 
            is properly attributed to business units, applications, and cost centers.
            """)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Monthly Spend", "$2.8M", "100%")
            with col2:
                st.metric("Allocated Spend", "$2.71M", "96.8%")
            with col3:
                st.metric("Unallocated", "$89K", "3.2%")
            with col4:
                st.metric("Allocation Accuracy", "96.8%", "+1.2% this month")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Cost Allocation by Tag")
                
                allocation_tags = ['CostCenter', 'Portfolio', 'Application', 'Environment', 'Owner']
                allocation_pct = [96.8, 97.2, 92.4, 98.5, 94.2]
                unallocated = [89000, 78000, 212000, 42000, 162000]
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=allocation_tags,
                    y=allocation_pct,
                    marker_color=['#A3BE8C' if p >= 95 else '#EBCB8B' if p >= 90 else '#BF616A' for p in allocation_pct],
                    text=[f'{p}%' for p in allocation_pct],
                    textposition='outside',
                    textfont=dict(color='#FFFFFF')
                ))
                
                fig.add_hline(y=95, line_dash="dash", line_color="#A3BE8C", annotation_text="Target: 95%")
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    yaxis_title='Allocation %',
                    yaxis_range=[0, 105],
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Unallocated Spend by Service")
                
                services_unalloc = ['EC2', 'RDS', 'S3', 'Data Transfer', 'Other']
                unalloc_amounts = [34000, 22000, 12000, 15000, 6000]
                
                fig = go.Figure(data=[go.Pie(
                    labels=services_unalloc,
                    values=unalloc_amounts,
                    hole=0.4,
                    marker_colors=['#BF616A', '#D08770', '#EBCB8B', '#88C0D0', '#5E81AC'],
                    textinfo='label+percent',
                    textfont=dict(color='#FFFFFF')
                )])
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    annotations=[dict(text=f'${sum(unalloc_amounts)/1000:.0f}K', x=0.5, y=0.5, font_size=20, font_color='#FFFFFF', showarrow=False)]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("#### 📋 Unallocated Resources (Top Impact)")
            
            unallocated_resources = []
            for i in range(10):
                unallocated_resources.append({
                    'Resource': f"{random.choice(['ec2', 'rds', 's3'])}-{random.randint(10000, 99999)}",
                    'Account': f"prod-{random.choice(['banking', 'payments', 'insurance'])}-{random.randint(1,99):03d}",
                    'Monthly Cost': f"${random.randint(500, 5000):,}",
                    'Missing Tags': random.choice(['CostCenter', 'CostCenter, Owner', 'Application', 'Portfolio']),
                    'Age': f"{random.randint(7, 90)} days",
                    'Suggested Action': random.choice(['Auto-tag', 'Owner review', 'AI inference'])
                })
            
            st.dataframe(pd.DataFrame(unallocated_resources), use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔧 Auto-Tag High-Impact Resources", type="primary", use_container_width=True):
                    st.success("✅ Auto-tagging initiated for 45 resources")
            with col2:
                if st.button("📧 Send Owner Notifications", use_container_width=True):
                    st.success("✅ Sent to 23 resource owners")
            with col3:
                if st.button("📊 Generate Allocation Report", use_container_width=True):
                    st.success("✅ Report generated for Finance team")
    
    with compliance_tab6:
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
    fig.update_layout(
        template='plotly_dark', 
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        legend=dict(font=dict(color='#FFFFFF')),
        xaxis=dict(tickfont=dict(color='#FFFFFF'), title=dict(font=dict(color='#FFFFFF'))),
        yaxis=dict(tickfont=dict(color='#FFFFFF'), title=dict(font=dict(color='#FFFFFF')))
    )
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
    sec_tab1, sec_tab2, sec_tab3, sec_tab4, sec_tab5 = st.tabs([
        "🔍 Active Threats",
        "🛠️ Remediation Queue",
        "📊 Security Dashboard",
        "🔐 IAM Analytics",
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
            title=dict(text='Security Threats: Detection vs Remediation (30 days)', font=dict(color='#FFFFFF')),
            height=400,
            legend=dict(font=dict(color='#FFFFFF', size=12)),
            font=dict(color='#FFFFFF'),
            xaxis=dict(title=dict(text='Date', font=dict(color='#FFFFFF')), tickfont=dict(color='#FFFFFF')),
            yaxis=dict(title=dict(text='Count', font=dict(color='#FFFFFF')), tickfont=dict(color='#FFFFFF'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Threat breakdown by type
        col1, col2 = st.columns(2)
        with col1:
            threat_counts = {'S3 Exposure': 23, 'IAM Issues': 45, 'Unpatched': 18, 'Credentials': 12, 'Network': 8}
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(threat_counts.keys()), 
                values=list(threat_counts.values()),
                hole=.4,
                textinfo='percent',
                textfont=dict(color='#FFFFFF', size=11),
                insidetextfont=dict(color='#FFFFFF'),
                outsidetextfont=dict(color='#FFFFFF')
            )])
            fig_pie.update_layout(
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title=dict(text='Threats by Category', font=dict(color='#FFFFFF')),
                legend=dict(font=dict(color='#FFFFFF', size=11)),
                font=dict(color='#FFFFFF')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("#### Security Health by Service")
            services = ['EC2', 'S3', 'IAM', 'RDS', 'Lambda', 'EKS']
            for svc in services:
                score = random.randint(85, 100)
                color = '#00FF88' if score >= 95 else '#FFD700' if score >= 85 else '#FF4444'
                st.markdown(f"**{svc}**: {score}% secure")
                st.progress(score/100)
    
    # ==================== SEC TAB 4: IAM ANALYTICS ====================
    with sec_tab4:
        st.subheader("🔐 IAM Analytics & Access Intelligence")
        
        st.markdown("""
        **Comprehensive IAM analysis** - Permission insights, least privilege scoring, 
        cross-account access mapping, and credential hygiene across 640+ AWS accounts.
        """)
        
        # IAM Metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total IAM Users", "2,847", "+23 this month")
        with col2:
            st.metric("IAM Roles", "12,456", "+156")
        with col3:
            st.metric("Service Accounts", "847", "+12")
        with col4:
            st.metric("Least Privilege Score", "72%", "+3%")
        with col5:
            st.metric("Unused Credentials", "234", "-45 cleaned")
        with col6:
            st.metric("Policy Violations", "89", "-23 fixed")
        
        st.markdown("---")
        
        # IAM Sub-tabs
        iam_tab1, iam_tab2, iam_tab3, iam_tab4, iam_tab5 = st.tabs([
            "📊 Permission Analysis",
            "🎯 Least Privilege",
            "🔗 Cross-Account Access",
            "🔑 Credential Hygiene",
            "⚠️ IAM Risks"
        ])
        
        with iam_tab1:
            st.markdown("### 📊 Permission Analysis Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Permission Distribution by Type")
                
                perm_types = ['Admin Access', 'Power User', 'Read/Write', 'Read Only', 'Custom Limited']
                perm_counts = [45, 234, 567, 1245, 756]
                perm_colors = ['#BF616A', '#D08770', '#EBCB8B', '#A3BE8C', '#88C0D0']
                
                fig = go.Figure(data=[go.Pie(
                    labels=perm_types,
                    values=perm_counts,
                    hole=0.4,
                    marker_colors=perm_colors,
                    textinfo='label+percent',
                    textfont=dict(color='#FFFFFF')
                )])
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(font=dict(color='#FFFFFF'))
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### High-Risk Permissions")
                
                high_risk_perms = [
                    ("iam:*", "45 principals", "🔴 Critical", "Full IAM control"),
                    ("s3:*", "234 principals", "🟠 High", "Full S3 access"),
                    ("ec2:*", "189 principals", "🟠 High", "Full EC2 control"),
                    ("*:*", "12 principals", "🔴 Critical", "Full admin access"),
                    ("kms:Decrypt", "567 principals", "🟡 Medium", "Can decrypt all KMS keys"),
                    ("sts:AssumeRole", "1,245 principals", "🟡 Medium", "Cross-account capable"),
                ]
                
                for perm, count, severity, desc in high_risk_perms:
                    sev_color = "#BF616A" if "Critical" in severity else "#D08770" if "High" in severity else "#EBCB8B"
                    st.markdown(f"""
                    <div style='background: #2E3440; padding: 0.6rem; border-radius: 5px; margin: 0.3rem 0; border-left: 3px solid {sev_color};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <code style='color: #88C0D0;'>{perm}</code>
                            <span style='color: {sev_color};'>{severity}</span>
                        </div>
                        <small>{count} | {desc}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### 📋 Overprivileged Principals (Top 20)")
            
            overprivileged = []
            for i in range(15):
                principal_type = random.choice(['User', 'Role', 'Role', 'Role'])
                overprivileged.append({
                    'Principal': f"{'user/' if principal_type == 'User' else 'role/'}{random.choice(['admin', 'developer', 'svc', 'lambda'])}-{random.choice(['prod', 'dev', 'deploy'])}-{random.randint(1,99):02d}",
                    'Type': principal_type,
                    'Account': f"prod-{random.choice(['banking', 'payments', 'insurance'])}-{random.randint(1,99):03d}",
                    'Permissions': random.randint(50, 500),
                    'Used (30d)': random.randint(5, 50),
                    'Unused %': f"{random.randint(60, 95)}%",
                    'Risk Score': random.choice(['🔴 Critical', '🟠 High', '🟠 High', '🟡 Medium'])
                })
            
            st.dataframe(pd.DataFrame(overprivileged), use_container_width=True, hide_index=True)
        
        with iam_tab2:
            st.markdown("### 🎯 Least Privilege Analysis")
            
            # Overall score
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style='text-align: center; background: #2E3440; padding: 2rem; border-radius: 10px;'>
                    <h1 style='color: #EBCB8B; font-size: 4rem; margin: 0;'>72%</h1>
                    <p style='color: #D8DEE9; font-size: 1.2rem;'>Organization Least Privilege Score</p>
                    <small style='color: #A3BE8C;'>↑ 3% improvement from last month</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Least Privilege Score by Portfolio")
                
                portfolios_lp = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Mgmt', 'Shared Services']
                lp_scores = [78, 65, 82, 71, 69, 75]
                
                fig = go.Figure(data=[go.Bar(
                    x=portfolios_lp,
                    y=lp_scores,
                    marker_color=['#A3BE8C' if s >= 75 else '#EBCB8B' if s >= 65 else '#BF616A' for s in lp_scores],
                    text=[f'{s}%' for s in lp_scores],
                    textposition='outside',
                    textfont=dict(color='#FFFFFF')
                )])
                
                fig.add_hline(y=80, line_dash="dash", line_color="#A3BE8C", annotation_text="Target: 80%")
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    yaxis_title='Least Privilege Score (%)',
                    yaxis_range=[0, 100],
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Score Trend (6 Months)")
                
                months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
                scores = [58, 62, 65, 68, 69, 72]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=months, y=scores,
                    mode='lines+markers',
                    line=dict(color='#A3BE8C', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(163, 190, 140, 0.2)'
                ))
                
                fig.add_hline(y=80, line_dash="dash", line_color="#EBCB8B", annotation_text="Target: 80%")
                
                fig.update_layout(
                    template='plotly_dark',
                    height=350,
                    yaxis_title='Score (%)',
                    yaxis_range=[0, 100],
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("#### 🤖 AI-Recommended Permission Reductions")
            
            recommendations = [
                ("role/lambda-data-processor-prod", "Remove s3:DeleteBucket", "Never used in 90 days", "🟢 Safe to remove", "$0 impact"),
                ("role/ecs-task-payments-01", "Scope down ec2:* to ec2:Describe*", "Only read operations used", "🟢 Safe to remove", "$0 impact"),
                ("user/developer-john-smith", "Remove iam:CreateUser", "Used once 180 days ago", "🟡 Review first", "Low risk"),
                ("role/glue-etl-insurance", "Remove kms:* - scope to specific keys", "Only 2 keys accessed", "🟢 Safe to remove", "$0 impact"),
                ("role/sagemaker-training-ml", "Remove s3:* - scope to ml-* buckets", "Only ML buckets accessed", "🟢 Safe to remove", "$0 impact"),
            ]
            
            for principal, action, reason, safety, impact in recommendations:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong><code>{principal}</code></strong>
                        <span>{safety}</span>
                    </div>
                    <div style='margin: 0.5rem 0;'>
                        <span style='color: #BF616A;'>Action: {action}</span>
                    </div>
                    <small style='color: #88C0D0;'>Reason: {reason} | Impact: {impact}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚀 Apply All Safe Recommendations", type="primary"):
                st.success("✅ Applied 4 permission reductions. Estimated score improvement: +5%")
        
        with iam_tab3:
            st.markdown("### 🔗 Cross-Account Access Map")
            
            st.markdown("""
            **Visualize and manage cross-account IAM trust relationships** across your 640+ AWS accounts.
            """)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Cross-Account Roles", "1,847", "Trust relationships")
            with col2:
                st.metric("External Trusts", "23", "3rd party access")
            with col3:
                st.metric("Circular Trusts", "4", "⚠️ Review needed")
            with col4:
                st.metric("Unused Trusts", "156", "90+ days inactive")
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Trust Relationship Matrix (Top Accounts)")
                
                # Create a heatmap-style matrix
                accounts_matrix = ['banking-prod', 'payments-prod', 'insurance-prod', 'data-lake', 'security-hub', 'shared-svc']
                trust_matrix = np.random.randint(0, 15, size=(6, 6))
                np.fill_diagonal(trust_matrix, 0)
                
                fig = go.Figure(data=go.Heatmap(
                    z=trust_matrix,
                    x=accounts_matrix,
                    y=accounts_matrix,
                    colorscale='Blues',
                    text=trust_matrix,
                    texttemplate='%{text}',
                    textfont=dict(color='white'),
                    hovertemplate='From: %{y}<br>To: %{x}<br>Roles: %{z}<extra></extra>'
                ))
                
                fig.update_layout(
                    template='plotly_dark',
                    height=400,
                    xaxis_title='Trusting Account',
                    yaxis_title='Trusted Account',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### ⚠️ High-Risk Trusts")
                
                risky_trusts = [
                    ("External: AWS Support", "🟡 Vendor access"),
                    ("External: Datadog", "🟡 Monitoring"),
                    ("External: Unknown-12345", "🔴 Investigate"),
                    ("Circular: A→B→C→A", "🟠 Complexity risk"),
                ]
                
                for trust, risk in risky_trusts:
                    color = "#BF616A" if "🔴" in risk else "#D08770" if "🟠" in risk else "#EBCB8B"
                    st.markdown(f"""
                    <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 3px solid {color};'>
                        <strong>{trust}</strong><br/>
                        <small style='color: {color};'>{risk}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                st.markdown("#### 📊 Trust by Type")
                st.markdown("""
                - **Internal Production**: 892 roles
                - **Internal Dev/Test**: 634 roles  
                - **Shared Services**: 298 roles
                - **External Vendors**: 23 roles
                """)
            
            st.markdown("---")
            
            st.markdown("#### 📋 Cross-Account Role Details")
            
            cross_account_roles = []
            for i in range(12):
                cross_account_roles.append({
                    'Role Name': f"cross-account-{random.choice(['read', 'admin', 'deploy', 'audit'])}-{random.randint(1,99):02d}",
                    'Source Account': f"prod-{random.choice(['banking', 'payments', 'insurance'])}-{random.randint(1,50):03d}",
                    'Target Account': f"prod-{random.choice(['data-lake', 'security', 'shared'])}-{random.randint(1,20):03d}",
                    'Trust Type': random.choice(['Internal', 'Internal', 'Internal', 'External']),
                    'Last Used': f"{random.randint(1, 90)} days ago",
                    'Sessions (30d)': random.randint(0, 500),
                    'Risk': random.choice(['🟢 Low', '🟢 Low', '🟡 Medium', '🟠 High'])
                })
            
            st.dataframe(pd.DataFrame(cross_account_roles), use_container_width=True, hide_index=True)
        
        with iam_tab4:
            st.markdown("### 🔑 Credential Hygiene Dashboard")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Active Access Keys", "1,234", "IAM users")
            with col2:
                st.metric("Keys > 90 days", "456", "🟡 Rotate soon")
            with col3:
                st.metric("Keys > 180 days", "123", "🔴 Critical")
            with col4:
                st.metric("Unused Keys", "234", "Ready to delete")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Access Key Age Distribution")
                
                age_ranges = ['< 30 days', '30-90 days', '90-180 days', '180-365 days', '> 365 days']
                key_counts = [345, 433, 289, 123, 44]
                colors = ['#A3BE8C', '#88C0D0', '#EBCB8B', '#D08770', '#BF616A']
                
                fig = go.Figure(data=[go.Bar(
                    x=age_ranges,
                    y=key_counts,
                    marker_color=colors,
                    text=key_counts,
                    textposition='outside',
                    textfont=dict(color='#FFFFFF')
                )])
                
                fig.update_layout(
                    template='plotly_dark',
                    height=300,
                    yaxis_title='Number of Keys',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Password Policy Compliance")
                
                policies = ['Min Length 14+', 'Uppercase Required', 'Numbers Required', 
                           'Symbols Required', 'MFA Enabled', 'Max Age 90 days']
                compliance = [98, 99, 99, 95, 87, 78]
                
                for policy, pct in zip(policies, compliance):
                    color = '#A3BE8C' if pct >= 95 else '#EBCB8B' if pct >= 85 else '#BF616A'
                    st.markdown(f"""
                    <div style='margin: 0.3rem 0;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>{policy}</span>
                            <span style='color: {color};'>{pct}%</span>
                        </div>
                        <div style='background: #4C566A; border-radius: 3px; height: 6px;'>
                            <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 3px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("#### 🔴 Credentials Requiring Immediate Action")
            
            urgent_creds = [
                ("user/svc-legacy-etl", "Access key 478 days old", "🔴 Critical", "Rotate immediately"),
                ("user/admin-contractor-01", "No MFA enabled", "🔴 Critical", "Enable MFA"),
                ("user/developer-jane-doe", "Password 245 days old", "🟠 High", "Force password reset"),
                ("user/svc-monitoring", "2 active keys (should be 1)", "🟡 Medium", "Delete unused key"),
                ("user/api-integration-prod", "Key unused 120 days", "🟡 Medium", "Verify or delete"),
            ]
            
            for principal, issue, severity, action in urgent_creds:
                sev_color = "#BF616A" if "Critical" in severity else "#D08770" if "High" in severity else "#EBCB8B"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.4rem 0; border-left: 4px solid {sev_color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong><code>{principal}</code></strong>
                        <span style='color: {sev_color};'>{severity}</span>
                    </div>
                    <div>Issue: {issue}</div>
                    <small style='color: #A3BE8C;'>Recommended: {action}</small>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Rotate All Critical Keys", type="primary", use_container_width=True):
                    st.success("✅ Initiated rotation for 123 critical access keys")
            with col2:
                if st.button("📧 Send Credential Reports", use_container_width=True):
                    st.success("✅ Reports sent to account owners")
        
        with iam_tab5:
            st.markdown("### ⚠️ IAM Risk Assessment")
            
            # Risk overview
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Critical Risks", "12", "Immediate action")
            with col2:
                st.metric("High Risks", "45", "This week")
            with col3:
                st.metric("Medium Risks", "156", "This month")
            with col4:
                st.metric("IAM Risk Score", "68/100", "+5 improved")
            
            st.markdown("---")
            
            st.markdown("#### 🔴 Critical IAM Risks")
            
            critical_risks = [
                {
                    "title": "Root Account Access Keys Exist",
                    "accounts": "3 accounts",
                    "detail": "Root access keys should never exist. Immediate deletion required.",
                    "remediation": "Delete root access keys, enable MFA on root"
                },
                {
                    "title": "Wildcard Principal in Resource Policies",
                    "accounts": "7 S3 buckets, 2 KMS keys",
                    "detail": "Resources accessible by any AWS principal (*)",
                    "remediation": "Restrict to specific accounts/principals"
                },
                {
                    "title": "IAM Users with Console + Programmatic Access",
                    "accounts": "23 users",
                    "detail": "Service accounts should not have console access",
                    "remediation": "Remove console access or convert to SSO"
                },
                {
                    "title": "Inactive IAM Users with Active Credentials",
                    "accounts": "45 users",
                    "detail": "Users not logged in 90+ days but credentials active",
                    "remediation": "Disable or delete inactive users"
                },
            ]
            
            for risk in critical_risks:
                st.markdown(f"""
                <div style='background: #3B1E1E; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #BF616A;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong style='color: #BF616A; font-size: 1.1rem;'>🔴 {risk['title']}</strong>
                        <span style='color: #D8DEE9;'>{risk['accounts']}</span>
                    </div>
                    <p style='margin: 0.5rem 0; color: #D8DEE9;'>{risk['detail']}</p>
                    <small style='color: #A3BE8C;'><strong>Remediation:</strong> {risk['remediation']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Risk Trend (6 Months)")
                
                months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
                critical = [18, 16, 15, 14, 13, 12]
                high = [67, 62, 58, 52, 48, 45]
                medium = [189, 178, 172, 168, 162, 156]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=critical, name='Critical', line=dict(color='#BF616A', width=2)))
                fig.add_trace(go.Scatter(x=months, y=high, name='High', line=dict(color='#D08770', width=2)))
                fig.add_trace(go.Scatter(x=months, y=medium, name='Medium', line=dict(color='#EBCB8B', width=2)))
                
                fig.update_layout(
                    template='plotly_dark',
                    height=300,
                    yaxis_title='Risk Count',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 🤖 Claude Risk Analysis")
                
                st.info("""
                **AI Risk Assessment Summary**
                
                Based on analysis of 640 accounts:
                
                **Top Concerns:**
                1. 3 root accounts have access keys (critical)
                2. 23% of roles have unused admin permissions
                3. Cross-account trust sprawl increasing
                
                **Positive Trends:**
                - MFA adoption up 12% (now 87%)
                - Key rotation compliance improving
                - Least privilege score trending up
                
                **Recommendation:**
                Focus on root account remediation and permission right-sizing this sprint.
                
                **Risk Reduction Potential:** 35% with recommended actions
                """)
    
    with sec_tab5:
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
            fig.update_layout(
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)',
                title=dict(text='Average Query Time (24h)', font=dict(color='#FFFFFF')), 
                height=300,
                font=dict(color='#FFFFFF'),
                legend=dict(font=dict(color='#FFFFFF')),
                xaxis=dict(tickfont=dict(color='#FFFFFF')),
                yaxis=dict(tickfont=dict(color='#FFFFFF'))
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Connection pool usage
            connections = {'prod-postgres-01': 78, 'prod-mysql-02': 45, 
                          'prod-aurora-03': 92, 'prod-dynamodb-main': 34}
            
            fig = go.Figure(data=[go.Bar(x=list(connections.keys()), 
                                        y=list(connections.values()),
                                        marker_color='#00FF88')])
            fig.update_layout(
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)',
                title=dict(text='Connection Pool Usage (%)', font=dict(color='#FFFFFF')), 
                height=300,
                font=dict(color='#FFFFFF'),
                xaxis=dict(tickfont=dict(color='#FFFFFF')),
                yaxis=dict(tickfont=dict(color='#FFFFFF'))
            )
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
                     annotation_text="Target: 95%", annotation_font_color="#FFFFFF")
        fig.update_layout(
            template='plotly_dark', 
            paper_bgcolor='rgba(0,0,0,0)',
            title=dict(text='Overall Policy Effectiveness (12 weeks)', font=dict(color='#FFFFFF')), 
            height=400,
            font=dict(color='#FFFFFF'),
            legend=dict(font=dict(color='#FFFFFF')),
            xaxis=dict(tickfont=dict(color='#FFFFFF')),
            yaxis=dict(tickfont=dict(color='#FFFFFF'))
        )
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

# ==================== TAB 11: ACCOUNT LIFECYCLE MANAGEMENT ====================
with tab11:
    st.header("🏗️ AWS Account Lifecycle Management")
    
    st.markdown("""
    **End-to-end account lifecycle management** - Streamlined onboarding, secure offboarding, 
    and comprehensive tracking across 640+ AWS accounts with automated provisioning via AWS Control Tower.
    """)
    
    # Create sub-tabs for Account Lifecycle
    lifecycle_tab1, lifecycle_tab2, lifecycle_tab3, lifecycle_tab4, lifecycle_tab5 = st.tabs([
        "📊 Overview",
        "🚀 Account Onboarding",
        "🔴 Account Offboarding", 
        "📋 Request Tracking",
        "📜 Account Inventory"
    ])
    
    # ==================== LIFECYCLE TAB 1: OVERVIEW ====================
    with lifecycle_tab1:
        st.subheader("📊 Account Lifecycle Dashboard")
        
        # Key metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total Accounts", "640", "+3 this month")
        with col2:
            st.metric("Active", "612", "95.6%")
        with col3:
            st.metric("Pending Onboard", "8", "In progress")
        with col4:
            st.metric("Pending Offboard", "4", "In progress")
        with col5:
            st.metric("Avg Onboard Time", "2.3 days", "-0.5 days")
        with col6:
            st.metric("Compliance Rate", "98.7%", "+0.3%")
        
        st.markdown("---")
        
        # Account distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Accounts by Environment")
            
            environments = ['Production', 'Development', 'Staging', 'Sandbox', 'DR', 'Security']
            env_counts = [127, 234, 89, 156, 12, 22]
            env_colors = ['#BF616A', '#A3BE8C', '#EBCB8B', '#88C0D0', '#B48EAD', '#5E81AC']
            
            fig = go.Figure(data=[go.Pie(
                labels=environments,
                values=env_counts,
                hole=0.4,
                marker_colors=env_colors,
                textinfo='label+value',
                textfont=dict(color='#FFFFFF')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#FFFFFF'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Accounts by Portfolio")
            
            portfolios = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Management', 'Shared Services']
            portfolio_counts = [145, 112, 98, 87, 76, 122]
            
            fig = go.Figure(data=[go.Bar(
                x=portfolios,
                y=portfolio_counts,
                marker_color=['#A3BE8C', '#88C0D0', '#EBCB8B', '#B48EAD', '#5E81AC', '#D08770'],
                text=portfolio_counts,
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            )])
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                yaxis_title='Number of Accounts',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Monthly account activity
        st.markdown("### 📈 Account Activity Trend (12 Months)")
        
        months = pd.date_range(end=datetime.now(), periods=12, freq='M')
        onboarded = [12, 15, 8, 22, 18, 14, 20, 16, 11, 19, 13, 8]
        offboarded = [3, 5, 2, 8, 4, 6, 3, 5, 2, 4, 3, 4]
        net_change = [o - off for o, off in zip(onboarded, offboarded)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=months, y=onboarded,
            name='Onboarded',
            marker_color='#A3BE8C'
        ))
        
        fig.add_trace(go.Bar(
            x=months, y=[-o for o in offboarded],
            name='Offboarded',
            marker_color='#BF616A'
        ))
        
        fig.add_trace(go.Scatter(
            x=months, y=net_change,
            name='Net Change',
            line=dict(color='#EBCB8B', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=350,
            barmode='relative',
            yaxis_title='Account Count',
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🆕 Recently Onboarded")
            
            recent_onboarded = [
                ("digital-banking-prod-089", "Digital Banking", "Production", "2 days ago"),
                ("payments-dev-156", "Payments", "Development", "3 days ago"),
                ("insurance-staging-034", "Insurance", "Staging", "5 days ago"),
                ("data-platform-sandbox-078", "Data Platform", "Sandbox", "1 week ago"),
                ("wealth-mgmt-prod-045", "Wealth Management", "Production", "1 week ago")
            ]
            
            for account, portfolio, env, time_ago in recent_onboarded:
                env_color = "#BF616A" if env == "Production" else "#A3BE8C" if env == "Development" else "#EBCB8B"
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 3px solid #A3BE8C;'>
                    <strong>{account}</strong><br/>
                    <small>{portfolio} | <span style='color: {env_color};'>{env}</span> | {time_ago}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🔴 Recently Offboarded")
            
            recent_offboarded = [
                ("legacy-crm-prod-012", "Digital Banking", "Decommissioned", "1 day ago"),
                ("test-sandbox-089", "Payments", "Cleanup", "4 days ago"),
                ("migration-temp-034", "Insurance", "Migration Complete", "1 week ago"),
                ("poc-ml-sandbox-067", "Data Platform", "POC Ended", "2 weeks ago")
            ]
            
            for account, portfolio, reason, time_ago in recent_offboarded:
                st.markdown(f"""
                <div style='background: #2E3440; padding: 0.7rem; border-radius: 5px; margin: 0.4rem 0; border-left: 3px solid #BF616A;'>
                    <strong>{account}</strong><br/>
                    <small>{portfolio} | Reason: {reason} | {time_ago}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== LIFECYCLE TAB 2: ACCOUNT ONBOARDING ====================
    with lifecycle_tab2:
        st.subheader("🚀 AWS Account Onboarding")
        
        st.markdown("""
        **Automated account provisioning** via AWS Control Tower with standardized configurations, 
        security baselines, and compliance guardrails.
        """)
        
        # Onboarding metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pending Requests", "8", "Awaiting approval")
        with col2:
            st.metric("In Progress", "5", "Being provisioned")
        with col3:
            st.metric("Completed (MTD)", "12", "+3 vs last month")
        with col4:
            st.metric("Avg Provisioning", "4.2 hours", "-1.5 hours")
        
        st.markdown("---")
        
        # New Account Request Form
        st.markdown("### 📝 New Account Request")
        
        with st.expander("➕ Submit New Account Request", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                account_name = st.text_input("Account Name *", placeholder="e.g., digital-banking-prod-090")
                portfolio = st.selectbox("Portfolio *", 
                    ["Digital Banking", "Insurance", "Payments", "Capital Markets", "Wealth Management", "Data Platform", "Shared Services"])
                environment = st.selectbox("Environment *", 
                    ["Production", "Development", "Staging", "Sandbox", "DR"])
                cost_center = st.text_input("Cost Center *", placeholder="e.g., CC-1001")
            
            with col2:
                owner_email = st.text_input("Account Owner Email *", placeholder="owner@company.com")
                team_dl = st.text_input("Team Distribution List *", placeholder="team-banking@company.com")
                business_justification = st.text_area("Business Justification *", placeholder="Describe the purpose of this account...")
                expected_monthly_cost = st.number_input("Expected Monthly Cost ($)", min_value=0, value=5000)
            
            st.markdown("#### Required Configurations")
            col1, col2, col3 = st.columns(3)
            with col1:
                vpc_required = st.checkbox("VPC Required", value=True)
                direct_connect = st.checkbox("Direct Connect", value=False)
                transit_gateway = st.checkbox("Transit Gateway", value=True)
            with col2:
                sso_integration = st.checkbox("SSO Integration", value=True)
                cloudtrail = st.checkbox("CloudTrail (Required)", value=True, disabled=True)
                config_rules = st.checkbox("Config Rules (Required)", value=True, disabled=True)
            with col3:
                guardduty = st.checkbox("GuardDuty (Required)", value=True, disabled=True)
                security_hub = st.checkbox("Security Hub (Required)", value=True, disabled=True)
                backup_policy = st.checkbox("AWS Backup Policy", value=True)
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🚀 Submit Request", type="primary", use_container_width=True):
                    st.success("✅ Account request submitted! Request ID: REQ-2024-00892")
                    st.info("📧 Approval request sent to cloud-governance@company.com")
            with col2:
                if st.button("💾 Save Draft", use_container_width=True):
                    st.info("💾 Draft saved")
        
        st.markdown("---")
        
        # Onboarding Pipeline
        st.markdown("### 🔄 Onboarding Pipeline")
        
        pipeline_stages = ["Pending Approval", "Approved", "Provisioning", "Configuring", "Validation", "Complete"]
        
        # Pending requests
        pending_requests = [
            {"id": "REQ-2024-00891", "account": "payments-prod-157", "requestor": "john.smith@company.com", 
             "portfolio": "Payments", "env": "Production", "stage": "Pending Approval", "submitted": "2 hours ago"},
            {"id": "REQ-2024-00890", "account": "insurance-dev-089", "requestor": "jane.doe@company.com", 
             "portfolio": "Insurance", "env": "Development", "stage": "Approved", "submitted": "1 day ago"},
            {"id": "REQ-2024-00889", "account": "banking-staging-045", "requestor": "mike.wilson@company.com", 
             "portfolio": "Digital Banking", "env": "Staging", "stage": "Provisioning", "submitted": "1 day ago"},
            {"id": "REQ-2024-00888", "account": "data-sandbox-123", "requestor": "sarah.chen@company.com", 
             "portfolio": "Data Platform", "env": "Sandbox", "stage": "Configuring", "submitted": "2 days ago"},
            {"id": "REQ-2024-00887", "account": "wealth-prod-067", "requestor": "tom.brown@company.com", 
             "portfolio": "Wealth Management", "env": "Production", "stage": "Validation", "submitted": "2 days ago"},
        ]
        
        for req in pending_requests:
            stage_idx = pipeline_stages.index(req['stage'])
            progress_pct = ((stage_idx + 1) / len(pipeline_stages)) * 100
            
            if req['stage'] == "Pending Approval":
                stage_color = "#EBCB8B"
            elif req['stage'] == "Complete":
                stage_color = "#A3BE8C"
            else:
                stage_color = "#88C0D0"
            
            env_color = "#BF616A" if req['env'] == "Production" else "#A3BE8C"
            
            st.markdown(f"""
            <div style='background: #2E3440; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='font-size: 1.1rem;'>{req['id']}</strong> - <strong>{req['account']}</strong><br/>
                        <small>{req['portfolio']} | <span style='color: {env_color};'>{req['env']}</span> | Requestor: {req['requestor']}</small>
                    </div>
                    <div style='text-align: right;'>
                        <span style='background: {stage_color}; color: #2E3440; padding: 4px 12px; border-radius: 12px; font-weight: bold;'>{req['stage']}</span><br/>
                        <small style='color: #88C0D0;'>Submitted: {req['submitted']}</small>
                    </div>
                </div>
                <div style='background: #4C566A; border-radius: 4px; height: 8px; margin-top: 10px;'>
                    <div style='background: {stage_color}; width: {progress_pct}%; height: 100%; border-radius: 4px;'></div>
                </div>
                <small style='color: #D8DEE9;'>Stage {stage_idx + 1} of {len(pipeline_stages)}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Onboarding Checklist
        st.markdown("### ✅ Standard Onboarding Checklist")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 Infrastructure Setup")
            checklist_infra = [
                ("Account created in Control Tower", True),
                ("OU assignment completed", True),
                ("SCPs applied", True),
                ("VPC provisioned (if required)", True),
                ("Transit Gateway attached", False),
                ("Direct Connect configured", False),
            ]
            for item, default in checklist_infra:
                st.checkbox(item, value=default, key=f"infra_{item}")
            
            st.markdown("#### 🔐 Security Configuration")
            checklist_security = [
                ("IAM Identity Center (SSO) configured", True),
                ("CloudTrail enabled", True),
                ("Config Rules deployed", True),
                ("GuardDuty enabled", True),
                ("Security Hub enabled", True),
                ("AWS Backup policy attached", False),
            ]
            for item, default in checklist_security:
                st.checkbox(item, value=default, key=f"sec_{item}")
        
        with col2:
            st.markdown("#### 📊 Governance & Compliance")
            checklist_gov = [
                ("Cost allocation tags configured", True),
                ("Budget alerts set up", True),
                ("Compliance baseline applied", True),
                ("Resource tagging policy enforced", False),
                ("Data classification completed", False),
            ]
            for item, default in checklist_gov:
                st.checkbox(item, value=default, key=f"gov_{item}")
            
            st.markdown("#### 📧 Notifications & Access")
            checklist_access = [
                ("Account owner notified", True),
                ("Team access provisioned", True),
                ("Runbook documentation shared", False),
                ("Onboarding training scheduled", False),
                ("Welcome email sent", False),
            ]
            for item, default in checklist_access:
                st.checkbox(item, value=default, key=f"access_{item}")
        
        st.markdown("---")
        
        # Automation Status
        st.markdown("### 🤖 Automated Provisioning Status")
        
        automation_steps = [
            ("AWS Control Tower Account Factory", "✅ Completed", "2 min", "Account created successfully"),
            ("OU Assignment", "✅ Completed", "30 sec", "Assigned to Production OU"),
            ("SCP Application", "✅ Completed", "15 sec", "3 SCPs applied"),
            ("VPC Provisioning", "🔄 In Progress", "~5 min", "Creating subnets..."),
            ("Security Baseline", "⏳ Pending", "~3 min", "Waiting for VPC"),
            ("SSO Configuration", "⏳ Pending", "~2 min", "Waiting for security baseline"),
            ("Tagging & Compliance", "⏳ Pending", "~1 min", "Final step"),
        ]
        
        for step, status, duration, detail in automation_steps:
            if "Completed" in status:
                color = "#A3BE8C"
            elif "In Progress" in status:
                color = "#88C0D0"
            else:
                color = "#4C566A"
            
            st.markdown(f"""
            <div style='background: #2E3440; padding: 0.6rem 1rem; border-radius: 5px; margin: 0.3rem 0; border-left: 3px solid {color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <span><strong>{step}</strong></span>
                    <span style='color: {color};'>{status}</span>
                </div>
                <small style='color: #88C0D0;'>Duration: {duration} | {detail}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # ==================== LIFECYCLE TAB 3: ACCOUNT OFFBOARDING ====================
    with lifecycle_tab3:
        st.subheader("🔴 AWS Account Offboarding")
        
        st.markdown("""
        **Secure and compliant account decommissioning** with resource cleanup verification, 
        data retention compliance, and complete audit trail.
        """)
        
        # Offboarding metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Pending Offboard", "4", "Awaiting approval")
        with col2:
            st.metric("In Progress", "2", "Being decommissioned")
        with col3:
            st.metric("Completed (MTD)", "4", "This month")
        with col4:
            st.metric("Avg Offboard Time", "5.3 days", "Including retention")
        
        st.markdown("---")
        
        # Offboarding Request Form
        st.markdown("### 📝 Account Offboarding Request")
        
        with st.expander("🔴 Submit Offboarding Request", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                offboard_account = st.selectbox("Select Account to Offboard *",
                    ["legacy-crm-prod-012", "test-sandbox-089", "migration-temp-034", "poc-ml-sandbox-067", "archive-data-045"])
                offboard_reason = st.selectbox("Reason for Offboarding *",
                    ["Project Completed", "Migration Complete", "Cost Optimization", "Consolidation", "Security Concern", "POC Ended", "Other"])
                offboard_date = st.date_input("Requested Offboard Date *", datetime.now() + timedelta(days=30))
            
            with col2:
                data_retention = st.selectbox("Data Retention Requirement *",
                    ["No retention required", "30 days", "90 days", "1 year", "7 years (compliance)", "Archive to Glacier"])
                backup_required = st.checkbox("Final backup required before deletion", value=True)
                compliance_review = st.checkbox("Compliance review completed", value=False)
                owner_approval = st.checkbox("Account owner approval obtained", value=False)
            
            offboard_justification = st.text_area("Offboarding Justification *", 
                placeholder="Provide detailed justification for account closure...")
            
            st.warning("""
            ⚠️ **Important**: Account offboarding is irreversible. Ensure all data has been backed up 
            or migrated before proceeding. Compliance and legal review may be required for production accounts.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔴 Submit Offboarding Request", type="primary", use_container_width=True):
                    st.success("✅ Offboarding request submitted! Request ID: OFF-2024-00156")
                    st.info("📧 Approval request sent to cloud-governance@company.com and compliance@company.com")
            with col2:
                if st.button("📋 Pre-Offboard Assessment", use_container_width=True):
                    st.info("🔍 Running pre-offboard resource assessment...")
        
        st.markdown("---")
        
        # Active Offboarding Requests
        st.markdown("### 🔄 Active Offboarding Requests")
        
        offboard_requests = [
            {"id": "OFF-2024-00155", "account": "legacy-crm-prod-012", "reason": "Migration Complete", 
             "stage": "Resource Cleanup", "resources": 45, "data_size": "2.3 TB", "target_date": "Dec 15, 2024"},
            {"id": "OFF-2024-00154", "account": "test-sandbox-089", "reason": "POC Ended", 
             "stage": "Pending Approval", "resources": 12, "data_size": "156 GB", "target_date": "Dec 10, 2024"},
            {"id": "OFF-2024-00153", "account": "migration-temp-034", "reason": "Consolidation", 
             "stage": "Data Backup", "resources": 89, "data_size": "5.7 TB", "target_date": "Dec 20, 2024"},
            {"id": "OFF-2024-00152", "account": "poc-ml-sandbox-067", "reason": "Cost Optimization", 
             "stage": "Validation", "resources": 23, "data_size": "890 GB", "target_date": "Dec 8, 2024"},
        ]
        
        offboard_stages = ["Pending Approval", "Data Backup", "Resource Cleanup", "Validation", "Account Closure", "Complete"]
        
        for req in offboard_requests:
            stage_idx = offboard_stages.index(req['stage'])
            progress_pct = ((stage_idx + 1) / len(offboard_stages)) * 100
            
            st.markdown(f"""
            <div style='background: #2E3440; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #BF616A;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='font-size: 1.1rem;'>{req['id']}</strong> - <strong>{req['account']}</strong><br/>
                        <small>Reason: {req['reason']} | Resources: {req['resources']} | Data: {req['data_size']}</small>
                    </div>
                    <div style='text-align: right;'>
                        <span style='background: #D08770; color: #2E3440; padding: 4px 12px; border-radius: 12px; font-weight: bold;'>{req['stage']}</span><br/>
                        <small style='color: #BF616A;'>Target: {req['target_date']}</small>
                    </div>
                </div>
                <div style='background: #4C566A; border-radius: 4px; height: 8px; margin-top: 10px;'>
                    <div style='background: #D08770; width: {progress_pct}%; height: 100%; border-radius: 4px;'></div>
                </div>
                <small style='color: #D8DEE9;'>Stage {stage_idx + 1} of {len(offboard_stages)}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Offboarding Checklist
        st.markdown("### ✅ Offboarding Checklist")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Pre-Offboarding")
            pre_offboard = [
                ("Account owner approval", True),
                ("Manager approval", True),
                ("Compliance review (if production)", True),
                ("Data classification review", False),
                ("Dependent services identified", False),
                ("Migration plan confirmed", False),
            ]
            for item, default in pre_offboard:
                st.checkbox(item, value=default, key=f"pre_off_{item}")
            
            st.markdown("#### 💾 Data & Backup")
            data_backup = [
                ("Final backup completed", True),
                ("Backup verification passed", True),
                ("Data retention policy applied", False),
                ("S3 data archived/deleted", False),
                ("RDS snapshots retained", False),
                ("EBS snapshots cleaned", False),
            ]
            for item, default in data_backup:
                st.checkbox(item, value=default, key=f"data_{item}")
        
        with col2:
            st.markdown("#### 🔧 Resource Cleanup")
            resource_cleanup = [
                ("EC2 instances terminated", False),
                ("RDS instances deleted", False),
                ("Lambda functions removed", False),
                ("S3 buckets emptied/deleted", False),
                ("IAM roles/users removed", False),
                ("VPC resources cleaned", False),
                ("Secrets Manager cleanup", False),
            ]
            for item, default in resource_cleanup:
                st.checkbox(item, value=default, key=f"cleanup_{item}")
            
            st.markdown("#### 📋 Finalization")
            finalization = [
                ("Cost allocation updated", False),
                ("Billing alerts removed", False),
                ("SSO access revoked", False),
                ("Account moved to Suspended OU", False),
                ("Closure documentation", False),
                ("Stakeholders notified", False),
            ]
            for item, default in finalization:
                st.checkbox(item, value=default, key=f"final_{item}")
        
        st.markdown("---")
        
        # Resource Assessment
        st.markdown("### 🔍 Pre-Offboard Resource Assessment")
        
        with st.expander("View Resource Assessment for: legacy-crm-prod-012", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Resources", "45")
            with col2:
                st.metric("Data Size", "2.3 TB")
            with col3:
                st.metric("Monthly Cost", "$4,200")
            with col4:
                st.metric("Dependencies", "3 accounts")
            
            st.markdown("#### Resource Breakdown")
            resource_df = pd.DataFrame({
                'Resource Type': ['EC2 Instances', 'RDS Databases', 'S3 Buckets', 'Lambda Functions', 'EBS Volumes', 'Secrets', 'IAM Roles'],
                'Count': [8, 2, 12, 15, 18, 5, 12],
                'Est. Data (GB)': [0, 450, 1800, 0, 120, 0, 0],
                'Monthly Cost': ['$1,200', '$890', '$180', '$45', '$120', '$5', '$0'],
                'Cleanup Status': ['⏳ Pending', '⏳ Pending', '🔄 In Progress', '⏳ Pending', '⏳ Pending', '✅ Done', '⏳ Pending']
            })
            
            st.dataframe(resource_df, use_container_width=True, hide_index=True)
            
            st.warning("""
            ⚠️ **Dependencies Detected**: 
            - `payments-prod-045` - API integration (must update before closure)
            - `data-lake-prod-001` - ETL pipeline source (migration required)
            - `monitoring-central-001` - CloudWatch cross-account (update dashboards)
            """)
    
    # ==================== LIFECYCLE TAB 4: REQUEST TRACKING ====================
    with lifecycle_tab4:
        st.subheader("📋 Request Tracking & History")
        
        st.markdown("""
        **Track all account lifecycle requests** with real-time status updates, 
        SLA monitoring, and complete audit history.
        """)
        
        # Tracking metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Open Requests", "12", "8 onboard, 4 offboard")
        with col2:
            st.metric("Avg Resolution", "2.8 days", "-0.3 days")
        with col3:
            st.metric("SLA Compliance", "96.4%", "+1.2%")
        with col4:
            st.metric("This Month", "16", "12 onboard, 4 offboard")
        
        st.markdown("---")
        
        # Filter controls
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_type = st.selectbox("Request Type", ["All", "Onboarding", "Offboarding"])
        with col2:
            filter_status = st.selectbox("Status", ["All", "Pending", "In Progress", "Completed", "Cancelled"])
        with col3:
            filter_portfolio = st.selectbox("Portfolio", ["All", "Digital Banking", "Insurance", "Payments", "Capital Markets", "Wealth Management"])
        with col4:
            filter_period = st.selectbox("Period", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"])
        
        st.markdown("---")
        
        # Request tracking table
        st.markdown("### 📊 All Requests")
        
        tracking_data = []
        request_types = ['Onboarding', 'Offboarding']
        statuses = ['Completed', 'In Progress', 'Pending Approval', 'Cancelled']
        portfolios = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Management']
        
        for i in range(20):
            req_type = random.choice(request_types)
            tracking_data.append({
                'Request ID': f"{'REQ' if req_type == 'Onboarding' else 'OFF'}-2024-{random.randint(100, 999):05d}",
                'Type': req_type,
                'Account Name': f"{random.choice(['banking', 'payments', 'insurance', 'data'])}-{random.choice(['prod', 'dev', 'staging'])}-{random.randint(1, 200):03d}",
                'Portfolio': random.choice(portfolios),
                'Requestor': f"{random.choice(['john', 'jane', 'mike', 'sarah'])}.{random.choice(['smith', 'doe', 'wilson', 'chen'])}@company.com",
                'Status': random.choice(statuses),
                'Submitted': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d'),
                'SLA Status': random.choice(['🟢 On Track', '🟢 On Track', '🟢 On Track', '🟡 At Risk', '🔴 Breached'])
            })
        
        df_tracking = pd.DataFrame(tracking_data)
        
        st.dataframe(
            df_tracking,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Request ID': st.column_config.TextColumn('Request ID', width='medium'),
                'Type': st.column_config.TextColumn('Type', width='small'),
                'Status': st.column_config.TextColumn('Status', width='medium')
            }
        )
        
        # Export options
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Export to CSV", use_container_width=True):
                st.success("✅ Downloaded request_tracking.csv")
        with col2:
            if st.button("📊 Generate Report", use_container_width=True):
                st.success("✅ Report generated")
        with col3:
            if st.button("📧 Email Summary", use_container_width=True):
                st.success("✅ Summary sent to cloud-ops@company.com")
        
        st.markdown("---")
        
        # SLA Dashboard
        st.markdown("### ⏱️ SLA Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Onboarding SLA (Target: 3 days)")
            
            sla_data = pd.DataFrame({
                'Month': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
                'Avg Days': [2.8, 3.2, 2.5, 2.3, 2.1],
                'Compliance %': [94, 89, 97, 98, 99]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sla_data['Month'], y=sla_data['Avg Days'], name='Avg Days', marker_color='#88C0D0'))
            fig.add_hline(y=3, line_dash="dash", line_color="#BF616A", annotation_text="SLA: 3 days")
            fig.update_layout(template='plotly_dark', height=250, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Offboarding SLA (Target: 7 days)")
            
            sla_data_off = pd.DataFrame({
                'Month': ['Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
                'Avg Days': [6.2, 7.5, 5.8, 5.3, 4.9],
                'Compliance %': [92, 85, 95, 97, 98]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sla_data_off['Month'], y=sla_data_off['Avg Days'], name='Avg Days', marker_color='#D08770'))
            fig.add_hline(y=7, line_dash="dash", line_color="#BF616A", annotation_text="SLA: 7 days")
            fig.update_layout(template='plotly_dark', height=250, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Audit Log
        st.markdown("### 📜 Recent Activity Log")
        
        audit_entries = [
            ("2024-11-24 14:32:15", "REQ-2024-00891", "Status changed to 'Approved'", "cloud-governance@company.com"),
            ("2024-11-24 14:28:45", "OFF-2024-00155", "Resource cleanup started", "automation@system"),
            ("2024-11-24 13:15:22", "REQ-2024-00890", "VPC provisioning completed", "automation@system"),
            ("2024-11-24 12:45:00", "OFF-2024-00154", "Approval request sent", "jane.doe@company.com"),
            ("2024-11-24 11:30:18", "REQ-2024-00889", "SSO configuration started", "automation@system"),
            ("2024-11-24 10:22:45", "REQ-2024-00888", "Security baseline applied", "automation@system"),
            ("2024-11-24 09:15:30", "OFF-2024-00153", "Data backup completed", "automation@system"),
        ]
        
        for timestamp, req_id, action, actor in audit_entries:
            st.markdown(f"""
            <div style='background: #2E3440; padding: 0.5rem 1rem; border-radius: 5px; margin: 0.2rem 0; font-size: 0.9rem;'>
                <span style='color: #88C0D0;'>{timestamp}</span> | 
                <strong>{req_id}</strong> | 
                {action} | 
                <span style='color: #A3BE8C;'>{actor}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # ==================== LIFECYCLE TAB 5: ACCOUNT INVENTORY ====================
    with lifecycle_tab5:
        st.subheader("📜 Complete Account Inventory")
        
        st.markdown("""
        **Comprehensive inventory of all AWS accounts** with metadata, ownership, 
        compliance status, and lifecycle information.
        """)
        
        # Inventory metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Accounts", "640")
        with col2:
            st.metric("Active", "612")
        with col3:
            st.metric("Suspended", "24")
        with col4:
            st.metric("Pending Closure", "4")
        with col5:
            st.metric("Last Audit", "2 days ago")
        
        st.markdown("---")
        
        # Search and filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_term = st.text_input("🔍 Search accounts", placeholder="Account name or ID...")
        with col2:
            inv_filter_env = st.multiselect("Environment", ["Production", "Development", "Staging", "Sandbox", "DR"])
        with col3:
            inv_filter_portfolio = st.multiselect("Portfolio", ["Digital Banking", "Insurance", "Payments", "Capital Markets", "Wealth Management", "Shared Services"])
        with col4:
            inv_filter_status = st.multiselect("Status", ["Active", "Suspended", "Pending Closure"])
        
        st.markdown("---")
        
        # Account inventory table
        inventory_data = []
        envs = ['Production', 'Development', 'Staging', 'Sandbox', 'DR']
        portfolios_inv = ['Digital Banking', 'Insurance', 'Payments', 'Capital Markets', 'Wealth Management', 'Shared Services']
        statuses_inv = ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Suspended', 'Pending Closure']
        
        for i in range(50):
            env = random.choice(envs)
            portfolio = random.choice(portfolios_inv)
            inventory_data.append({
                'Account ID': f'{random.randint(100000000000, 999999999999)}',
                'Account Name': f"{portfolio.lower().replace(' ', '-')[:8]}-{env.lower()[:4]}-{random.randint(1, 200):03d}",
                'Environment': env,
                'Portfolio': portfolio,
                'Owner': f"{random.choice(['john', 'jane', 'mike', 'sarah', 'tom'])}.{random.choice(['smith', 'doe', 'wilson'])}@company.com",
                'Status': random.choice(statuses_inv),
                'Created': (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime('%Y-%m-%d'),
                'Monthly Cost': f"${random.randint(1000, 50000):,}",
                'Compliance': random.choice(['✅ Compliant', '✅ Compliant', '✅ Compliant', '⚠️ Warning', '❌ Non-Compliant'])
            })
        
        df_inventory = pd.DataFrame(inventory_data)
        
        st.dataframe(
            df_inventory,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Export and actions
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📥 Export Full Inventory", use_container_width=True):
                st.success("✅ Downloaded account_inventory.csv")
        with col2:
            if st.button("🔄 Refresh Inventory", use_container_width=True):
                st.info("🔄 Refreshing from AWS Organizations...")
        with col3:
            if st.button("📊 Compliance Report", use_container_width=True):
                st.success("✅ Report generated")
        with col4:
            if st.button("📧 Send to Stakeholders", use_container_width=True):
                st.success("✅ Sent to cloud-governance@company.com")
        
        st.markdown("---")
        
        # Account Details Viewer
        st.markdown("### 🔍 Account Detail Viewer")
        
        selected_account = st.selectbox("Select Account", 
            ["digital-banking-prod-089", "payments-dev-156", "insurance-staging-034", "data-platform-sandbox-078"])
        
        if selected_account:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 Account Information")
                st.markdown(f"""
                | Property | Value |
                |----------|-------|
                | **Account ID** | 123456789012 |
                | **Account Name** | {selected_account} |
                | **Environment** | Production |
                | **Portfolio** | Digital Banking |
                | **OU Path** | Root/Production/Banking |
                | **Created** | 2023-06-15 |
                | **Owner** | john.smith@company.com |
                | **Cost Center** | CC-1001 |
                """)
            
            with col2:
                st.markdown("#### 📊 Account Metrics")
                st.metric("Monthly Cost", "$12,450", "+5% MoM")
                st.metric("Resources", "156", "+12 this month")
                st.metric("Compliance Score", "98%", "+2%")
                st.metric("Security Score", "96%", "+1%")
            
            st.markdown("#### 🔐 Applied Guardrails")
            guardrails = [
                ("SCP: DenyPublicS3", "✅ Active"),
                ("SCP: RequireIMDSv2", "✅ Active"),
                ("SCP: RestrictRegions", "✅ Active"),
                ("Config: RequireEncryption", "✅ Active"),
                ("Config: RequireTagging", "⚠️ 3 violations"),
            ]
            
            for guardrail, status in guardrails:
                color = "#A3BE8C" if "Active" in status else "#EBCB8B"
                st.markdown(f"- **{guardrail}**: <span style='color: {color};'>{status}</span>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 24px; background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border-radius: 12px; border: 1px solid #334155; margin-top: 20px;'>
    <div style='font-size: 1.3rem; font-weight: 700; color: #10B981; margin-bottom: 8px;'>🛡️ TechGuard Rails Platform</div>
    <div style='color: #CBD5E1; font-size: 0.95rem;'>Enterprise Cloud Operations | AWS Bedrock + Claude 4 | 640+ AWS Accounts | 6 AI Agents</div>
    <div style='color: #64748B; font-size: 0.85rem; margin-top: 8px;'>Version 2.0 | All Systems Operational | Transform Phase</div>
</div>
""", unsafe_allow_html=True)