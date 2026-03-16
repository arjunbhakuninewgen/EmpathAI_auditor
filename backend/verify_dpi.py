import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph.workflow import audit_graph
from backend.tools.wcag_mapper import enrich_with_wcag

async def test_dpi():
    print("🇮🇳 Starting DPI Verification Test...")
    
    # 1. Test GIGW Mapping
    print("\n--- Test Case 1: GIGW 3.0 Mapping ---")
    sample_violation = {"id": "color-contrast", "help": "Elements must have sufficient color contrast"}
    enriched = enrich_with_wcag(sample_violation)
    
    if "gigw_checkpoint" in enriched:
        print(f"✅ GIGW Mapping Success: {enriched['rule']} -> {enriched['gigw_checkpoint']}")
    else:
        print("❌ GIGW Mapping Failed: 'gigw_checkpoint' missing")

    # 2. Test Bhashini Integration (via Workflow)
    print("\n--- Test Case 2: Bhashini Translation in Workflow ---")
    # We use a real URL but rely on the mock Bhashini service we wrote
    state = {"url": "https://example.com"}
    
    try:
        result = await audit_graph.ainvoke(state)
        report = result.get("final_report", [])
        
        if report:
            first_issue = report[0]
            if "hindi_explanation" in first_issue:
                print(f"✅ Bhashini Success: Found Hindi explanation.")
                print(f"   English: {first_issue.get('ai_explanation', 'N/A')[:50]}...")
                print(f"   Hindi:   {first_issue['hindi_explanation'][:50]}...")
            else:
                print("⚠️ Bhashini Warning: 'hindi_explanation' missing in first issue (might be no issues found).")
        else:
            print("ℹ️ No issues found to translate (expected for clean site).")
            
    except Exception as e:
        print(f"❌ Workflow Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_dpi())
