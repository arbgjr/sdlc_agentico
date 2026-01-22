#!/usr/bin/env python3
"""
Integration Test for Parallel Workers

Tests basic functionality of the parallel-workers skill.
"""

import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from worker_manager import WorkerManager
from state_tracker import StateTracker, WorkerState


def test_worker_lifecycle():
    """Test complete worker lifecycle"""
    print("Testing worker lifecycle...")

    # Initialize
    manager = WorkerManager("test-project")
    tracker = StateTracker()

    # Test 1: Spawn worker
    print("  [1/5] Testing worker spawn...")
    result = manager.spawn(
        task_id="test-task-001",
        description="Test task",
        agent="code-author",
        base_branch="main"
    )

    assert result["success"], "Worker spawn failed"
    assert "worker_id" in result, "No worker_id returned"

    worker_id = result["worker_id"]
    print(f"    ✓ Worker spawned: {worker_id}")

    # Test 2: Verify state
    print("  [2/5] Testing state retrieval...")
    state = tracker.get(worker_id)
    assert state["exists"], "Worker state not found"
    assert state["state"] == WorkerState.NEEDS_INIT.value, "Wrong initial state"
    print("    ✓ State retrieved correctly")

    # Test 3: State transition
    print("  [3/5] Testing state transition...")
    success = tracker.transition(
        worker_id,
        WorkerState.NEEDS_INIT,
        WorkerState.WORKING
    )
    assert success, "State transition failed"

    state = tracker.get(worker_id)
    assert state["state"] == WorkerState.WORKING.value, "State not updated"
    print("    ✓ State transitioned correctly")

    # Test 4: Invalid transition
    print("  [4/5] Testing invalid transition...")
    success = tracker.transition(
        worker_id,
        WorkerState.WORKING,
        WorkerState.NEEDS_INIT  # Invalid transition
    )
    assert not success, "Invalid transition allowed"
    print("    ✓ Invalid transition blocked")

    # Test 5: Cleanup
    print("  [5/5] Testing cleanup...")
    result = manager.terminate(worker_id, force=True)
    assert result["success"], "Cleanup failed"

    state = tracker.get(worker_id)
    assert not state.get("exists", True), "State not removed"
    print("    ✓ Worker cleaned up")

    print("✅ All tests passed!\n")


def test_simple_store():
    """Test simple memory store"""
    print("Testing simple memory store...")

    sys.path.insert(0, str(Path(__file__).parents[2] / "memory-manager" / "scripts"))
    from simple_store import SimpleStore

    # Use temp directory for tests
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SimpleStore(Path(tmpdir))

        # Test 1: Add fact
        print("  [1/4] Testing add fact...")
        fact_id = store.add_fact("Test fact", tags=["test"], project="test-project")
        assert fact_id, "Fact not added"
        print(f"    ✓ Fact added: {fact_id}")

        # Test 2: Recall fact
        print("  [2/4] Testing recall...")
        facts = store.recall_facts(query="test", project="test-project")
        assert len(facts) > 0, "Fact not recalled"
        assert facts[0]["text"] == "Test fact", "Wrong fact text"
        print("    ✓ Fact recalled correctly")

        # Test 3: Add tool
        print("  [3/4] Testing add tool...")
        store.add_tool("test-tool", repo="https://example.com", version="1.0.0")
        tool = store.get_tool("test-tool")
        assert tool, "Tool not added"
        assert tool["version"] == "1.0.0", "Wrong tool version"
        print("    ✓ Tool added correctly")

        # Test 4: Search
        print("  [4/4] Testing search...")
        results = store.search("test")
        assert len(results["facts"]) > 0, "Fact not in search results"
        assert len(results["tools"]) > 0, "Tool not in search results"
        print("    ✓ Search works correctly")

    print("✅ All tests passed!\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("SDLC Agêntico - Parallel Workers Integration Tests")
    print("=" * 60)
    print()

    try:
        test_worker_lifecycle()
        test_simple_store()

        print("=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        sys.exit(0)

    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        sys.exit(1)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
