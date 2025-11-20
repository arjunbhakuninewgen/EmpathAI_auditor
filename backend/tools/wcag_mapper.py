# A larger mapping dictionary for common Axe-core rules
AXE_TO_WCAG = {
    "accesskeys": {"wcag": "2.1.1", "title": "Access Keys Usage"},
    "area-alt": {"wcag": "1.1.1", "title": "Active Area Alternative Text"},
    "aria-allowed-attr": {"wcag": "4.1.2", "title": "ARIA Attribute Allowed"},
    "aria-hidden-body": {"wcag": "4.1.2", "title": "ARIA Hidden Body"},
    "aria-required-attr": {"wcag": "4.1.2", "title": "ARIA Required Attribute"},
    "aria-roles": {"wcag": "4.1.2", "title": "ARIA Role Correctness"},
    "aria-valid-attr-value": {"wcag": "4.1.2", "title": "ARIA Attribute Value"},
    "aria-valid-attr": {"wcag": "4.1.2", "title": "ARIA Attribute Validity"},
    "audio-caption": {"wcag": "1.2.1", "title": "Audio Captioning"},
    "autocomplete-valid": {"wcag": "1.3.5", "title": "Autocomplete Validity"},
    "avoid-inline-spacing": {"wcag": "1.4.12", "title": "Inline Spacing"},
    "blink": {"wcag": "2.2.2", "title": "Blinking Content"},
    "button-name": {"wcag": "4.1.2", "title": "Button Name"},
    "bypass": {"wcag": "2.4.1", "title": "Bypass Blocks"},
    "color-contrast": {"wcag": "1.4.3", "title": "Color Contrast"},
    "css-orientation-lock": {"wcag": "1.3.4", "title": "CSS Orientation Lock"},
    "definition-list": {"wcag": "1.3.1", "title": "Definition List Structure"},
    "dlitem": {"wcag": "1.3.1", "title": "Definition List Item"},
    "document-title": {"wcag": "2.4.2", "title": "Document Title"},
    "duplicate-id-active": {"wcag": "4.1.1", "title": "Duplicate Active ID"},
    "duplicate-id": {"wcag": "4.1.1", "title": "Duplicate ID"},
    "empty-heading": {"wcag": "2.4.6", "title": "Empty Heading"},
    "focus-order-semantics": {"wcag": "2.4.3", "title": "Focus Order"},
    "form-field-multiple-labels": {"wcag": "3.3.2", "title": "Multiple Form Labels"},
    "frame-tested": {"wcag": "4.1.2", "title": "Frame Scripting"},
    "frame-title": {"wcag": "4.1.2", "title": "Frame Title"},
    "heading-order": {"wcag": "1.3.1", "title": "Heading Hierarchy"},
    "html-has-lang": {"wcag": "3.1.1", "title": "HTML Language Attribute"},
    "html-lang-valid": {"wcag": "3.1.1", "title": "HTML Language Validity"},
    "html-xml-lang-mismatch": {"wcag": "3.1.1", "title": "Language Mismatch"},
    "image-alt": {"wcag": "1.1.1", "title": "Image Alternative Text"},
    "image-redundant-alt": {"wcag": "1.1.1", "title": "Redundant Image Alt"},
    "input-image-alt": {"wcag": "1.1.1", "title": "Input Image Alt"},
    "label": {"wcag": "1.3.1", "title": "Form Label"},
    "layout-table": {"wcag": "1.3.1", "title": "Layout Table"},
    "link-in-text-block": {"wcag": "1.4.1", "title": "Link Distinction"},
    "link-name": {"wcag": "2.4.4", "title": "Link Purpose"},
    "list": {"wcag": "1.3.1", "title": "List Structure"},
    "listitem": {"wcag": "1.3.1", "title": "List Item Structure"},
    "marquee": {"wcag": "2.2.2", "title": "Marquee Usage"},
    "meta-refresh": {"wcag": "2.2.1", "title": "Meta Refresh"},
    "meta-viewport": {"wcag": "1.4.4", "title": "Meta Viewport Zoom"},
    "nested-interactive": {"wcag": "4.1.2", "title": "Nested Controls"},
    "no-autoplay-audio": {"wcag": "1.4.2", "title": "Audio Autoplay"},
    "object-alt": {"wcag": "1.1.1", "title": "Object Alternative Text"},
    "p-as-heading": {"wcag": "1.3.1", "title": "Paragraph as Heading"},
    "page-has-heading-one": {"wcag": "1.3.1", "title": "Missing H1 Heading"},
    "region": {"wcag": "1.3.1", "title": "Landmark Regions"},
    "role-img-alt": {"wcag": "1.1.1", "title": "Role Image Alt"},
    "scope-attr-valid": {"wcag": "1.3.1", "title": "Scope Attribute Validity"},
    "scrollable-region-focusable": {"wcag": "2.1.1", "title": "Scrollable Region Focus"},
    "select-name": {"wcag": "4.1.2", "title": "Select Element Name"},
    "server-side-image-map": {"wcag": "2.1.1", "title": "Server-Side Image Map"},
    "skip-link": {"wcag": "2.4.1", "title": "Skip Link"},
    "tabindex": {"wcag": "2.1.1", "title": "Tabindex Usage"},
    "table-duplicate-name": {"wcag": "1.3.1", "title": "Duplicate Table Summary"},
    "table-fake-caption": {"wcag": "1.3.1", "title": "Fake Table Caption"},
    "td-headers-attr": {"wcag": "1.3.1", "title": "Table Cell Headers"},
    "td-has-header": {"wcag": "1.3.1", "title": "Table Data Headers"},
    "th-has-data-cells": {"wcag": "1.3.1", "title": "Table Header Cells"},
    "valid-lang": {"wcag": "3.1.1", "title": "Valid Language Code"},
    "video-caption": {"wcag": "1.2.2", "title": "Video Captions"},
}

def map_to_wcag(raw_violations):
    mapped_issues = []
    
    for violation in raw_violations:
        rule_id = violation.get("id", "unknown-rule")
        
        # Improved Fallback: If rule not in dict, use the Axe description
        default_title = violation.get("help", "Accessibility Issue")
        
        wcag_info = AXE_TO_WCAG.get(rule_id, {
            "wcag": "Unknown", 
            "title": f"{rule_id} ({default_title})", # Use actual rule name if unknown
            "description": violation.get("description")
        })
        
        mapped_issues.append({
            "rule_id": rule_id,
            "wcag_sc": wcag_info["wcag"],
            "wcag_title": wcag_info["title"],
            "impact": violation.get("impact", "minor"),
            "nodes_affected": violation.get("count", 1),
            "help_url": violation.get("helpUrl"),
            "specific_nodes": violation.get("nodes", [])
        })
        
    return mapped_issues