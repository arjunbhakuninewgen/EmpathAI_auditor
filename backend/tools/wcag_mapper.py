# backend/tools/wcag_mapper.py

"""
WCAG mapper (extended)
Maps common axe-core rule IDs to WCAG 2.1 success criteria.
Includes Level A and AA rules.
"""

# Optional: Reference path for future RAG/PDF generation features
WCAG_PDF_PATH = "/mnt/data/Web Content Accessibility Guidelines (WCAG) 2.1.pdf"

AXE_TO_WCAG = {
    # --- ARIA & Structure ---
    "aria-allowed-attr": {"wcag": "4.1.2", "title": "ARIA Attribute Allowed"},
    "aria-required-attr": {"wcag": "4.1.2", "title": "ARIA Required Attribute"},
    "aria-required-parent": {"wcag": "1.3.1", "title": "ARIA Required Parent"},
    "aria-roles": {"wcag": "4.1.2", "title": "ARIA Role Correctness"},
    "aria-valid-attr-value": {"wcag": "4.1.2", "title": "ARIA Attribute Value"},
    "aria-valid-attr": {"wcag": "4.1.2", "title": "ARIA Attribute Validity"},
    "button-name": {"wcag": "4.1.2", "title": "Button Name"},
    "role-img-alt": {"wcag": "1.1.1", "title": "Role Image Alt"},
    "duplicate-id": {"wcag": "4.1.1", "title": "Duplicate ID"},
    "duplicate-id-active": {"wcag": "4.1.1", "title": "Duplicate Active ID"},

    # --- Landmarks & Navigation ---
    "landmark-one-main": {"wcag": "1.3.1", "title": "One Main Landmark"},
    "landmark-unique": {"wcag": "1.3.1", "title": "Unique Landmarks"},
    "region": {"wcag": "1.3.1", "title": "Landmark Regions"},
    "bypass": {"wcag": "2.4.1", "title": "Bypass Blocks"},
    "skip-link": {"wcag": "2.4.1", "title": "Skip Link"},
    "document-title": {"wcag": "2.4.2", "title": "Document Title"},
    "focus-order-semantics": {"wcag": "2.4.3", "title": "Focus Order"},
    "link-name": {"wcag": "2.4.4", "title": "Link Purpose (In Context)"},
    "frame-title": {"wcag": "4.1.2", "title": "Frame Title"},
    "page-has-heading-one": {"wcag": "1.3.1", "title": "Missing H1 Heading"},

    # --- Content & Images ---
    "image-alt": {"wcag": "1.1.1", "title": "Image Alternative Text"},
    "image-redundant-alt": {"wcag": "1.1.1", "title": "Redundant Image Alt"},
    "input-image-alt": {"wcag": "1.1.1", "title": "Input Image Alt"},
    "object-alt": {"wcag": "1.1.1", "title": "Object Alternative Text"},
    "html-has-lang": {"wcag": "3.1.1", "title": "HTML Language Attribute"},
    "valid-lang": {"wcag": "3.1.1", "title": "Valid Language Code"},
    "list": {"wcag": "1.3.1", "title": "List Structure"},
    "listitem": {"wcag": "1.3.1", "title": "List Item Structure"},
    "heading-order": {"wcag": "1.3.1", "title": "Heading Hierarchy"},
    "p-as-heading": {"wcag": "1.3.1", "title": "Paragraph used as Heading"},

    # --- Color & Visual (Level AA additions) ---
    "color-contrast": {"wcag": "1.4.3", "title": "Contrast (Minimum)"},
    "meta-viewport": {"wcag": "1.4.4", "title": "Resize Text / Zoom capability"},
    "scrollable-region-focusable": {"wcag": "2.1.1", "title": "Scrollable Region Focus"},
    "css-orientation-lock": {"wcag": "1.3.4", "title": "Orientation Lock"},

    # --- Forms & Input ---
    "label": {"wcag": "3.3.2", "title": "Form Label"},
    "select-name": {"wcag": "4.1.2", "title": "Select Element Name"},
    "autocomplete-valid": {"wcag": "1.3.5", "title": "Autocomplete Validity"},

    # --- Keyboard & Interaction ---
    "tabindex": {"wcag": "2.1.1", "title": "Tabindex Usage"},
    "keyboard": {"wcag": "2.1.1", "title": "Keyboard Operable"},
    
    # --- Media ---
    "video-caption": {"wcag": "1.2.2", "title": "Video Captions"},
    "audio-caption": {"wcag": "1.2.2", "title": "Audio Captions"},

    # --- Best Practices & Structure ---
    "page-has-heading-one": {"wcag": "Best Practice", "title": "Missing H1 Heading"},
    "landmark-one-main": {"wcag": "Best Practice", "title": "Page must have one Main Landmark"},
    "region": {"wcag": "Best Practice", "title": "All content must be in a Landmark Region"},
    "meta-viewport": {"wcag": "1.4.4", "title": "Zooming must not be disabled"},
    "scope-attr-valid": {"wcag": "1.3.1", "title": "Table headers must have scope"},
}

def map_to_wcag(raw_violations):
    """
    Convert raw violations (axe or custom scanner) into mapped WCAG entries.
    """
    mapped_issues = []
    
    for violation in raw_violations:
        # Robust ID extraction
        rule_id = violation.get("id", violation.get("rule", "unknown-rule"))
        
        # Fallback: If rule isn't in our dict, use the Axe description
        default_title = violation.get("help", violation.get("message", "Accessibility Issue"))

        wcag_info = AXE_TO_WCAG.get(rule_id, {
            "wcag": "Best Practice",  # Default if unknown
            "title": f"{rule_id} ({default_title})",
            "description": violation.get("description")
        })

        # Calculate nodes count safely
        nodes = violation.get("nodes", [])
        count = len(nodes) if nodes else violation.get("count", 1)

        mapped_issues.append({
            "rule": rule_id,  # Matches frontend expectation
            "wcag": wcag_info["wcag"],
            "description": wcag_info.get("title"),
            "impact": violation.get("impact", "minor"),
            "nodes_affected": count,
            "help_url": violation.get("helpUrl") or violation.get("help_url"),
            "specific_nodes": nodes,
            "reference_pdf": WCAG_PDF_PATH
        })

    return mapped_issues