import streamlit as st
from web3 import Web3
import hashlib
import json
import os
import subprocess
import tempfile
import base64
import requests

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Clean Chain | Customs Clearance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# MONOCHROME PASTEL BLUE THEME (BACKGROUND ALWAYS VISIBLE)
# ----------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=IBM+Plex+Mono:wght@400;600;700&display=swap');

:root{
  --ink: rgba(16, 30, 48, 0.95);
  --muted: rgba(16, 30, 48, 0.70);
  --line: rgba(60, 95, 130, 0.26);
  --shadow: 0 12px 24px rgba(16, 30, 48, 0.10);

  --panel: rgba(255,255,255,0.78);
  --chip: rgba(234,244,255,0.92);
  --btn: rgba(214,234,255,0.96);
}

/* ================================
   BACKGROUND (FIXED / ALWAYS VISIBLE)
   Applied to Streamlit root container
   ================================ */

/* Root container */
[data-testid="stAppViewContainer"]{
  position: relative !important;
  background: transparent !important;
}

/* Background overlay pinned to viewport */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: 0;
  z-index: -1;
  /* Stronger pastel blue so it doesn't look white */
  background: linear-gradient(180deg, #bfe0ff 0%, #e8f4ff 55%, #ffffff 100%);
}

/* Make Streamlit layers transparent so overlay shows */
html, body{
  background: transparent !important;
}

[data-testid="stAppViewBlockContainer"],
section.main,
.main,
.block-container,
.stApp,
header,
[data-testid="stHeader"],
[data-testid="stToolbar"]{
  background: transparent !important;
}

/* Typography */
html, body, [class*="css"]{
  font-family: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  color: var(--ink) !important;
}
h1,h2,h3,h4,h5,h6{
  font-family: "VT323","IBM Plex Mono",monospace !important;
  letter-spacing: 0.6px;
  color: var(--ink) !important;
}

/* spacing */
.block-container{
  padding-top: 1.0rem;
  padding-bottom: 2rem;
}

/* Header bar */
.cc-topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(214,234,255,0.98), rgba(234,244,255,0.92));
  border: 2px solid var(--line);
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.cc-brand{ display:flex; align-items:center; gap:10px; }
.cc-shield{ font-size:22px; }
.cc-title{
  font-family:"VT323","IBM Plex Mono",monospace !important;
  font-size: 50px;
  letter-spacing: 2px;
  color: var(--ink) !important;
}
.cc-tag{
  font-size: 12px;
  font-weight: 900;
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.72);
  border: 2px solid var(--line);
  color: var(--ink) !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Cards */
.cc-card{
  background: var(--panel) !important;
  border: 2px solid var(--line);
  border-radius: 14px;
  padding: 14px 14px;
  box-shadow: var(--shadow);
}
.cc-label{
  font-size: 12px;
  color: var(--muted) !important;
  margin-bottom: 6px;
}

/* Pills */
.pill{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding: 8px 10px;
  border-radius: 14px;
  font-weight: 800;
  font-size: 12px;
  border: 2px solid var(--line);
  background: rgba(255,255,255,0.82);
  color: var(--ink) !important;
}
.pill-dot{
  width:10px; height:10px;
  border-radius: 3px;
  display:inline-block;
  background: rgba(214,234,255,1.0);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap: 10px; }
.stTabs [data-baseweb="tab"]{
  background: rgba(234,244,255,0.96) !important;
  border: 2px solid var(--line) !important;
  border-radius: 14px !important;
  padding: 10px 14px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--ink) !important;
}
.stTabs [aria-selected="true"]{
  background: rgba(214,234,255,0.98) !important;
}

/* Buttons */
.stButton > button{
  border-radius: 14px !important;
  padding: 0.72rem 1.1rem !important;
  border: 2px solid var(--line) !important;
  background: var(--btn) !important;
  color: var(--ink) !important;
  font-weight: 900 !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.stButton > button:hover{ filter: brightness(0.99); }
.stButton > button:active{ transform: translateY(1px); }

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea{
  border-radius: 14px !important;
  border: 2px solid var(--line) !important;
  background: rgba(255,255,255,0.95) !important;
  color: var(--ink) !important;
}

/* Number +/- */
[data-testid="stNumberInput"] button{
  background: rgba(234,244,255,1.0) !important;
  border: 2px solid var(--line) !important;
  color: var(--ink) !important;
  border-radius: 14px !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"]{
  background: rgba(234,244,255,0.98) !important;
  border: 2px dashed rgba(60,95,130,0.38) !important;
  border-radius: 14px !important;
  padding: 18px !important;
}
[data-testid="stFileUploaderDropzone"] *{ color: var(--ink) !important; }
[data-testid="stFileUploaderDropzone"] button{
  background: rgba(214,234,255,0.98) !important;
  border: 2px solid var(--line) !important;
  color: var(--ink) !important;
  border-radius: 12px !important;
  font-weight: 900 !important;
  padding: 10px 14px !important;
}

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(234,244,255,0.98), rgba(255,255,255,0.95)) !important;
  border-right: 2px solid var(--line) !important;
}
section[data-testid="stSidebar"] *{ color: var(--ink) !important; }
section[data-testid="stSidebar"] .stCaptionContainer,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span{ color: var(--muted) !important; }

/* Accent panels (monochrome) */
.accent{
  border-radius: 14px;
  padding: 12px 14px;
  border: 2px solid var(--line);
  background: rgba(255,255,255,0.86);
}
.accent-blue, .accent-green, .accent-red, .accent-yellow, .accent-orange{
  border-left: 12px solid rgba(214,234,255,1.0);
}

/* code */
code{
  background: rgba(214,234,255,0.60) !important;
  color: var(--ink) !important;
  padding: 2px 6px;
  border-radius: 8px;
  border: 1px solid rgba(60,95,130,0.22);
}
</style>
"""
# st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

#use: st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------
# 0) PATHS
# ----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_path = os.path.join(current_dir, "artifacts")

IPFS_EXE = r"C:\ipfs\kubo\ipfs.exe"  # update if different
HASH_TO_CID_PATH = os.path.join(current_dir, "hash_to_cid.json")

# ----------------------------
# 1) AUTO DEPLOY (Ganache)
# ----------------------------
def auto_deploy_contract(project_root):
    cmd = ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "ganache"]
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        shell=True
    )
    return result.returncode, result.stdout, result.stderr

# ----------------------------
# 2) IPFS UPLOAD VIA KUBO CLI
# ----------------------------
def ipfs_add_pdf_via_cli(pdf_bytes: bytes) -> str:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        result = subprocess.run(
            [IPFS_EXE, "add", "-Q", tmp_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Unknown IPFS CLI error")

        cid = result.stdout.strip()
        if not cid:
            raise RuntimeError("IPFS CLI returned empty CID.")
        return cid

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

# ----------------------------
# 3) LOCAL HASH -> CID STORE
# ----------------------------
def load_hash_map() -> dict:
    if os.path.exists(HASH_TO_CID_PATH):
        try:
            with open(HASH_TO_CID_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
    return {}

def save_hash_map(data: dict) -> None:
    with open(HASH_TO_CID_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def show_pdf_from_url(url: str):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    b64 = base64.b64encode(r.content).decode("utf-8")
    pdf_html = f"""
    <iframe
        src="data:application/pdf;base64,{b64}"
        width="100%"
        height="720"
        style="border:0; border-radius:12px; background:white;">
    </iframe>
    """
    st.components.v1.html(pdf_html, height=740)

# ----------------------------
# 4) FIND ABI
# ----------------------------
def find_abi():
    for root, dirs, files in os.walk(artifacts_path):
        for file in files:
            if file == "CustomsClearance.json":
                return os.path.join(root, file)
    return None

abi_file_path = find_abi()

# ----------------------------
# 5) CONNECT BLOCKCHAIN (Ganache)
# ----------------------------
ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

# ----------------------------
# 6) LOAD ABI + CONTRACT ADDRESS
# ----------------------------
try:
    if abi_file_path is None:
        raise FileNotFoundError(
            "Could not find CustomsClearance.json in artifacts.\n"
            "Run: npx hardhat compile"
        )

    with open(abi_file_path, "r", encoding="utf-8") as f:
        contract_json = json.load(f)
        abi = contract_json["abi"]

    deployed_address_path = os.path.join(current_dir, "deployedAddress.json")
    if not os.path.exists(deployed_address_path):
        raise FileNotFoundError(
            "deployedAddress.json not found.\n"
            "Deploy once using:\n"
            "npx hardhat run scripts/deploy.js --network ganache\n"
            "or use Auto Deploy in sidebar."
        )

    with open(deployed_address_path, "r", encoding="utf-8") as f:
        deploy_info = json.load(f)
        contract_address = deploy_info["contractAddress"]

    contract = w3.eth.contract(address=contract_address, abi=abi)

except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.markdown("### ⚙️ Port Systems")
    st.caption("Operational checks for local blockchain + IPFS services.")

    ganache_ok = w3.is_connected()
    ipfs_ok = os.path.exists(IPFS_EXE)

    st.markdown(
        f"""
        <div class="pill">
          <span class="pill-dot" style="background:{'rgba(201,242,230,0.98)' if ganache_ok else 'rgba(255,210,217,0.98)'}"></span>
          Ganache: {"Connected" if ganache_ok else "Not Connected"}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="pill">
          <span class="pill-dot" style="background:{'rgba(201,242,230,0.98)' if ipfs_ok else 'rgba(255,210,217,0.98)'}"></span>
          IPFS Kubo: {"Ready" if ipfs_ok else "Missing ipfs.exe"}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 🚀 Contract Deployment")
    st.caption("Optional: redeploy contract to Ganache using Hardhat.")
    if st.button("Deploy to Ganache"):
        code, out, err = auto_deploy_contract(current_dir)
        if code == 0:
            st.success("Deployed! Reloading...")
            st.code(out)
            st.rerun()
        else:
            st.error("Deploy failed")
            st.code(err or out)

    st.markdown("---")
    st.markdown("### 🧠 Quick Notes")
    st.caption("Keep `ipfs daemon` running to preview PDFs via local gateway.")
    st.caption("Validator previews the invoice; exporter does not.")

# ----------------------------
# CLEAN HEADER (NO SUBTEXT BELOW)
# ----------------------------
st.markdown(
    """
    <div class="cc-topbar">
      <div class="cc-brand">
        <span class="cc-shield">🛡️</span>
        <span class="cc-title">CLEAN CHAIN</span>
      </div>
      <div class="cc-tag">Customs Clearance Console</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# TABS
# ----------------------------
tab_exporter, tab_validator = st.tabs(["🧾 Exporter Desk", "🛂 Customs Validator"])

# =========================================================
# EXPORTER TAB (NO PREVIEW)
# =========================================================
with tab_exporter:
    st.markdown('<div class="cc-card">', unsafe_allow_html=True)
    st.markdown("#### Exporter Submission")
    st.caption("Upload invoice PDF → stored on IPFS → hash anchored on blockchain ledger.")

    c1, c2, c3 = st.columns([1.1, 1.1, 1.3])
    with c1:
        st.markdown('<div class="cc-label">Declared Invoice Value</div>', unsafe_allow_html=True)
        price = st.number_input("Declared Invoice Value ($)", min_value=0, label_visibility="collapsed")
    with c2:
        st.markdown('<div class="cc-label">HS Code</div>', unsafe_allow_html=True)
        hs_code = st.text_input("HS Code (e.g., 8471.30)", label_visibility="collapsed")
    with c3:
        st.markdown('<div class="cc-label">Invoice PDF</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Invoice PDF", type="pdf", label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🚢 Submit to Port Ledger", key="submit_exporter"):
        if not w3.is_connected():
            st.warning("Ganache is not connected. Start Ganache first.")
            st.stop()

        if not os.path.exists(IPFS_EXE):
            st.error(f"ipfs.exe not found at: {IPFS_EXE}\nUpdate IPFS_EXE in app.py")
            st.stop()

        if uploaded_file is None:
            st.warning("Please upload an invoice PDF.")
            st.stop()

        try:
            pdf_file_bytes = uploaded_file.getvalue()

            with st.spinner("📦 Uploading to IPFS (local Kubo)..."):
                ipfs_cid = ipfs_add_pdf_via_cli(pdf_file_bytes)

            invoice_hash = hashlib.sha256(pdf_file_bytes).hexdigest()

            hash_map = load_hash_map()
            hash_map[invoice_hash] = ipfs_cid
            save_hash_map(hash_map)

            market_avg = 1000
            tx_hash = contract.functions.processTrade(
                invoice_hash, int(price), market_avg
            ).transact({"from": w3.eth.accounts[0]})

            st.success("✅ Submitted successfully. Manifest stored (Exporter has no preview).")

            st.markdown(
                f"""
                <div class="accent accent-blue">
                    <b>Dock Manifest</b><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">CID:</span> <code>{ipfs_cid}</code><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">Invoice Hash:</span> <code>{invoice_hash}</code><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">TX ID:</span> <code>{tx_hash.hex()}</code>
                </div>
                """,
                unsafe_allow_html=True
            )

            # still monochrome: same border, different message
            if price < (market_avg * 0.7):
                st.markdown(
                    """
                    <div class="accent accent-red">
                        🚩 <b>RED CHANNEL</b> — Flagged for physical inspection (risk/anomaly).
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div class="accent accent-green">
                        ✅ <b>GREEN CHANNEL</b> — Verified for instant clearance (low risk).
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"Submission error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# VALIDATOR TAB (SHOW PREVIEW)
# =========================================================
with tab_validator:
    st.markdown('<div class="cc-card">', unsafe_allow_html=True)
    st.markdown("#### Validator Verification")
    st.caption("Verify hash on-chain → fetch PDF from IPFS via local gateway → preview inside validator console.")

    v1, v2 = st.columns([1.4, 1.0])
    with v1:
        st.markdown('<div class="cc-label">Invoice Hash</div>', unsafe_allow_html=True)
        search_hash = st.text_input("Enter Invoice Hash to Verify", key="validator_hash", label_visibility="collapsed")
    with v2:
        st.markdown('<div class="cc-label">Fallback CID (Optional)</div>', unsafe_allow_html=True)
        manual_cid = st.text_input("Optional: Enter CID", key="validator_cid", label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🔍 Verify & Open Cargo Docs", key="verify_validator"):
        if not w3.is_connected():
            st.warning("Ganache is not connected. Start Ganache first.")
            st.stop()

        if not search_hash:
            st.warning("Please enter an invoice hash.")
            st.stop()

        try:
            record = contract.functions.ledger(search_hash).call()

            if record[0] == "":
                st.warning("No record found for this hash.")
                st.stop()

            st.markdown(
                f"""
                <div class="accent accent-yellow">
                    ✅ <b>Ledger Match Found</b><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">Stored Hash:</span> <code>{record[0]}</code><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">Declared Price:</span> <b>${record[1]}</b><br>
                    <span style="color:rgba(16, 30, 48, 0.72)">Clearance Status:</span> <b>{record[2]}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

            hash_map = load_hash_map()
            cid = hash_map.get(search_hash) or manual_cid.strip()

            if not cid:
                st.warning("CID not available. Exporter must submit once, or enter CID manually.")
                st.stop()

            local_gateway_url = f"http://127.0.0.1:8080/ipfs/{cid}"

            st.markdown(
                f"""
                <div class="accent accent-orange">
                    📄 <b>Document Gateway</b><br>
                    Open in browser: <a href="{local_gateway_url}" target="_blank">{local_gateway_url}</a>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown("##### Invoice Preview (Validator Only)")
            show_pdf_from_url(local_gateway_url)

        except Exception as e:
            st.error(f"Verification error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
