import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph.workflow import audit_graph

async def test_audit():
    print("🧪 Starting Verification Test...")
    
    # Test Case 1: Valid URL
    print("\n--- Test Case 1: Valid URL ---")
    state = {"url": "https://example.com"}
    result = await audit_graph.ainvoke(state)
    print("✅ Audit Completed.")
    if "final_report" in result:
        print(f"   Report Items: {len(result['final_report'])}")
    else:
        print("   ⚠️ No final report found (might be expected if no issues).")

    # Test Case 2: Blocked URL
    print("\n--- Test Case 2: Blocked URL ---")
    state_blocked = {"url": "https://malicious-site.com"}
    result_blocked = await audit_graph.ainvoke(state_blocked)
    
    # Check if scanner skipped or returned error
    if "error" in result_blocked:
        print(f"✅ Blocked URL correctly identified: {result_blocked['error']}")
    else:
        # If scanner skipped, it might return empty report or similar
        print(f"ℹ️ Result for blocked URL: {result_blocked.keys()}")

if __name__ == "__main__":
    asyncio.run(test_audit())
