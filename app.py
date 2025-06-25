
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
MODEL_ID = os.getenv("MODEL_ID")
WATSONX_URL = os.getenv("WATSONX_URL")

# Function to get IBM token
def get_token():
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"apikey={API_KEY}&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    response = requests.post(url, headers=headers, data=data)

    print("Token response:", response.status_code, response.text)  # Add this line

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None
# Function to query Granite model
def granite_response(prompt):
    token = get_token()
    if not token:
        return "❌ Error: IBM authentication failed."

    url = f"{WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    body = {
        "messages": [
            {"role": "system", "content": "You are a helpful, cautious AI health assistant named HealthAI."},
            {"role": "user", "content": prompt}
        ],
        "project_id": PROJECT_ID,
        "model_id": MODEL_ID,
        "max_tokens": 2000,
        "temperature": 0
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        # Show response for debugging (optional)
        st.code(f"💬 IBM Response:\n{data}", language="json")

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ IBM API Error: {data['error']}"
        else:
            return f"❌ Unexpected response format: {data}"
    except Exception as e:
        return f"❌ Exception: {e}"
# Streamlit UI
st.set_page_config(page_title="HealthAI Assistant", layout="wide", page_icon="🧠")
st.title("🧠 HealthAI - Your Smart Health Assistant")

tabs = st.tabs([
    "💬 Chat Assistant",
    "🧪 Disease Predictor",
    "💊 Treatment Planner",
    "📊 Health Analytics",
])

# --- Chat Assistant ---
with tabs[0]:
    st.subheader("💬 Chat with HealthAI")
    user_input = st.text_input("Ask anything health-related:")
    if st.button("Send", key="chat"):
        if user_input:
            with st.spinner("Thinking..."):
                reply = granite_response(user_input)
            st.success(reply)
        else:
            st.warning("Please enter a message.")

# --- Disease Predictor ---
with tabs[1]:
    st.subheader("🧪 Disease Predictor")
    symptoms_input = st.text_input("Enter symptoms (comma-separated):")
    if st.button("Predict Disease", key="predict"):
        if symptoms_input:
            with st.spinner("Predicting..."):
                prompt = f"Based on the symptoms: {symptoms_input}, what is the most likely disease?"
                reply = granite_response(prompt)
            st.success(reply)
        else:
            st.warning("Please enter symptoms.")

# --- Treatment Plan Generator ---
with tabs[2]:
    st.subheader("💊 Treatment Plan Generator")
    diagnosis_input = st.text_input("Enter a diagnosis:")
    if st.button("Generate Plan", key="treatment"):
        if diagnosis_input:
            with st.spinner("Generating..."):
                prompt = f"Provide a detailed treatment plan for {diagnosis_input}."
                reply = granite_response(prompt)
            st.success(reply)
        else:
            st.warning("Please enter a diagnosis.")

# --- Health Analytics ---
with tabs[3]:
    st.subheader("📊 Health Analytics")
    analytics_input = st.text_area("Enter patient data:")
    if st.button("Generate Analytics", key="analytics"):
        if analytics_input:
            with st.spinner("Analyzing..."):
                prompt = f"Analyze the following patient health data and provide insights:\n{analytics_input}"
                reply = granite_response(prompt)
            st.success(reply)
        else:
            st.warning("Please enter data.")
