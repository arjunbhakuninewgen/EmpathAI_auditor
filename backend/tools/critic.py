# backend/tools/critic.py

def critique_issues(issues):
    prioritized = []
    grouped = {}
    
    for issue in issues:
        rule_id = issue.get("rule", "unknown")
        
        if rule_id not in grouped:
            grouped[rule_id] = {
                "rule": rule_id,
                "description": issue.get("description", ""),
                "wcag_sc": issue.get("wcag_sc", "Unknown"),
                "fix_priority": issue.get("fix_priority", "LOW"),
                "total_occurrences": 0,
                "code_snippets": []  # <--- container for per-node HTML
            }
        
        grouped[rule_id]["total_occurrences"] += issue.get("nodes_affected", 1)
        
        # --- collect node-level snippets from wcag_mapper.enrich_with_wcag ---
        new_nodes = issue.get("specific_nodes", [])
        current_snippets = grouped[rule_id]["code_snippets"]
        
        # Only keep top 5 snippets to avoid huge payloads
        if len(current_snippets) < 5:
            current_snippets.extend(new_nodes)
            
    return list(grouped.values())
