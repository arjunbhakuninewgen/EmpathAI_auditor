# backend/graph/state.py
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

# Single issue (shared format)
class AccessibilityIssue(TypedDict, total=False):
    rule: str
    description: str
    impact: str
    wcag_sc: str
    wcag_title: str
    selector: str
    html_snippet: str
    fix_priority: str
    is_vision: bool
    version_badge: str
    ai_explanation: Optional[str]
    ai_fixed_code: Optional[str]
    india_priority: Optional[str]
    learn_more: Optional[str]


# Main graph state
class AuditState(TypedDict):
    url: str
    screenshot_b64: Optional[str]
    page_title: Optional[str]

    # Scanner → Critic
    raw_violations: List[Dict[Any, Any]]
    critiqued_issues: List[AccessibilityIssue]

    # Vision Analyzer
    vision_issues: List[AccessibilityIssue]

    # Final output
    final_report: List[AccessibilityIssue]