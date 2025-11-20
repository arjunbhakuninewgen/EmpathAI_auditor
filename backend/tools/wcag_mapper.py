# This maps technical "Axe" Rule IDs to official WCAG Success Criteria
AXE_TO_WCAG = {
    "image-alt": {
        "wcag": "1.1.1",
        "title": "Non-text Content",
        "description": "Images must have text alternatives that describe their purpose."
    },
    "color-contrast": {
        "wcag": "1.4.3",
        "title": "Contrast (Minimum)",
        "description": "The visual presentation of text must have a contrast ratio of at least 4.5:1."
    },
    "html-has-lang": {
        "wcag": "3.1.1",
        "title": "Language of Page",
        "description": "The default language of each Web page can be programmatically determined."
    },
    "label": {
        "wcag": "3.3.2",
        "title": "Labels or Instructions",
        "description": "Labels or instructions are provided when content requires user input."
    }
}

def map_to_wcag(raw_violations):
    """
    Takes raw axe-core violations and attaches WCAG legal data.
    """
    mapped_issues = []
    
    for violation in raw_violations:
        rule_id = violation.get("id") # e.g., "image-alt"
        
        # Look up the rule in our dictionary, or use defaults
        wcag_info = AXE_TO_WCAG.get(rule_id, {
            "wcag": "Unknown", 
            "title": "General Accessibility Issue",
            "description": violation.get("description")
        })
        
        mapped_issues.append({
            "rule_id": rule_id,
            "wcag_sc": wcag_info["wcag"],
            "wcag_title": wcag_info["title"],
            "impact": violation.get("impact"),
            "nodes_affected": violation.get("count", 1),
            "help_url": violation.get("helpUrl"),
            "specific_nodes": violation.get("nodes", []) # <--- Pass it along
        })
        
    return mapped_issues