"""
Streamlit Chat App with Async Evaluation
"""

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
import requests
import uuid
import time

# Config
API_URL = "https://eval-api-531143332778.us-central1.run.app"
client = OpenAI()

st.title("💬 Chat with Evaluation")

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "eval_status" not in st.session_state:
    st.session_state.eval_status = {}

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "eval" in msg:
            with st.expander("📊 Evaluation"):
                st.json(msg["eval"])

# Chat input
if prompt := st.chat_input("Message"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": m["role"], "content": m["content"]} 
                     for m in st.session_state.messages]
        )
        reply = response.choices[0].message.content
        st.write(reply)
        
        # Trigger evaluation
        conv_id = str(uuid.uuid4())
        try:
            requests.post(f"{API_URL}/evaluate", json={
                "conversation_id": conv_id,
                "query": prompt,
                "response": reply
            })
            st.session_state.eval_status[conv_id] = "processing"
            st.info("🔄 Evaluation started...")
        except:
            st.warning("⚠️ Evaluation service unavailable")
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "conv_id": conv_id
        })

# Sidebar: Check evaluations
with st.sidebar:
    st.header("📊 Evaluations")
    
    if st.button("🔄 Refresh Status"):
        for msg in st.session_state.messages:
            if "conv_id" in msg and "eval" not in msg:
                conv_id = msg["conv_id"]
                try:
                    resp = requests.get(f"{API_URL}/evaluation/{conv_id}")
                    data = resp.json()
                    if data.get("status") == "completed":
                        msg["eval"] = data["results"]
                        st.success(f"✅ Evaluation complete")
                except:
                    pass
        st.rerun()
    
    # Show pending
    pending = sum(1 for m in st.session_state.messages 
                  if "conv_id" in m and "eval" not in m)
    st.metric("Pending Evaluations", pending)
