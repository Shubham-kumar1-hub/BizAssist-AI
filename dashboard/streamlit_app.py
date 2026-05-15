import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Smart AI Business Assistant", layout="wide")
st.title("Smart AI Business Assistant")


def api_request(method: str, path: str, token: str | None = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=30, **kwargs)
    if response.status_code >= 400:
        st.error(response.text)
        return None
    return response.json()


if "token" not in st.session_state:
    st.session_state.token = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


with st.sidebar:
    st.header("Account")
    email = st.text_input("Email", value="admin@example.com")
    password = st.text_input("Password", value="password123", type="password")
    auth_col1, auth_col2 = st.columns(2)
    if auth_col1.button("Sign up"):
        result = api_request("POST", "/auth/signup", json={"email": email, "password": password})
        if result:
            st.session_state.token = result["access_token"]
            st.success("Signed up and logged in.")
    if auth_col2.button("Login"):
        result = api_request("POST", "/auth/login", json={"email": email, "password": password})
        if result:
            st.session_state.token = result["access_token"]
            st.success("Logged in.")

    st.caption(f"Backend: {API_URL}")


if not st.session_state.token:
    st.info("Create an account or log in from the sidebar to use the dashboard.")
    st.stop()


tab_overview, tab_assistant, tab_documents, tab_leads, tab_workflows, tab_logs = st.tabs(
    ["Overview", "Assistant", "Documents", "Leads", "Workflows", "Logs"]
)


with tab_overview:
    summary = api_request("GET", "/analytics/summary", token=st.session_state.token) or {}
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Conversations", summary.get("total_conversations", 0))
    col2.metric("Messages", summary.get("total_messages", 0))
    col3.metric("Leads", summary.get("total_leads", 0))
    col4.metric("Documents", summary.get("total_documents", 0))

    left, right = st.columns(2)
    with left:
        st.subheader("Lead Temperature")
        st.bar_chart(pd.Series(summary.get("lead_temperature", {}), dtype="int64"))
    with right:
        st.subheader("Workflow Status")
        st.bar_chart(pd.Series(summary.get("workflow_status", {}), dtype="int64"))


with tab_assistant:
    st.subheader("Customer Conversation")
    customer_name = st.text_input("Customer name", value="Demo Customer")
    customer_email = st.text_input("Customer email", value="demo@example.com")
    message = st.text_area("Message", value="I am interested in your services. Can you tell me the price and contact me?")
    if st.button("Send message"):
        result = api_request(
            "POST",
            "/assistant/chat",
            token=st.session_state.token,
            json={
                "message": message,
                "conversation_id": st.session_state.conversation_id,
                "customer_name": customer_name,
                "customer_email": customer_email,
            },
        )
        if result:
            st.session_state.conversation_id = result["conversation_id"]
            st.write(result["answer"])
            st.caption(f"Sources: {', '.join(result.get('sources', [])) or 'No uploaded sources yet'}")
            st.caption(f"Validator: {result.get('validation_notes')}")
            if result.get("lead_created"):
                st.success(f"Lead captured as {result.get('lead_temperature')} lead.")


with tab_documents:
    st.subheader("Knowledge Documents")
    uploaded = st.file_uploader("Upload PDF or TXT document", type=["pdf", "txt", "md"])
    if uploaded and st.button("Index document"):
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
        result = api_request("POST", "/documents/upload", token=st.session_state.token, files=files)
        if result:
            st.success(f"Indexed {result['chunks_indexed']} chunks from {result['filename']}.")
    docs = api_request("GET", "/documents", token=st.session_state.token) or []
    st.dataframe(pd.DataFrame(docs), use_container_width=True)


with tab_leads:
    st.subheader("Lead CRM")
    with st.form("manual_lead"):
        name = st.text_input("Name")
        lead_email = st.text_input("Lead email")
        phone = st.text_input("Phone")
        interest = st.text_area("Interest")
        submitted = st.form_submit_button("Add lead")
        if submitted:
            api_request(
                "POST",
                "/leads",
                token=st.session_state.token,
                json={"name": name, "email": lead_email or None, "phone": phone or None, "interest": interest},
            )
    leads = api_request("GET", "/leads", token=st.session_state.token) or []
    st.dataframe(pd.DataFrame(leads), use_container_width=True)


with tab_workflows:
    st.subheader("Automation Workflows")
    col1, col2, col3 = st.columns(3)
    if col1.button("Generate follow-up"):
        result = api_request(
            "POST",
            "/workflows/run",
            token=st.session_state.token,
            json={"workflow_name": "lead_followup", "payload": {"lead": "Demo lead wants pricing"}},
        )
        if result:
            st.write(result["result"])
    if col2.button("Export CRM CSV"):
        result = api_request(
            "POST",
            "/workflows/run",
            token=st.session_state.token,
            json={"workflow_name": "crm_csv_sync", "payload": {}},
        )
        if result:
            st.success(result["result"])
    if col3.button("Summarize conversation"):
        result = api_request(
            "POST",
            "/workflows/run",
            token=st.session_state.token,
            json={"workflow_name": "conversation_summary", "payload": {"conversation": "Customer asked about services and pricing."}},
        )
        if result:
            st.write(result["result"])


with tab_logs:
    st.subheader("Conversation Logs")
    messages = api_request("GET", "/analytics/conversation-logs", token=st.session_state.token) or []
    st.dataframe(pd.DataFrame(messages), use_container_width=True)
    st.subheader("Workflow Logs")
    workflow_logs = api_request("GET", "/analytics/workflow-logs", token=st.session_state.token) or []
    st.dataframe(pd.DataFrame(workflow_logs), use_container_width=True)
