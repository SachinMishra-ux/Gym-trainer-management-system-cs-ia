import re
import streamlit as st
import pandas as pd
from api_client import check_health, get_clients, create_client

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,15}$")

# Streamlit Page Config
st.set_page_config(
    page_title="Gym Trainer System - Clients",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏋️‍♂️ Gym Trainer Management System")
st.caption("Client Directory & Client Registration (Integrated with FastAPI Backend)")

# Check Backend Health Status
health_info = check_health()
if health_info["healthy"]:
    st.sidebar.success("🟢 Backend API: Online")
else:
    st.sidebar.error(f"🔴 Backend API: Offline ({health_info.get('error', 'Unreachable')})")
    st.warning("⚠️ Cannot connect to FastAPI backend server at `http://127.0.0.1:8000`. Please make sure the backend is running.")

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Options")
active_only = st.sidebar.checkbox("Show Active Clients Only", value=False)

# Fetch Clients Data
clients = []
try:
    if health_info["healthy"]:
        clients = get_clients(active_only=active_only)
except Exception as err:
    st.error(f"Error fetching clients from API: {err}")

# Metric Cards
total_clients = len(clients)
active_clients_count = sum(1 for c in clients if c.get("active", True))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Clients", value=total_clients)
with col2:
    st.metric(label="Active Clients", value=active_clients_count)
with col3:
    st.metric(label="Inactive Clients", value=total_clients - active_clients_count)

st.markdown("---")

# Main Content Tabs: Client Directory & Add New Client
tab1, tab2 = st.tabs(["📋 Client Directory (GET /clients)", "➕ Add New Client (POST /clients)"])

with tab1:
    st.subheader("Client Roster")
    
    if not health_info["healthy"]:
        st.info("Backend server is currently offline. Start the server using: `uvicorn backend.main:app --reload`")
    elif not clients:
        st.info("No clients found in database.")
    else:
        # Search Filter
        search_query = st.text_input("Search Client by Name", placeholder="Type client name...").strip().lower()
        
        filtered_clients = [
            c for c in clients
            if not search_query or search_query in c.get("name", "").lower()
        ]
        
        if filtered_clients:
            # Format DataFrame for Streamlit Table
            df = pd.DataFrame(filtered_clients)
            df = df.rename(columns={
                "id": "ID",
                "name": "Full Name",
                "phone": "Phone Number",
                "email": "Email Address",
                "active": "Is Active",
                "created_at": "Created At"
            })
            
            # Format display values
            df["Is Active"] = df["Is Active"].apply(lambda val: "✅ Active" if val else "❌ Inactive")
            df["Phone Number"] = df["Phone Number"].fillna("N/A")
            df["Email Address"] = df["Email Address"].fillna("N/A")
            
            st.dataframe(
                df[["ID", "Full Name", "Phone Number", "Email Address", "Is Active", "Created At"]],
                width="stretch",
                hide_index=True
            )
            st.caption(f"Showing {len(filtered_clients)} client(s)")
        else:
            st.warning("No clients match your search query.")

with tab2:
    st.subheader("Register a New Client")
    st.write("Fill out the form below to create a new client record via the backend REST API.")
    
    with st.form(key="add_client_form", clear_on_submit=True):
        name_input = st.text_input("Client Full Name *", placeholder="e.g. John Doe")
        phone_input = st.text_input("Phone Number (10 digits)", placeholder="e.g. 9828376353")
        email_input = st.text_input("Email Address", placeholder="e.g. john.doe@example.com")
        active_input = st.checkbox("Active Client Status", value=True)
        
        submit_btn = st.form_submit_button("Add Client", type="primary")

    # Display feedback message directly below the Add Client form
    if submit_btn:
        name_val = name_input.strip()
        phone_val = phone_input.strip()
        email_val = email_input.strip()
        
        # Extract digits
        digits_only = re.sub(r"\D", "", phone_val) if phone_val else ""
        if phone_val and phone_val.startswith("+91") and len(digits_only) > 10:
            digits_only = digits_only[2:]
        elif phone_val and phone_val.startswith("+1") and len(digits_only) > 10:
            digits_only = digits_only[1:]
        elif phone_val and phone_val.startswith("+44") and len(digits_only) > 10:
            digits_only = digits_only[2:]
        
        # Validation Checks
        if not name_val:
            st.error("❌ Invalid Field: Client Name is required!")
        elif phone_val and not PHONE_REGEX.match(phone_val):
            st.error("❌ Invalid Field: Phone number must contain valid digits only (e.g. 9828376353). Alphabets and letters are not allowed!")
        elif phone_val and len(digits_only) != 10:
            st.error(f"❌ Invalid Field: Phone number must be a valid 10-digit number! (Found {len(digits_only)} digits)")
        elif email_val and not EMAIL_REGEX.match(email_val):
            st.error("❌ Invalid Field: Please enter a valid email address (e.g. user@example.com).")
        elif not health_info["healthy"]:
            st.error("❌ API Error: Backend server is offline.")
        else:
            try:
                new_client = create_client(
                    name=name_val,
                    phone=phone_val if phone_val else None,
                    email=email_val if email_val else None,
                    active=active_input
                )
                st.success(f"🎉 Success! Client '{new_client['name']}' (ID: #{new_client['id']}) was successfully added!")
            except Exception as e:
                st.error(f"❌ Creation Failed: {e}")
