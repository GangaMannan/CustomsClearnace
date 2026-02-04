import streamlit as st
from web3 import Web3
import hashlib
import json
import os
import ipfshttpclient
import io

# Connect to IPFS Desktop API (default port 5001)
try:
    # Use version 0.8.0a2 as discussed for Windows compatibility
    client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
except Exception as e:
    st.sidebar.error("❌ IPFS Desktop Not Running")

st.sidebar.title("Clean Chain Dashboard")
st.sidebar.info(
    "This system uses an Ethereum Shared Ledger (Ganache) to provide a "
    "Single Source of Truth for customs documents, reducing fraud and "
    "automated risk-based clearance."
)

# --- 1. SETUP & AUTOMATIC PATH SEARCH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
artifacts_path = os.path.join(current_dir, "artifacts")

def find_abi():
    # Searching for the file based on your actual spelling: CustomClearance
    for root, dirs, files in os.walk(artifacts_path):
        for file in files:
            # Match the exact name you see in your folder
            if file == "CustomsClearance.json": 
                return os.path.join(root, file)
    return None

abi_file_path = find_abi()

# --- 2. BLOCKCHAIN CONNECTION (Ganache) ---
ganache_url = "http://127.0.0.1:7545" 
w3 = Web3(Web3.HTTPProvider(ganache_url))

# --- 3. LOAD ABI & SMART CONTRACT ---
try:
    if abi_file_path is None:
        raise FileNotFoundError("Could not find any JSON file in artifacts. Run 'npx hardhat compile'.")
        
    with open(abi_file_path, "r") as f:
        contract_json = json.load(f)
        abi = contract_json["abi"]
    
    # Your specific Ganache deployment address
    contract_address = "0x7C2D9F1d98B17c5014BE2294DB7E517b3517872b" 
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    st.sidebar.success(f"✅ ABI Loaded: {os.path.basename(abi_file_path)}")
    st.sidebar.success("✅ Blockchain Link Active")
except Exception as e:
    st.sidebar.error("❌ Setup Failed")
    st.error(f"Error: {e}")
    st.stop()

# --- 4. USER INTERFACE (Frontend) ---
st.title("🛡️ Clean Chain: Blockchain Customs Clearance")
st.markdown("### Secure, Tamper-Proof Trade Documentation")



# Section for Exporter
st.header("Step 1: Exporter Submission Portal")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Declared Invoice Value ($)", min_value=0)
        hs_code = st.text_input("HS Code (e.g., 8471.30)")
    with col2:
        uploaded_file = st.file_uploader("Upload Invoice PDF", type="pdf")

if st.button("🚀 Submit to Ledger"):
    if uploaded_file and w3.is_connected():
        try:
            # --- STEP 1: UPLOAD TO IPFS (FIXED FOR PDF BINARY DATA) ---
            with st.spinner("Uploading to IPFS..."):
                # Convert PDF bytes into a binary stream to avoid utf-8 errors
                pdf_file_bytes = uploaded_file.getvalue()
                file_stream = io.BytesIO(pdf_file_bytes)
                
                # Upload the stream to IPFS
                res = client.add(file_stream)
                
                # Handle different library return types (list vs dict)
                if isinstance(res, list):
                    ipfs_cid = res[0]['Hash']
                else:
                    ipfs_cid = res['Hash']
            
            # --- STEP 2: DIGITAL FINGERPRINTING ---
            invoice_hash = hashlib.sha256(pdf_file_bytes).hexdigest()
            
            # --- STEP 3: AUTOMATED RISK SCORING & BLOCKCHAIN RECORD ---
            market_avg = 1000
            
            # Send transaction to the ledger
            tx_hash = contract.functions.processTrade(
                invoice_hash, int(price), market_avg
            ).transact({'from': w3.eth.accounts[0]})
            
            # --- DISPLAY RESULTS ---
            st.success(f"✅ Document Stored on IPFS! CID: `{ipfs_cid}`")
            st.markdown(f"🔗 [View on IPFS Gateway](https://ipfs.io/ipfs/{ipfs_cid})")
            st.write(f"**Digital Fingerprint (Hash):** `{invoice_hash}`")
            st.info(f"Blockchain TX ID: {tx_hash.hex()}")
            
            # Channel Assignment logic remains the same
            if price < (market_avg * 0.7):
                st.error("🚩 RED CHANNEL: Flagged for Physical Inspection.")
            else:
                st.success("✅ GREEN CHANNEL: Verified. Instant Clearance.")
                
        except Exception as e:
            st.error(f"Error during submission: {e}")
    else:
        st.warning("Please upload a file and ensure both Ganache and IPFS are running.")

# Section for Customs Authority (Validator Node view)
st.divider()
st.header("Step 2: Customs Validator View")

search_hash = st.text_input("Enter Invoice Hash to Verify")

if st.button("🔍 Verify on Ledger"):
    if search_hash:
        try:
            # This calls the 'ledger' mapping from your Smart Contract
            # It retrieves the (hash, price, status) stored on the blockchain
            record = contract.functions.ledger(search_hash).call()
            
            if record[0] == "":
                st.warning("No record found for this hash. Document may be fraudulent or not yet registered.")
            else:
                st.success("✅ Match Found on Immutable Ledger!")
                st.write(f"**Stored Hash:** {record[0]}")
                st.write(f"**Declared Price:** ${record[1]}")
                st.write(f"**Clearance Status:** {record[2]}")
        except Exception as e:
            st.error(f"Error querying ledger: {e}")