def critique_issues(issues):
    """
    Analyzes the list of issues and prioritizes them.
    Returns a cleaner, prioritized list.
    """
    prioritized = []
    
    # 1. Group by Rule ID (deduplication)
    grouped = {}
    for issue in issues:
        # --- FIX: Handle both 'rule' and 'rule_id' keys safely ---
        rule = issue.get("rule") or issue.get("rule_id") or "unknown-rule"
        
        if rule not in grouped:
            grouped[rule] = {
                "rule": rule,
                "impact": issue.get("impact", "minor"),
                "wcag": issue.get("wcag", "Best Practice"),
                "description": issue.get("description", "General Issue"),
                "total_occurrences": 0,
                "fix_priority": "Low",
                "code_snippets": [] 
            }
        
        # Sum the counts
        grouped[rule]["total_occurrences"] += issue.get("nodes_affected", 1)
        
        # Collect the code snippets (Limit to first 5 to avoid huge JSON)
        if len(grouped[rule]["code_snippets"]) < 5:
            # Handle specific_nodes list
            nodes = issue.get("specific_nodes", [])
            grouped[rule]["code_snippets"].extend(nodes)

    # 2. Assign Priority Logic (Rule-based AI)
    for rule_id, data in grouped.items():
        impact = data["impact"]
        
        # Critical impact or WCAG A level gets High priority
        if impact == 'critical':
            data["fix_priority"] = "🔥 HIGH - Fix Immediately"
        elif impact == 'serious':
            data["fix_priority"] = "🔸 MEDIUM - Fix Next"
        else:
            data["fix_priority"] = "🔹 LOW - Backlog"
            
        prioritized.append(data)

    # 3. Sort by Priority (High -> Low)
    prioritized.sort(key=lambda x: x["fix_priority"], reverse=True)
    
    return prioritized