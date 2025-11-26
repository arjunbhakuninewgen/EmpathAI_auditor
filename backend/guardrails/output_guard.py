import re

def validate_fix(fix_code: str) -> str:
    """
    Sanitizes the AI-generated fix code to prevent injection of malicious scripts.
    Removes:
    - <script> tags
    - javascript: URIs
    - Event handlers (onclick, onload, etc.)
    """
    if not fix_code:
        return ""

    original_code = fix_code
    
    # 1. Remove <script> tags (case insensitive)
    fix_code = re.sub(r'<script\b[^>]*>.*?</script>', '', fix_code, flags=re.IGNORECASE | re.DOTALL)
    
    # 2. Remove javascript: protocol
    fix_code = re.sub(r'javascript:', '', fix_code, flags=re.IGNORECASE)
    
    # 3. Remove inline event handlers (e.g., onclick=...)
    fix_code = re.sub(r'\son\w+="[^"]*"', '', fix_code, flags=re.IGNORECASE)
    fix_code = re.sub(r"\son\w+='[^']*'", '', fix_code, flags=re.IGNORECASE)

    if fix_code != original_code:
        print("🛡️ OUTPUT GUARD: Sanitized unsafe code in fix.")
        # Add a comment indicating sanitization
        return fix_code + "\n<!-- EmpathAI Guard: Unsafe content removed -->"

    return fix_code
