def critique_issues(issues):
    """
    Analyzes the list of issues and prioritizes them.
    Returns a cleaner, prioritized list.
    """
    prioritized = []
    
# 1. Group by Rule ID (deduplication)
    grouped = {}
    for issue in issues:
        rule = issue["rule_id"]
        if rule not in grouped:
            grouped[rule] = {
                "rule": rule,
                "impact": issue["impact"],
                "wcag": issue.get("wcag_sc", "Best Practice"),
                "description": issue.get("wcag_title", "General Issue"),
                "total_occurrences": 0,
                "fix_priority": "Low",
                "code_snippets": [] # <--- New List
            }
        
        # Sum the counts
        grouped[rule]["total_occurrences"] += issue["nodes_affected"]
        
        # Collect the code snippets (Limit to first 5 to avoid huge JSON)
        if len(grouped[rule]["code_snippets"]) < 5:
            grouped[rule]["code_snippets"].extend(issue.get("specific_nodes", []))
    # 2. Assign Priority Logic (Rule-based AI)
    for rule_id, data in grouped.items():
        # Critical impact or WCAG A level gets High priority
        if data["impact"] == 'critical':
            data["fix_priority"] = "🔥 HIGH - Fix Immediately"
        elif data["impact"] == 'serious':
            data["fix_priority"] = "🔸 MEDIUM - Fix Next"
        else:
            data["fix_priority"] = "🔹 LOW - Backlog"
            
        prioritized.append(data)

    # 3. Sort by Priority (High -> Low)
    # We sort by impact string reverse alphabetically just as a simple hack
    # (Critical < Serious < Moderate) isn't alphabetical, so we stick to the assigned label
    prioritized.sort(key=lambda x: x["fix_priority"], reverse=True)
    
    return prioritized