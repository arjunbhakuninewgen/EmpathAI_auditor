import streamlit as st
import requests
import pandas as pd
import time

# --- CONFIGURATION ---
# Use localhost if running locally or Docker
API_BASE = "http://localhost:8000"

st.set_page_config(page_title="EmpathAI v2.0", page_icon="♿", layout="wide")

# --- SESSION STATE ---
if "crawled_pages" not in st.session_state:
    st.session_state.crawled_pages = []
if "audit_results" not in st.session_state:
    st.session_state.audit_results = {}

# --- HEADER ---
st.title("♿ EmpathAI v2.0: Autonomous Auditor")
st.markdown("### Discovery & Remediation Engine")

# --- STEP 1: DISCOVERY (The Crawler) ---
with st.container():
    st.subheader("1. Discovery Phase")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        target_url = st.text_input("Enter Website URL", placeholder="https://example.com")
    
    with col2:
        st.write("") 
        st.write("") 
        if st.button("🕷️ Start Discovery", type="primary", use_container_width=True):
            if not target_url:
                st.error("Please enter a URL.")
            else:
                with st.spinner(f"Crawling {target_url} for pages..."):
                    try:
                        response = requests.post(f"{API_BASE}/crawl", json={"url": target_url, "max_pages": 10})
                        if response.status_code == 200:
                            data = response.json()
                            
                            # --- THE FIX: CLEAR OLD DATA ---
                            st.session_state.audit_results = {}  # <--- Add this line!
                            # -------------------------------
                            
                            st.session_state.crawled_pages = data.get("urls", [])
                            st.success(f"Found {len(st.session_state.crawled_pages)} pages!")
                        else:
                            st.error(f"Crawler failed: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

# --- STEP 2: SELECTION & AUDIT ---
if st.session_state.crawled_pages:
    st.divider()
    st.subheader("2. Select Pages to Audit")
    
    selected_pages = st.multiselect(
        "Choose pages to analyze", 
        st.session_state.crawled_pages,
        default=st.session_state.crawled_pages[:1]
    )
    
    if st.button("🚀 Run Deep Audit", type="primary"):
        if not selected_pages:
            st.warning("Please select at least one page.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, page_url in enumerate(selected_pages):
                status_text.text(f"🤖 Agent is auditing: {page_url} ...")
                try:
                    response = requests.post(f"{API_BASE}/audit", json={"url": page_url})
                    if response.status_code == 200:
                        st.session_state.audit_results[page_url] = response.json()
                    else:
                        st.error(f"Failed to audit {page_url}")
                except Exception as e:
                    st.error(f"Error on {page_url}: {e}")
                
                progress_bar.progress((i + 1) / len(selected_pages))
            
            status_text.text("✅ Audit Complete!")
            time.sleep(1)
            st.rerun()

# --- STEP 3: THE REPORT (Fixed & Enhanced) ---
if st.session_state.audit_results:
    st.divider()
    st.subheader("3. Audit Results")
    
    page_tabs = st.tabs(list(st.session_state.audit_results.keys()))
    
    for tab, (url, data) in zip(page_tabs, st.session_state.audit_results.items()):
        with tab:
            report = data.get("report", [])
            summary = data.get("summary", {})
            
            # --- A. METRICS ROW (Updated) ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Issues", summary.get("total", 0))
            m2.metric("🔥 Critical", summary.get("critical", 0))
            m3.metric("🔸 Serious", summary.get("serious", 0))
            m4.metric("🔹 Minor", summary.get("minor", 0)) # <--- Added Minor back
            
            st.divider()

            if not report:
                st.balloons()
                st.success("🎉 No accessibility violations found on this page!")
            else:
                # --- B. VIOLATION OVERVIEW TABLE (Restored) ---
                st.subheader("📊 Violation Overview")
                
                summary_data = []
                for i in report:
                    # SAFE KEY ACCESS
                    rule_name = i.get('rule') or i.get('rule_id') or "Unknown Rule"
                    priority = i.get('fix_priority', 'Low')
                    
                    # Clean up priority string for table (remove emojis if needed, or keep them)
                    p_label = "🔴 High" if "HIGH" in priority else "🟠 Medium" if "MEDIUM" in priority else "🔵 Low"

                    summary_data.append({
                        "Priority": p_label,
                        "Rule ID": rule_name,
                        "Description": i.get('description', 'No description'),
                        "WCAG Criteria": i.get('wcag', 'Unknown')
                    })
                
                if summary_data:
                    df = pd.DataFrame(summary_data)
                    st.dataframe(
                        df, 
                        use_container_width=True,
                        hide_index=True
                    )

                st.divider()

                # --- C. DEVELOPER TASK LIST ---
                st.subheader("🛠️ Developer Action Plan")
                
                for issue in report:
                    rule_name = issue.get('rule') or issue.get('rule_id') or "Unknown"
                    priority = issue.get('fix_priority', 'Low')
                    desc = issue.get('description', '')
                    
                    p_color = "red" if "HIGH" in priority else "orange" if "MEDIUM" in priority else "blue"
                    
                    with st.expander(f":{p_color}[{priority}] **{rule_name}**: {desc}"):
                        
                        tab_problem, tab_solution = st.tabs(["🚫 The Problem", "✅ AI Solution"])
                        
                        with tab_problem:
                            st.markdown(f"**WCAG Criteria:** {issue.get('wcag', 'Unknown')}")
                            st.markdown("**Location (CSS Selector):**")
                            st.code(issue.get('selector', 'Unknown'), language="css")
                            
                            st.markdown("**Bad Code Snippet:**")
                            st.code(issue.get('html_snippet', 'Code not available'), language="html")
                        
                        with tab_solution:
                            if issue.get("ai_explanation"):
                                st.info(f"**Why this is an error:** {issue['ai_explanation']}")
                                
                                st.markdown("**✨ AI Generated Fix:**")
                                st.code(issue['ai_fixed_code'], language="html")
                            else:
                                st.warning("AI Fix generation was skipped for this item (Limit reached).")