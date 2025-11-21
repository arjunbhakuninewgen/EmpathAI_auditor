from typing import List, TypedDict, Optional

# 1. Define the structure of a single "Issue"
class AccessibilityIssue(TypedDict):
    rule_id: str
    description: str
    impact: str
    wcag: str
    selector: str
    html_snippet: str
    fix_priority: str
    
    # The Fixer Agent will add these fields later:
    ai_explanation: Optional[str]
    ai_fixed_code: Optional[str]

# 2. Define the Graph State (The Shared Memory)
class AuditState(TypedDict):
    url: str
    screenshot_b64: Optional[str]
    
    # Step 1: Raw data from Scanner
    raw_violations: List[dict] 
    
    # Step 2: Filtered & Prioritized by Critic
    critiqued_issues: List[AccessibilityIssue]
    
    # Step 3: Solved by Fixer (Final Output)
    final_report: List[AccessibilityIssue]