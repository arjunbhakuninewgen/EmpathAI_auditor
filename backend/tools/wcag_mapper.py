# backend/tools/wcag_mapper.py
"""
EmpathAI v2.0 — Complete WCAG 2.1 + 2.2 Mapper
Used by Critic Node to give intelligent, future-aware feedback.
Includes Indian Law (GIGW / IS 17802) prioritization.
"""

WCAG_REFERENCE = "https://www.w3.org/TR/WCAG22/"

WCAG_RULES = {
    # ==================== CORE RULES (WCAG 2.1 & 2.2) ====================
    "accesskeys":            {"sc": "2.1.4", "level": "A",  "since": "2.1", "title": "Character Key Shortcuts", "india_priority": "LOW"},
    "aria-allowed-attr":     {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-hidden-body":      {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-hidden-focus":     {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-input-field-name": {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-required-attr":    {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-required-children":{"sc": "1.3.1", "level": "A",  "since": "2.1", "title": "Info and Relationships", "india_priority": "MEDIUM"},
    "aria-roles":            {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-valid-attr-value": {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "aria-valid-attr":       {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "HIGH"},
    "button-name":           {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "CRITICAL"},
    "bypass":                {"sc": "2.4.1", "level": "A",  "since": "2.1", "title": "Bypass Blocks", "india_priority": "HIGH"},
    "color-contrast":        {"sc": "1.4.3", "level": "AA", "since": "2.1", "title": "Contrast (Minimum)", "india_priority": "CRITICAL"},
    "document-title":        {"sc": "2.4.2", "level": "A",  "since": "2.1", "title": "Page Titled", "india_priority": "HIGH"},
    "frame-title":           {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "MEDIUM"},
    "html-has-lang":         {"sc": "3.1.1", "level": "A",  "since": "2.1", "title": "Language of Page", "india_priority": "HIGH"},
    "html-lang-valid":       {"sc": "3.1.1", "level": "A",  "since": "2.1", "title": "Language of Page", "india_priority": "HIGH"},
    "image-alt":             {"sc": "1.1.1", "level": "A",  "since": "2.1", "title": "Non-text Content", "india_priority": "CRITICAL"},
    "input-image-alt":       {"sc": "1.1.1", "level": "A",  "since": "2.1", "title": "Non-text Content", "india_priority": "CRITICAL"},
    "label":                 {"sc": "3.3.2", "level": "A",  "since": "2.1", "title": "Labels or Instructions", "india_priority": "CRITICAL"},
    "link-name":             {"sc": "2.4.4", "level": "A",  "since": "2.1", "title": "Link Purpose (In Context)", "india_priority": "HIGH"},
    "meta-viewport":         {"sc": "1.4.4", "level": "AA", "since": "2.1", "title": "Resize Text", "india_priority": "MEDIUM"},
    "tabindex":              {"sc": "2.1.1", "level": "A",  "since": "2.1", "title": "Keyboard", "india_priority": "MEDIUM"},
    "select-name":           {"sc": "4.1.2", "level": "A",  "since": "2.1", "title": "Name, Role, Value", "india_priority": "CRITICAL"},

    # ==================== NEW IN WCAG 2.2 ONLY ====================
    "focus-not-obscured":                {"sc": "2.4.11", "level": "AA", "since": "2.2", "title": "Focus Not Obscured", "india_priority": "MEDIUM"},
    "focus-appearance":                  {"sc": "2.4.11", "level": "AA", "since": "2.2", "title": "Focus Appearance", "india_priority": "MEDIUM"},
    "target-size":                       {"sc": "2.5.8",  "level": "AA", "since": "2.2", "title": "Target Size (Minimum)", "india_priority": "MEDIUM"},
    "dragging-movements":                {"sc": "2.5.7",  "level": "A",  "since": "2.2", "title": "Dragging Movements", "india_priority": "LOW"},
    "consistent-help":                   {"sc": "3.2.6",  "level": "A",  "since": "2.2", "title": "Consistent Help", "india_priority": "LOW"},
    "redundant-entry":                   {"sc": "3.3.7",  "level": "A",  "since": "2.2", "title": "Redundant Entry", "india_priority": "LOW"},
    "accessible-authentication-minimum": {"sc": "3.3.8",  "level": "A",  "since": "2.2", "title": "Accessible Authentication", "india_priority": "MEDIUM"},

    # ==================== BEST PRACTICES (not strict WCAG) ====================
    "heading-order":        {"sc": "G130", "level": "Best", "since": "2.1", "title": "Heading Order", "india_priority": "MEDIUM"},
    "landmark-one-main":    {"sc": "Best", "level": "Best", "since": "2.1", "title": "One Main Landmark", "india_priority": "MEDIUM"},
    "page-has-heading-one": {"sc": "Best", "level": "Best", "since": "2.1", "title": "Page should have <h1>", "india_priority": "HIGH"},
    "region":               {"sc": "Best", "level": "Best", "since": "2.1", "title": "Landmark Regions", "india_priority": "MEDIUM"},
}

# --- GIGW 3.0 MAPPING (India Specific) ---
# Guidelines for Indian Government Websites 3.0
GIGW_MAPPING = {
    "1.1.1": "9.1.1 (Non-text Content)",
    "1.3.1": "9.1.3 (Info and Relationships)",
    "1.4.3": "9.1.4 (Contrast Minimum)",
    "2.1.1": "9.2.1 (Keyboard)",
    "2.4.1": "9.2.4 (Bypass Blocks)",
    "2.4.2": "9.2.4 (Page Titled)",
    "2.4.4": "9.2.4 (Link Purpose)",
    "3.1.1": "9.3.1 (Language of Page)",
    "3.3.2": "9.3.3 (Labels or Instructions)",
    "4.1.2": "9.4.1 (Name, Role, Value)"
}

def enrich_with_wcag(violation: dict) -> dict:
    rule_id = violation.get("id", "unknown")
    
    # Get Rule Data
    data = WCAG_RULES.get(rule_id, {
        "sc": "Unknown", "level": "?", "since": "2.1",
        "title": violation.get("help", rule_id), "india_priority": "LOW"
    })

    # You can keep/extend your priority calculation logic here
    india_priority = data.get("india_priority", "LOW")
    # ...

    # --- CRITICAL: PASS 'nodes' TO 'specific_nodes' ---
    # `dom_scanner` already normalized Axe nodes into:
    #   { "html": "<button>Buy</button>", "target": "button.buy" }
    specific_nodes = violation.get("nodes", [])
    
    # --- GIGW 3.0 ENRICHMENT ---
    wcag_sc = data.get("sc", "Unknown")
    gigw_checkpoint = GIGW_MAPPING.get(wcag_sc, "N/A - Best Practice")

    return {
        **violation,
        "rule": rule_id,
        "wcag_sc": wcag_sc,
        "wcag_title": data.get("title", "Accessibility Issue"),
        "gigw_checkpoint": gigw_checkpoint, # New GIGW field
        "fix_priority": "HIGH" if india_priority == "CRITICAL" else "MEDIUM",
        "specific_nodes": specific_nodes,  # <--- used later by critic.py
        "india_priority": india_priority
    }