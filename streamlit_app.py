import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

# Page configuration
st.set_page_config(
    page_title="AI Platform - Transform Phase Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #88C0D0;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #D8DEE9;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1f35 0%, #2E3440 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #5E81AC;
        margin-bottom: 1rem;
    }
    .agent-status {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .status-active {
        background-color: #A3BE8C;
        color: #000;
    }
    .status-idle {
        background-color: #EBCB8B;
        color: #000;
    }
    .status-processing {
        background-color: #88C0D0;
        color: #000;
    }
    .alert-critical {
        background-color: #BF616A;
        color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background-color: #D08770;
        color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .alert-info {
        background-color: #5E81AC;
        color: #fff;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2E3440;
        border-radius: 5px 5px 0 0;
        padding: 1rem 2rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #5E81AC;
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

# Helper functions for data generation
def generate_account_data(num_accounts=640):
    """Generate simulated AWS account data"""
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

def generate_cost_trend_data(days=90):
    """Generate cost trend data"""
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

# Main app header
st.markdown('<div class="main-header">🤖 AI-Powered Cloud Operations Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Transform Phase | AWS Bedrock + Claude 4 | 640+ AWS Accounts | Autonomous Operations</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Control Center")
    
    st.markdown("### System Status")
    st.success("🟢 All Systems Operational")
    st.metric("Uptime", "99.97%")
    st.metric("Active Agents", "6/6")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.metric("Total Accounts", "640")
    st.metric("Monthly Spend", "$2.8M")
    st.metric("Cost Savings (30d)", f"${st.session_state.cost_savings:,}")
    
    st.markdown("---")
    st.markdown("### Demo Controls")
    
    if st.button("🎯 Simulate Cost Optimization", use_container_width=True):
        st.session_state.actions_executed += 1
        st.session_state.cost_savings += random.randint(2000, 15000)
        st.success("Optimization executed!")
        time.sleep(0.5)
        st.rerun()
    
    if st.button("⚠️ Simulate Anomaly Detection", use_container_width=True):
        st.session_state.anomalies_detected += 1
        st.warning("Anomaly detected!")
        time.sleep(0.5)
        st.rerun()
    
    if st.button("🔄 Reset Demo", use_container_width=True):
        st.session_state.cost_savings = 0
        st.session_state.actions_executed = 0
        st.session_state.anomalies_detected = 0
        st.session_state.agent_decisions = []
        st.rerun()

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard", 
    "🤖 AI Agents", 
    "💰 FinOps Intelligence",
    "🛡️ Security & Compliance",
    "📈 Analytics & Insights",
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
        cost_data = generate_cost_trend_data()
        
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
    
    # Cost breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost Distribution by Service")
        
        services = ['EC2', 'RDS', 'S3', 'Lambda', 'EKS', 'Data Transfer', 'Other']
        costs = [850000, 420000, 280000, 180000, 350000, 290000, 430000]
        
        fig = go.Figure(data=[go.Pie(
            labels=services,
            values=costs,
            hole=0.4,
            marker_colors=['#A3BE8C', '#88C0D0', '#EBCB8B', '#B48EAD', '#5E81AC', '#D08770', '#BF616A']
        )])
        fig.update_layout(template='plotly_dark', height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Optimization Opportunities")
        
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
    st.header("🛡️ Security & Compliance Operations")
    
    # Security metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Security Score", "94/100", "+2 this week")
    with col2:
        st.metric("Compliance Rate", "97.8%", "+0.3%")
    with col3:
        st.metric("Vulnerabilities", "23", "-12 remediated")
    with col4:
        st.metric("Policy Violations", "5", "-3 auto-fixed")
    
    st.markdown("---")
    
    # Security findings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Recent Security Findings")
        
        findings = [
            ("Critical", "S3 bucket public access in prod-042", "🔄 Auto-remediation in progress"),
            ("High", "IAM user with unused credentials (90+ days)", "✅ Automatically disabled"),
            ("High", "Unencrypted EBS volume in staging", "✅ Encryption enabled"),
            ("Medium", "Security group with 0.0.0.0/0 access", "⏳ Pending review"),
            ("Low", "CloudTrail not enabled in new account", "✅ Automatically configured")
        ]
        
        for severity, finding, status in findings:
            color = "#BF616A" if severity == "Critical" else "#D08770" if severity == "High" else "#EBCB8B"
            st.markdown(f"""
            <div style='background: #2E3440; padding: 0.8rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid {color};'>
                <strong style='color: {color};'>{severity}</strong>: {finding}<br/>
                <small>{status}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📋 Compliance Status by Framework")
        
        frameworks = ['PCI DSS', 'HIPAA', 'SOC 2', 'GDPR', 'ISO 27001', 'NIST']
        scores = [98, 96, 99, 97, 95, 98]
        
        fig = go.Figure(data=[
            go.Bar(x=frameworks, y=scores, marker_color='#A3BE8C')
        ])
        fig.add_hline(y=95, line_dash="dash", line_color="#EBCB8B")
        fig.update_layout(
            template='plotly_dark',
            height=300,
            yaxis_range=[90, 100],
            yaxis_title='Compliance %'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Automated remediation
    st.subheader("🔧 Automated Security Remediation")
    
    st.markdown("""
    The AI platform continuously monitors security events and automatically remediates issues within defined guardrails:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        **Auto-Remediated (24h)**
        - 12 public S3 buckets secured
        - 8 unused IAM users disabled
        - 15 unencrypted volumes encrypted
        - 5 security groups tightened
        """)
    
    with col2:
        st.warning("""
        **Pending Review**
        - 3 high-impact changes
        - 2 cross-account access requests
        - 1 VPC peering configuration
        """)
    
    with col3:
        st.info("""
        **Audit Trail**
        - All actions logged
        - Claude reasoning preserved
        - 7-year retention
        - Compliance-ready reports
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