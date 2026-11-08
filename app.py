
import streamlit as st

st.set_page_config(
    page_title="UdyamOne | Business, Connected",
    page_icon="assets/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #F6F7FA;
}
header[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}
[data-testid="stSidebar"] {
    background: #171923;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
.brand {
    font-size: 29px;
    font-weight: 800;
    color: #D7193F;
    letter-spacing: -1.5px;
}
.hero {
    background: linear-gradient(120deg, #171923, #303447);
    padding: 42px;
    border-radius: 18px;
    color: white;
    margin: 15px 0 28px 0;
}
.hero h1 {
    font-size: 38px;
    color: white;
    margin-bottom: 10px;
}
.hero p {
    color: #D5D8E2;
    font-size: 16px;
    max-width: 650px;
}
.eyebrow {
    color: #FF8298;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}
.feature {
    background: white;
    border: 1px solid #EAECF0;
    border-radius: 14px;
    padding: 22px;
    min-height: 155px;
}
.feature h3 {
    color: #171923;
    font-size: 17px;
}
.feature p {
    color: #697386;
    font-size: 13px;
}
.tag {
    display: inline-block;
    background: #FFF0F2;
    color: #D7193F;
    padding: 5px 11px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
.section-title {
    font-size: 23px;
    font-weight: 700;
    color: #171923;
    margin: 25px 0 15px 0;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #EAECF0;
    padding: 15px;
    border-radius: 12px;
}
.stButton button {
    background: #D7193F;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
.stButton button:hover {
    background: #B91435;
    color: white;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">UdyamOne.</div>', unsafe_allow_html=True)
    st.caption("YOUR BUSINESS, CONNECTED.")
    st.divider()
    st.markdown("### Navigation")
    st.markdown("🏠  Overview")
    st.markdown("🤖  AI Business Advisor")
    st.markdown("📦  Bundle Builder")
    st.markdown("🧾  Quotes & Checkout")
    st.markdown("🪪  Smart KYC")
    st.markdown("🚚  Order Tracking")
    st.markdown("📊  Operations")
    st.divider()
    st.caption("Airtel Sync 2026 | Prototype")

st.markdown(
    '<div class="eyebrow">THE UNIFIED BUSINESS EXPERIENCE</div>',
    unsafe_allow_html=True
)
st.markdown('<div class="brand">UdyamOne.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="eyebrow">WELCOME TO UDYAMONE</div>
    <h1>Everything your business needs.<br>One connected experience.</h1>
    <p>
    Discover tailored business solutions, build service bundles,
    explore indicative quotes and navigate your business journey
    through one unified digital platform.
    </p>
    <span class="tag">SMARTER BUSINESS. SIMPLER GROWTH.</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Your business at a glance</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Solution categories", "04", "Unified ecosystem")
c2.metric("Customer journey", "04", "Connected stages")
c3.metric("Digital experience", "01", "Single platform")
c4.metric("Platform status", "Preview", "Prototype")

st.markdown('<div class="section-title">Explore the UdyamOne ecosystem</div>',
            unsafe_allow_html=True)

features = [
    ("🤖", "AI Business Advisor",
     "Discover relevant business solutions through guided requirement discovery."),
    ("📦", "Smart Bundle Builder",
     "Explore tailored combinations of connectivity and business services."),
    ("🧾", "Quote & Checkout",
     "Review indicative pricing and explore a streamlined quotation journey."),
    ("🪪", "Smart KYC",
     "Experience a guided digital document submission and verification journey."),
    ("🚚", "Order Tracker",
     "Follow the different stages of a business service order."),
    ("📊", "Operations Intelligence",
     "Explore an overview of business metrics and operational insights.")
]

for start in range(0, len(features), 3):
    cols = st.columns(3)
    for col, item in zip(cols, features[start:start+3]):
        emoji, title, description = item
        with col:
            st.markdown(f"""
            <div class="feature">
                <div style="font-size:27px">{emoji}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="section-title">The connected journey</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="feature">
    <div style="font-size:15px;font-weight:700;color:#171923">
    DISCOVER &nbsp; → &nbsp; CONFIGURE &nbsp; → &nbsp; VERIFY
    &nbsp; → &nbsp; TRACK
    </div>
    <p>
    From understanding business requirements to exploring solutions,
    completing verification and tracking orders.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.info(
    "Prototype Preview: UdyamOne is an early-stage concept demonstration. "
    "Displayed metrics and workflows are illustrative. Live AI, "
    "registry verification, payments and order integrations are not "
    "yet enabled."
)

st.markdown("""
<div style="text-align:center;color:#9298A5;padding:30px 0 5px 0;
font-size:12px">
UdyamOne © 2026 | Built for Airtel Sync 2026
<br>Connecting businesses to smarter digital solutions.
</div>
""", unsafe_allow_html=True)
