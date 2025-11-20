import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/scan"

st.set_page_config(page_title="EmpathAI Auditor", page_icon="♿", layout="wide")

# --- HEADER ---
st.title("♿ EmpathAI: Accessibility Auditor Agent")
st.markdown("Enter a URL below. Your AI Agent will scan, analyze, and critique the accessibility.")

# --- INPUT SECTION ---
col1, col2 = st.columns([3, 1])
with col1:
    url_input = st.text_input("Website URL", placeholder="https://example.com")
with col2:
    # Just for spacing
    st.write("") 
    st.write("")
    scan_button = st.button("🚀 Run Audit", type="primary", use_container_width=True)

# --- LOGIC ---
if scan_button and url_input:
    with st.spinner(f"🤖 Agent is visiting {url_input}... (This may take 30 seconds)"):
        try:
            # Call your FastAPI Backend
            response = requests.post(API_URL, json={"url": url_input, "wcag_level": "AA"})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for scanner errors
                if "error" in data:
                    st.error(f"Scanner Error: {data['error']}")
                else:
                    report = data.get("report", {})
                    ai_insight = data.get("ai_insight", "No AI summary available.")
                    
                    # --- RESULTS DASHBOARD ---
                    st.success("Audit Complete!")
                    
                    # 1. AI SUMMARY
                    st.subheader("🤖 Executive Summary (AI)")
                    st.info(ai_insight)
                    
                    # 2. METRICS ROW
                    stats = report.get("metadata", {}).get("severity_breakdown", {})
                    total = report.get("metadata", {}).get("total_issues", 0)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Issues", total)
                    m2.metric("🔥 Critical", stats.get("critical", 0))
                    m3.metric("🔸 Serious", stats.get("serious", 0))
                    m4.metric("🔹 Minor", stats.get("minor", 0))
                    
                
                  # 3. DEVELOPER TASK LIST
                    st.subheader("🛠️ Developer Task List")
                    st.markdown("---")
                    
                    issues = report.get("issues", [])
                    
                    if issues:
                        for index, issue in enumerate(issues):
                            # Priority Badge Color
                            p_color = "red" if "HIGH" in issue['fix_priority'] else "orange" if "MEDIUM" in issue['fix_priority'] else "blue"
                            
                            # Create a clean card for each issue group
                            with st.container():
                                c1, c2 = st.columns([0.1, 0.9])
                                
                                # A Checkbox to mark as "Done" (Visual only for now)
                                with c1:
                                    st.checkbox(f"## {index}", key=f"check_{index}", label_visibility="hidden")
                                
                                with c2:
                                    # Title Row
                                    st.markdown(f":{p_color}[**{issue['fix_priority']}**] : **{issue['rule']}**")
                                    st.caption(f"{issue['description']} (Affects {issue['total_occurrences']} elements)")
                                    
                                    # Expander for the gritty details
                                    with st.expander("View Code & Fixes"):
                                        # AI Hint (Static for now, but could be dynamic)
                                        st.info(f"**How to fix:** Ensure {issue['rule']} follows WCAG {issue['wcag']} standards.")
                                        
                                        # Code Snippets
                                        snippets = issue.get("code_snippets", [])
                                        for i, snippet in enumerate(snippets):
                                            st.markdown(f"**Location {i+1}:** `{snippet.get('target')}`")
                                            st.code(snippet.get('html'), language='html')
                                            st.divider()
                            
                            # Spacer between tasks
                            st.write("")
                    else:
                        st.balloons()
                        st.success("No violations found! Great job.")
            else:
                st.error(f"Server Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Connection Error: Is the backend running? \n\n{e}")