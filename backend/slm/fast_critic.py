import re

def fast_critique(issues: list) -> list:
    """
    SLM / Heuristic Layer:
    Quickly filters out obvious false positives or low-value issues 
    BEFORE sending them to the expensive LLM.
    
    This acts as a 'Small Language Model' logic layer.
    """
    print(f"⚡ SLM: Fast Critiquing {len(issues)} issues...")
    
    valid_issues = []
    
    for issue in issues:
        rule = issue.get("id", "")
        impact = issue.get("impact", "")
        
        # 1. Filter out minor contrast issues that are often false positives
        if rule == "color-contrast" and impact == "minor":
            continue
            
        # 2. Filter out 'region' issues which are often noise
        if rule == "region":
            continue
            
        # 3. Deduplicate based on selector (simple heuristic)
        # (This is a simplified version of what the full critic does)
        
        valid_issues.append(issue)

    print(f"⚡ SLM: Reduced to {len(valid_issues)} high-value issues.")
    return valid_issues
