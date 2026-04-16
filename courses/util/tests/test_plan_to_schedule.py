#!/usr/bin/env python3
"""Test plan_to_schedule functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from plan_to_schedule import plan_to_schedule, current_quarter, next_quarter
from datetime import date

def test_current_quarter():
    """Test current quarter detection"""
    assert current_quarter(date(2026, 3, 31)) == ("Winter", 2026)
    assert current_quarter(date(2026, 4, 1)) == ("Spring", 2026)
    assert current_quarter(date(2026, 7, 15)) == ("Summer", 2026)
    assert current_quarter(date(2026, 10, 1)) == ("Fall", 2026)
    print("[PASS] Current quarter detection")

def test_next_quarter():
    """Test quarter advancement"""
    assert next_quarter("Fall", 2026) == ("Winter", 2027)
    assert next_quarter("Winter", 2027) == ("Spring", 2027)
    assert next_quarter("Spring", 2027) == ("Summer", 2027)
    assert next_quarter("Summer", 2027) == ("Fall", 2027)
    print("[PASS] Next quarter advancement")

def test_simple_schedule():
    """Test scheduling a simple course"""
    # Just CIS 110 with no prereqs
    courses = ["CIS 110"]
    taken = []
    schedule = plan_to_schedule(courses, taken)
    
    if schedule is None:
        print("[FAIL] Could not generate schedule for CIS 110")
        return False
    
    # Should schedule in Summer 2026 or later
    assert len(schedule) >= 1
    assert schedule[0][0] == "CIS 110"
    print(f"[PASS] Simple schedule: {schedule}")
    return True

def test_with_prereq():
    """Test scheduling courses with prerequisites"""
    # CS 143 requires CS& 141
    courses = ["CS 143"]
    taken = []
    
    schedule = plan_to_schedule(courses, taken)
    
    if schedule is None:
        print("[FAIL] Could not generate schedule for CS 143")
        return False
    
    # Should have both CS& 141 (prereq) and CS 143
    course_ids = [s[0] for s in schedule]
    assert "CS& 141" in course_ids
    assert "CS 143" in course_ids
    
    # CS& 141 should come before CS 143
    idx_141 = course_ids.index("CS& 141")
    idx_143 = course_ids.index("CS 143")
    assert idx_141 < idx_143
    
    # CS& 141 should be in an earlier quarter than CS 143
    quarter_141 = schedule[idx_141][1]
    year_141 = schedule[idx_141][2]
    quarter_143 = schedule[idx_143][1]
    year_143 = schedule[idx_143][2]
    
    quarters = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
    assert (year_141, quarters[quarter_141]) < (year_143, quarters[quarter_143])
    
    print(f"[PASS] Schedule with prereq: {schedule}")
    return True


def test_prereq_same_quarter():
    """Test that scheduling prereq and course in same quarter is invalid"""
    from course_types import is_course_schedule
    
    # CS 143 requires CS& 141 - both in same quarter should fail
    schedule = [("CS& 141", "Spring", 2026), ("CS 143", "Spring", 2026)]
    
    assert not is_course_schedule(schedule), "Should reject prereq in same quarter"
    print("[PASS] Prereq in same quarter correctly rejected")
    return True

def test_with_taken_courses():
    """Test scheduling when some courses already taken"""
    courses = ["CS 143"]
    taken = ["CS& 141"]
    schedule = plan_to_schedule(courses, taken)
    
    if schedule is None:
        print("[FAIL] Could not generate schedule with taken courses")
        return False
    
    # Should only have CS 143 (not CS& 141 since it's taken)
    course_ids = [s[0] for s in schedule]
    assert "CS& 141" not in course_ids
    assert "CS 143" in course_ids
    
    print(f"[PASS] Schedule with taken courses: {schedule}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Plan to Schedule")
    print("=" * 60)
    print()
    
    try:
        test_current_quarter()
        test_next_quarter()
        test_simple_schedule()
        test_with_prereq()
        test_prereq_same_quarter()
        test_with_taken_courses()
        print()
        print("[PASS] TEST PASSED: All plan to schedule tests passed")
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
