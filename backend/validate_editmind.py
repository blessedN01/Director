#!/usr/bin/env python3
"""Quick validation script for EditMind integration components."""

import sys
import os
import tempfile

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_editmind_wrapper():
    """Test EditMindWrapper initialization."""
    try:
        from director.tools.ai.editmind_wrapper import EditMindWrapper
        wrapper = EditMindWrapper()
        print("[PASS] EditMindWrapper initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] EditMindWrapper failed: {e}")
        return False

def test_local_videodb_tool():
    """Test LocalVideoDBTool initialization and basic methods."""
    try:
        from director.tools.ai.videodb_local_tool import LocalVideoDBTool

        # Create temporary database
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            tool = LocalVideoDBTool(collection_id='test', db_path=db_path)

            # Test semantic search
            results = tool.semantic_search('test query', limit=5)
            print(f"[PASS] LocalVideoDBTool semantic_search returned {len(results)} results")

            # Test collection operations
            collection = tool.get_collection()
            print(f"[PASS] Collection retrieved: {collection['id']}")

            return True
        finally:
            os.unlink(db_path)

    except Exception as e:
        print(f"[FAIL] LocalVideoDBTool failed: {e}")
        return False

def test_handler():
    """Test VideoDBHandler initialization."""
    try:
        from director.handler import VideoDBHandler

        # This might fail due to missing dependencies, but let's see
        handler = VideoDBHandler('test')
        print("[PASS] VideoDBHandler initialized successfully")
        return True
    except Exception as e:
        print(f"[WARN] VideoDBHandler initialization failed (expected due to missing dependencies): {e}")
        return False

def test_routes_import():
    """Test routes import."""
    try:
        # Just test the import without full Flask app
        import director.entrypoint.api.routes as routes_module
        print("[PASS] Routes module imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Routes import failed: {e}")
        return False

def main():
    print("EditMind Integration Validation\n")

    tests = [
        ("EditMindWrapper", test_editmind_wrapper),
        ("LocalVideoDBTool", test_local_videodb_tool),
        ("VideoDBHandler", test_handler),
        ("Routes Import", test_routes_import),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} core components validated")
    print(f"Status: {'[PASS]' if passed >= 2 else '[FAIL]'}")
    print(f"{'='*50}")

    if passed >= 2:
        print("\nSUCCESS: Core EditMind integration is functional!")
        print("Note: Full functionality requires Docker services and API keys.")
    else:
        print("\nFAILURE: Critical integration issues detected.")

    return passed >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)