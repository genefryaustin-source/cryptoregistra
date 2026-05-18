import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from web3 import Web3
from eth_abi import encode

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Crypto Registra",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS (Website Style) ======================
st.markdown("""
<style>
    .stApp {
        background-color: #0a0f1c;
        color: #e0f0ff;
    }
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #00bfff;
        margin-bottom: 2rem;
    }
    .hero-text {
        font-size: 1.35rem;
        color: #a0b8ff;
        line-height: 1.4;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f1629;
        border-right: 1px solid #1e2a4d;
    }
    .stRadio > label {
        color: #e0f0ff;
    }

    /* Buttons */
    .stButton > button {
        background-color: #00bfff;
        color: #000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.65rem 2rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #00d4ff;
        transform: translateY(-2px);
    }

    /* Cards / Containers */
    .stContainer, .element-container {
        background-color: #121a2e;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #1e2a4d;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER (Website Style) ======================
col1, col2 = st.columns([1.2, 5])
with col1:
    st.image("logo.png", width=140)

with col2:
    st.markdown('<h1 class="main-header">Crypto Registra</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Global Registry for Crypto Exchanges, Web3 Platforms & Recovery Companies</p>', unsafe_allow_html=True)

st.markdown("**NEXT GENERATION REGULATORY INFRASTRUCTURE**", unsafe_allow_html=True)
st.markdown("---")

# ====================== SIDEBAR ======================
st.sidebar.title("🔗 CryptoCheck")
st.sidebar.markdown("**Public Registry with 10-Regulator Validation**")
mode = st.sidebar.radio("Navigation", 
    ["🏠 Home", "📝 Register Entity", "🔍 Search Registry", "📊 Analytics", "ℹ️ About"])

# ====================== MAIN CONTENT ======================
if mode == "🏠 Home":
    st.markdown('<h2 class="hero-text">Public Immutable Registry for Crypto Entities</h2>', unsafe_allow_html=True)
    st.markdown("""
    Validates against **10 major regulators** before on-chain attestation on Ethereum.
    """)
    
    st.success("✅ Live on **EAS Mainnet** • Real-time Multi-Regulator Validation")

elif mode == "📝 Register Entity":
    st.title("Register Entity — 10-Regulator Validation + EAS Attestation")
    
    with st.form("register_form"):
        legal_name = st.text_input("Legal Entity Name *", placeholder="Phoenix DEX LLC")
        entity_type = st.selectbox("Entity Type *", 
            ["Centralized/Decentralized Exchange", "Web3 Platform / dApp", "Crypto Recovery Company"])
        website = st.text_input("Official Website", placeholder="https://example.com")
        country = st.text_input("Country of Operation", "United States")
        description = st.text_area("Description", placeholder="What does your platform do?")
        wallet_input = st.text_input("Attester Wallet Address", placeholder="0x...")
        uploaded_file = st.file_uploader("Upload Proof Document (optional)", type=["pdf", "jpg", "png"])
        
        submitted = st.form_submit_button("🔍 Run Full Validation + Create EAS Attestation", type="primary")
        
        if submitted and legal_name:
            # ... (keep all your existing validation code here - I didn't change logic)
            # Just paste your existing validation code from check_mica to check_state_mtls

            # (I'll assume you keep the rest of your form processing code unchanged)

elif mode == "🔍 Search Registry":
    st.title("Search Public Registry")
     
    st.caption(f"Live on Ethereum Mainnet • Schema: {SCHEMA_UID[:20]}...")

    if st.button("🔄 Refresh from Ethereum Mainnet"):
        with st.spinner("Querying EAS GraphQL..."):
            attestations = query_eas_attestations()

        if attestations:
            df = pd.DataFrame(attestations)
            df['Registered'] = pd.to_datetime(df['time'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
            df = df[['id', 'attester', 'Registered', 'revoked']]
            df.columns = ['Attestation ID', 'Attester Wallet', 'Registered', 'Revoked']
            st.dataframe(df, use_container_width=True, hide_index=True)

            for _, row in df.iterrows():
                if st.button(f"View on easscan.org → {row['Attestation ID'][:12]}...", key=row['id']):
                    st.markdown(f"[Open Full Record](https://easscan.org/attestation/{row['id']})", unsafe_allow_html=True)
        else:
            st.info("No attestations found yet.\n\nRegister your first entity in the **Register Entity** tab to see records here.")

    else:
        st.info("Click **Refresh from Ethereum Mainnet** to load live on-chain data.")

elif mode == "📊 Analytics":
    st.title("Registry Analytics")
    st.info("Analytics will populate as entities register on-chain.")

else:
    st.title("About CryptoCheck")
    st.markdown("Public immutable registry built on Ethereum Attestation Service (EAS) with comprehensive regulatory validation across 10 jurisdictions.")

st.caption("CryptoCheck • EAS Mainnet • Real-time Multi-Regulator Validation")