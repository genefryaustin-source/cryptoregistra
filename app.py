import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from web3 import Web3
from eth_abi import encode

st.set_page_config(
    page_title="CryptoCheck • Public EAS Registry",
    page_icon="🔗",
    layout="wide"
)

SCHEMA_UID = "0x5a18963db219ed409d6e5fc7778784c36ab337def788cbc76aabe3258cc7ffa"
GRAPHQL_URL = "https://easscan.org/graphql"

# ====================== REGULATORY VALIDATION ======================
@st.cache_data(ttl=3600)
def load_mica_data():
    try:
        casps = pd.read_csv("https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv")
        ncasp = pd.read_csv("https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv")
        return casps, ncasp
    except:
        return None, None

def check_mica(entity_name: str):
    casps, ncasp = load_mica_data()
    if casps is None:
        return {"status": "❌ Unavailable", "details": "", "color": "red", "score": 0, "non_compliant": False}
    name_lower = entity_name.lower().strip()
    match = casps[casps.astype(str).apply(lambda x: x.str.contains(name_lower, case=False, na=False)).any(axis=1)]
    if not match.empty:
        return {"status": "✅ MiCA Authorised", "details": "ESMA CASP", "color": "green", "score": 15, "non_compliant": False}
    if ncasp is not None:
        match_nc = ncasp[ncasp.astype(str).apply(lambda x: x.str.contains(name_lower, case=False, na=False)).any(axis=1)]
        if not match_nc.empty:
            return {"status": "⚠️ MiCA Non-Compliant", "details": "ESMA Non-Compliant List", "color": "red", "score": 0, "non_compliant": True}
    return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}

def check_edgar(entity_name: str):
    try:
        url = f"https://www.sec.gov/edgar/search/?q={requests.utils.quote(entity_name)}"
        headers = {"User-Agent": "CryptoCheck Registry"}
        if entity_name.lower() in requests.get(url, headers=headers, timeout=10).text.lower():
            return {"status": "✅ EDGAR Found", "details": "SEC Filings", "color": "green", "score": 10, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_fincen_msb(entity_name: str):
    try:
        url = f"https://www.fincen.gov/msb-state-selector?search={requests.utils.quote(entity_name)}"
        headers = {"User-Agent": "CryptoCheck Registry"}
        if entity_name.lower() in requests.get(url, headers=headers, timeout=15).text.lower():
            return {"status": "✅ FinCEN MSB", "details": "Money Services Business", "color": "green", "score": 15, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_nmls_mtl(entity_name: str):
    try:
        url = f"https://nmlsconsumeraccess.org/EntitySearch?search={requests.utils.quote(entity_name)}"
        headers = {"User-Agent": "CryptoCheck Registry"}
        if "money transmitter" in requests.get(url, headers=headers, timeout=15).text.lower():
            return {"status": "✅ NMLS MTL Found", "details": "Nationwide Multistate Licensing", "color": "green", "score": 15, "non_compliant": False}
        return {"status": "⚠️ Limited MTL", "details": "No strong NMLS match", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_nydfs_bitlicense(entity_name: str):
    try:
        if entity_name.lower() in requests.get("https://www.dfs.ny.gov/apps_and_licensing/virtual_currency_businesses", timeout=15).text.lower():
            return {"status": "✅ NYDFS BitLicense", "details": "New York Virtual Currency License", "color": "green", "score": 15, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_cftc(entity_name: str):
    try:
        if entity_name.lower() in requests.get("https://www.cftc.gov/LabCFTC/Registrants", timeout=15).text.lower():
            return {"status": "✅ CFTC Registered", "details": "Futures / Derivatives", "color": "green", "score": 10, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_fca_uk(entity_name: str):
    try:
        url = f"https://register.fca.org.uk/s/search?predefined=CA&q={requests.utils.quote(entity_name)}"
        if "authorised" in requests.get(url, headers={"User-Agent": "CryptoCheck"}, timeout=15).text.lower():
            return {"status": "✅ FCA UK Registered", "details": "Cryptoasset authorised", "color": "green", "score": 10, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_mas_singapore(entity_name: str):
    try:
        url = f"https://eservices.mas.gov.sg/fid/institution?search={requests.utils.quote(entity_name)}"
        if any(x in requests.get(url, headers={"User-Agent": "CryptoCheck"}, timeout=15).text.lower() for x in ["dpt", "licensed"]):
            return {"status": "✅ MAS DPT Licensed", "details": "Digital Payment Token", "color": "green", "score": 10, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_asic_australia(entity_name: str):
    try:
        url = f"https://connect.asic.gov.au/search?query={requests.utils.quote(entity_name)}"
        if any(x in requests.get(url, headers={"User-Agent": "CryptoCheck"}, timeout=15).text.lower() for x in ["afsl", "licence"]):
            return {"status": "✅ ASIC Registered", "details": "AFSL / Crypto", "color": "green", "score": 10, "non_compliant": False}
        return {"status": "⚠️ Not Found", "details": "", "color": "orange", "score": 5, "non_compliant": False}
    except:
        return {"status": "❌ Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

def check_state_mtls(entity_name: str):
    try:
        score = 0
        details = []
        nmls_url = f"https://nmlsconsumeraccess.org/EntitySearch?search={requests.utils.quote(entity_name)}"
        if "money transmitter" in requests.get(nmls_url, headers={"User-Agent": "CryptoCheck"}, timeout=10).text.lower():
            score += 10
            details.append("NMLS MTL")
        
        if entity_name.lower() in requests.get("https://dfpi.ca.gov/regulated-industries/money-transmitters/directory-of-money-transmitters/", timeout=10).text.lower():
            score += 8
            details.append("CA DFPI")
        
        if entity_name.lower() in requests.get("https://www.dob.texas.gov/entity-search", timeout=10).text.lower():
            score += 8
            details.append("TX DOB")
        
        status = "✅ Multiple State MTLs" if score >= 15 else "⚠️ Limited State MTLs"
        return {"status": status, "details": ", ".join(details) or "No strong state MTL", "color": "green" if score >= 15 else "orange", "score": score, "non_compliant": False}
    except:
        return {"status": "❌ MTL Check Failed", "details": "", "color": "red", "score": 0, "non_compliant": False}

# ====================== HELPERS ======================
def compute_doc_hash(file_bytes):
    if not file_bytes:
        return "0x0000000000000000000000000000000000000000000000000000000000000000"
    return "0x" + hashlib.sha256(file_bytes).hexdigest()

def upload_to_ipfs(file_bytes, filename):
    if not file_bytes:
        return None
    try:
        jwt = st.secrets.get("PINATA_JWT")
        if not jwt:
            return "QmDemo" + hashlib.md5(file_bytes).hexdigest()[:20]
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {"Authorization": f"Bearer {jwt}"}
        files = {"file": (filename, file_bytes)}
        r = requests.post(url, headers=headers, files=files, timeout=30)
        r.raise_for_status()
        return r.json()["IpfsHash"]
    except:
        return None

def encode_attestation_data(legal_name, entity_type, website, description, country, timestamp, doc_hash, ipfs_cid):
    types = ["string", "string", "string", "string", "string", "uint256", "string", "string"]
    values = [legal_name, entity_type, website or "", description or "", country, timestamp, doc_hash, ipfs_cid or ""]
    return encode(types, values)

def query_eas_attestations():
    query = """
    query GetAttestations($schema: String!) {
      attestations(
        where: { schemaId: { equals: $schema } }
        take: 50
        orderBy: { time: desc }
      ) {
        id
        attester
        time
        revoked
      }
    }
    """
    try:
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"schema": SCHEMA_UID}})
        response.raise_for_status()
        return response.json().get("data", {}).get("attestations", [])
    except:
        return []

# ====================== SIDEBAR ======================
st.sidebar.title("🔗 CryptoCheck")
st.sidebar.markdown("**Public Registry with 10-Regulator Validation**")
mode = st.sidebar.radio("Navigation", ["🏠 Home", "📝 Register Entity", "🔍 Search Registry", "📊 Analytics", "ℹ️ About"])

# ====================== TABS ======================
if mode == "🏠 Home":
    st.title("CryptoCheck")
    st.subheader("Public Immutable Registry for Crypto Entities")
    st.markdown("Validates against **10 major regulators** before on-chain attestation.")

elif mode == "📝 Register Entity":
    st.title("Register Entity — 10-Regulator Validation + EAS Attestation")
    
    with st.form("register_form"):
        legal_name = st.text_input("Legal Entity Name *", placeholder="Phoenix DEX LLC")
        entity_type = st.selectbox("Entity Type *", ["Centralized/Decentralized Exchange", "Web3 Platform / dApp", "Crypto Recovery Company"])
        website = st.text_input("Official Website", placeholder="https://example.com")
        country = st.text_input("Country of Operation", "United States")
        description = st.text_area("Description", placeholder="What does your platform do?")
        wallet_input = st.text_input("Attester Wallet Address", placeholder="0x...")
        uploaded_file = st.file_uploader("Upload Proof Document (optional)", type=["pdf", "jpg", "png"])

        submitted = st.form_submit_button("🔍 Run Full Validation + Create EAS Attestation", type="primary")

        if submitted and legal_name:
            st.subheader("Regulatory Validation Results")

            results = {
                "MiCA (EU)": check_mica(legal_name),
                "EDGAR (US)": check_edgar(legal_name),
                "FinCEN MSB (US)": check_fincen_msb(legal_name),
                "NMLS MTL (US)": check_nmls_mtl(legal_name),
                "NYDFS BitLicense (US)": check_nydfs_bitlicense(legal_name),
                "CFTC (US)": check_cftc(legal_name),
                "FCA UK": check_fca_uk(legal_name),
                "MAS Singapore": check_mas_singapore(legal_name),
                "ASIC Australia": check_asic_australia(legal_name),
                "State MTLs": check_state_mtls(legal_name)
            }

            cols = st.columns(5)
            for i, (reg, res) in enumerate(results.items()):
                with cols[i % 5]:
                    st.markdown(f"**{reg}**")
                    st.markdown(f"**{res['status']}**")
                    st.caption(res['details'])

            total_score = sum(r['score'] for r in results.values())
            st.progress(total_score / 100)
            st.metric("Overall Compliance Score", f"{total_score}/100")

            if any(r.get('non_compliant', False) for r in results.values()):
                st.error("🚨 HIGH RISK: Entity on non-compliant list")
            elif total_score < 60:
                st.warning("⚠️ Low regulatory footprint")
            elif total_score >= 85:
                st.success("✅ Strong compliance")
            else:
                st.info("Moderate regulatory coverage")

            # EAS Attestation
            st.divider()
            st.subheader("EAS Attestation Preview")
            timestamp = int(datetime.now().timestamp())
            file_bytes = uploaded_file.getvalue() if uploaded_file else None
            doc_hash = compute_doc_hash(file_bytes)
            ipfs_cid = upload_to_ipfs(file_bytes, uploaded_file.name) if uploaded_file else None

            encoded = encode_attestation_data(legal_name, entity_type, website, description, country, timestamp, doc_hash, ipfs_cid or "")

            st.json({
                "Schema UID": SCHEMA_UID,
                "Legal Name": legal_name,
                "Entity Type": entity_type,
                "IPFS CID": ipfs_cid or "—",
                "Document Hash": doc_hash[:20] + "..."
            })

            st.success("✅ Validation complete. In production this would trigger MetaMask for EAS attestation.")

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