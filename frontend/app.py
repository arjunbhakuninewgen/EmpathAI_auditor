import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
API_URL = "https://empathai-backend.onrender.com/scan"

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
                    
                    # 1. AI EXECUTIVE SUMMARY
                    with st.container():
                        st.subheader("🤖 Executive Summary")
                        st.info(ai_insight)

                    st.divider()

                    # 2. HIGH-LEVEL METRICS
                    stats = report.get("metadata", {}).get("severity_breakdown", {})
                    total = report.get("metadata", {}).get("total_issues", 0)
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total Violations", total)
                    c2.metric("🔥 Critical", stats.get("critical", 0))
                    c3.metric("🔸 Serious", stats.get("serious", 0))
                    c4.metric("🔹 Minor", stats.get("minor", 0))

                    st.divider()

                    # 3. PRIORITIZATION MATRIX (The "Good Table")
                    st.subheader("📊 Violation Overview")
                    
                    issues = report.get("issues", [])
                    
                    if issues:
                        # Create a clean summary table for the top view
                        summary_data = []
                        for i in issues:
                            summary_data.append({
                                "Priority": "🔴 High" if "HIGH" in i['fix_priority'] else "🟠 Medium" if "MEDIUM" in i['fix_priority'] else "🔵 Low",
                                "Rule ID": i['rule'],
                                "Issue Description": i['description'],
                                "Occurrences": i['total_occurrences'],
                                "WCAG Criteria": i['wcag']
                            })
                        
                        df = pd.DataFrame(summary_data)
                        st.dataframe(
                            df, 
                            use_container_width=True,
                            column_config={
                                "Occurrences": st.column_config.ProgressColumn(
                                    "Count", 
                                    format="%d", 
                                    min_value=0, 
                                    max_value=max(df["Occurrences"]) if not df.empty else 10
                                )
                            }
                        )

                        # 4. DEVELOPER TASK LIST (The Details)
                        st.subheader("🛠️ Developer Action Plan")
                        st.caption("Expand items below to see code snippets.")
                        
                        for index, issue in enumerate(issues):
                            p_color = "red" if "HIGH" in issue['fix_priority'] else "orange" if "MEDIUM" in issue['fix_priority'] else "blue"
                            
                            with st.expander(f":{p_color}[{issue['fix_priority']}] **{issue['rule']}** ({issue['total_occurrences']} issues)"):
                                st.markdown(f"**Description:** {issue['description']}")
                                st.markdown(f"**Compliance:** WCAG {issue['wcag']}")
                                
                                tabs = st.tabs(["📍 Locations & Code", "💡 AI Fix Advice"])
                                
                                with tabs[0]:
                                    snippets = issue.get("code_snippets", [])
                                    for i, snippet in enumerate(snippets):
                                        st.markdown(f"**Location {i+1}:** `{snippet.get('target')}`")
                                        st.code(snippet.get('html'), language='html')
                                        st.divider()
                                
                                with tabs[1]:
                                    st.info(f"Standard fix for **{issue['rule']}**: Ensure elements comply with WCAG {issue['wcag']}. Check generic accessibility documentation for {issue['rule']}.")

                    else:
                        st.balloons()
                        st.success("🎉 Perfect Score! No violations found.")
            else:
                st.error(f"Server Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Connection Error: Is the backend running? \n\n{e}")