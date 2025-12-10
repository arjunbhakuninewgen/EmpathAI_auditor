# backend/graph/state.py

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AccessibilityIssue(TypedDict, total=False):
    rule: str
    description: str
    impact: str
    wcag_sc: str
    wcag_title: str
    selector: str
    html_snippet: str
    fix_priority: str
    # New Flags
    category: str  # 'syntax', 'semantic', 'interaction', 'visual'
    ai_explanation: Optional[str]
    ai_fixed_code: Optional[str]

class AuditState(TypedDict):
    url: str
    screenshot_b64: Optional[str]
    dom_hash: Optional[str]  # For cache key
    
    # RAW DATA
    raw_violations: List[Dict[Any, Any]] # Axe (Syntax)
    dom_content: Dict[str, Any]          # New: For Semantic Analysis
    tab_log: List[Dict[str, Any]]        # New: For Interaction Analysis (FIXED: was tab_order_log)

    # ISSUES LISTS
    critiqued_issues: List[AccessibilityIssue] # Syntax
    vision_issues: List[AccessibilityIssue]    # Visual
    semantic_issues: List[AccessibilityIssue]  # Meaning (New)
    interaction_issues: List[AccessibilityIssue] # State (New)

    # Final output
    final_report: List[AccessibilityIssue]  