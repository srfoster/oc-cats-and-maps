#!/usr/bin/env python3
"""
Test add_prereqs_to_plan function.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from util
sys.path.insert(0, str(Path(__file__).parent.parent))

from add_prereqs_to_plan import add_prereqs_to_plan
from util import load_prereqs, get_prereqs_path
from course_types import _is_topologically_sorted


def test_simple_prereq():
    """Test single level prerequisite."""
    plan = ['CS 143']
    result = add_prereqs_to_plan(plan)
    expected = {'CS 143', 'CS& 141'}
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert set(result) == expected, f"Expected {expected}, got {set(result)}"
    return True


def test_recursive_prereqs():
    """Test multi-level prerequisites."""
    plan = ['MATH& 151']
    result = add_prereqs_to_plan(plan)
    expected = {'MATH& 151', 'MATH& 142', 'MATH& 141', 'MATH 99'}
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert set(result) == expected, f"Expected {expected}, got {set(result)}"
    return True


def test_no_prereqs():
    """Test course with no prerequisites."""
    plan = ['ENGL& 101']
    result = add_prereqs_to_plan(plan)
    expected = {'ENGL& 101'}
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert set(result) == expected, f"Expected {expected}, got {set(result)}"
    return True


def test_empty_plan():
    """Test empty plan."""
    plan = []
    result = add_prereqs_to_plan(plan)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 0, f"Expected empty list, got {result}"
    return True


def test_multiple_courses():
    """Test plan with multiple courses."""
    plan = ['CS 143', 'MATH& 142']
    result = add_prereqs_to_plan(plan)
    expected = {'CS 143', 'CS& 141', 'MATH& 142', 'MATH& 141', 'MATH 99'}
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert set(result) == expected, f"Expected {expected}, got {set(result)}"
    return True


def test_two_level_depth():
    """Test prerequisite chain with two levels."""
    plan = ['MATH& 142']
    result = add_prereqs_to_plan(plan)
    expected = {'MATH& 142', 'MATH& 141', 'MATH 99'}
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert set(result) == expected, f"Expected {expected}, got {set(result)}"
    return True


def test_returns_list():
    """Test that result is a list, not a set."""
    plan = ['CS 143']
    result = add_prereqs_to_plan(plan)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    return True


def test_topological_sorting_simple():
    """Test that result is topologically sorted (simple case)."""
    plan = ['CS 143']
    result = add_prereqs_to_plan(plan)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert _is_topologically_sorted(result), f"Result not topologically sorted: {result}"
    # CS& 141 must come before CS 143
    if 'CS& 141' in result and 'CS 143' in result:
        idx_141 = result.index('CS& 141')
        idx_143 = result.index('CS 143')
        assert idx_141 < idx_143, f"CS& 141 (index {idx_141}) must come before CS 143 (index {idx_143})"
    return True


def test_topological_sorting_chain():
    """Test topological sorting with a prerequisite chain."""
    plan = ['MATH& 151']
    result = add_prereqs_to_plan(plan)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert _is_topologically_sorted(result), f"Result not topologically sorted: {result}"
    # MATH 99 -> MATH& 141 -> MATH& 142 -> MATH& 151
    expected_order = ['MATH 99', 'MATH& 141', 'MATH& 142', 'MATH& 151']
    for i, course in enumerate(expected_order[:-1]):
        next_course = expected_order[i + 1]
        if course in result and next_course in result:
            idx_current = result.index(course)
            idx_next = result.index(next_course)
            assert idx_current < idx_next, f"{course} must come before {next_course}"
    return True


def test_topological_sorting_unsorted_input():
    """Test that topological sorting works even when input is unsorted."""
    # Input plan in reverse order (courses before their prereqs)
    plan = ['MATH& 151', 'CS 143']
    result = add_prereqs_to_plan(plan)
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert _is_topologically_sorted(result), f"Result not topologically sorted: {result}"
    return True


def main():
    tests = [
        ("Simple prerequisite", test_simple_prereq),
        ("Recursive prerequisites", test_recursive_prereqs),
        ("No prerequisites", test_no_prereqs),
        ("Empty plan", test_empty_plan),
        ("Multiple courses", test_multiple_courses),
        ("Two level depth", test_two_level_depth),
        ("Returns list", test_returns_list),
        ("Topological sorting (simple)", test_topological_sorting_simple),
        ("Topological sorting (chain)", test_topological_sorting_chain),
        ("Topological sorting (unsorted input)", test_topological_sorting_unsorted_input),
    ]
    
    print("=" * 60)
    print("TEST: Prerequisite Resolution")
    print("=" * 60)
    print()
    
    all_passed = True
    for name, test_func in tests:
        try:
            test_func()
            print(f"[PASS] {name}")
        except AssertionError as e:
            print(f"[FAIL] {name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"[FAIL] {name}: Unexpected error: {e}")
            all_passed = False
    
    print()
    if all_passed:
        print("[PASS] TEST PASSED: All prerequisite resolution tests passed")
        return 0
    else:
        print("[FAIL] TEST FAILED: Some prerequisite resolution tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
