#!/usr/bin/env python3
"""
Test course schedule validation functions.
"""

import sys
from pathlib import Path

# Add parent directory to path to import from util
sys.path.insert(0, str(Path(__file__).parent.parent))

from course_types import is_scheduled_course, is_course_schedule


def test_is_scheduled_course_valid():
    """Test valid scheduled courses."""
    assert is_scheduled_course(('CIS 110', 'Fall', 2026))
    assert is_scheduled_course(['MATH& 141', 'Winter', 2027])
    assert is_scheduled_course(('ENGL& 101', 'Spring', 2026))
    assert is_scheduled_course(('CS 143', 'Summer', 2026))
    return True


def test_is_scheduled_course_invalid():
    """Test invalid scheduled courses."""
    assert not is_scheduled_course(('CIS 110', 'Fall'))  # Missing year
    assert not is_scheduled_course(('CIS 110', 'Fall', 2026, 'extra'))  # Too many
    assert not is_scheduled_course(('CIS 110', 'Invalid', 2026))  # Invalid quarter
    assert not is_scheduled_course(('CIS 110', 'Fall', '2026'))  # Year not int
    assert not is_scheduled_course('not a tuple')  # Wrong type
    return True


def test_is_course_schedule_valid():
    """Test valid course schedule."""
    # Simple schedule with prereqs satisfied
    schedule = [
        ('MATH 99', 'Spring', 2026),
        ('MATH& 141', 'Summer', 2026),
    ]
    assert is_course_schedule(schedule)
    return True


def test_is_course_schedule_empty():
    """Test empty schedule."""
    assert is_course_schedule([])
    return True


def test_is_course_schedule_wrong_order():
    """Test schedule with courses in wrong topological order."""
    # CS 143 before its prereq CS& 141
    schedule = [
        ('CS 143', 'Spring', 2026),
        ('CS& 141', 'Winter', 2027),
    ]
    assert not is_course_schedule(schedule)
    return True


def test_is_course_schedule_missing_prereq():
    """Test schedule missing prerequisites."""
    schedule = [
        ('CS 143', 'Spring', 2026),  # Missing CS& 141 prereq
    ]
    assert not is_course_schedule(schedule)
    return True


def test_is_course_schedule_not_offered():
    """Test schedule with course not offered in that quarter/year."""
    # CIS 247 is only offered in Fall 2026, not Spring
    schedule = [
        ('CIS 247', 'Spring', 2026),
    ]
    assert not is_course_schedule(schedule)
    return True


def test_is_course_schedule_wrong_temporal_order():
    """Test schedule with courses not in temporal order."""
    # Fall 2026 before Spring 2026 - wrong order (Spring comes before Fall in calendar)
    schedule = [
        ('ENGL& 101', 'Fall', 2026),
        ('ENGL& 235', 'Spring', 2026),
    ]
    assert not is_course_schedule(schedule)
    return True


def test_is_course_schedule_temporal_order_across_years():
    """Test temporal ordering across years."""
    # Summer 2026 after Spring 2027 - wrong order
    schedule = [
        ('ENGL& 101', 'Summer', 2027),
        ('ENGL& 235', 'Spring', 2027),
    ]
    assert not is_course_schedule(schedule)
    return True


def test_courses_taken_satisfies_prereq():
    """Test that courses_taken can satisfy prerequisites."""
    # CS 143 requires CS& 141, but CS& 141 is already taken
    schedule = [
        ('CS 143', 'Spring', 2026),
    ]
    courses_taken = ['CS& 141']
    assert is_course_schedule(schedule, courses_taken)
    return True


def test_courses_taken_allows_topological_order():
    """Test that courses_taken affects topological ordering."""
    # Without courses_taken, MATH& 142 needs MATH& 141 first
    schedule = [
        ('MATH& 142', 'Spring', 2026),
    ]
    assert not is_course_schedule(schedule)
    
    # With MATH& 141 already taken, it's valid
    courses_taken = ['MATH& 141', 'MATH 99']
    assert is_course_schedule(schedule, courses_taken)
    return True


def test_courses_taken_chain():
    """Test courses_taken with prerequisite chain."""
    # MATH& 151 requires: MATH& 142 -> MATH& 141 -> MATH 99
    schedule = [
        ('MATH& 151', 'Summer', 2026),
    ]
    
    # Missing all prereqs - should fail
    assert not is_course_schedule(schedule)
    
    # With all prereqs taken - should pass
    courses_taken = ['MATH 99', 'MATH& 141', 'MATH& 142']
    assert is_course_schedule(schedule, courses_taken)
    return True


def test_courses_taken_partial_schedule():
    """Test courses_taken with multi-course schedule."""
    # Schedule has CS 143 and MATH& 142, both need prereqs
    schedule = [
        ('CS 143', 'Spring', 2026),
        ('MATH& 142', 'Summer', 2026),
    ]
    
    # Without any courses taken, should fail (missing prereqs)
    assert not is_course_schedule(schedule)
    
    # With their prereqs taken, should pass
    courses_taken = ['CS& 141', 'MATH& 141', 'MATH 99']
    assert is_course_schedule(schedule, courses_taken)
    return True


def main():
    tests = [
        ("Valid scheduled course", test_is_scheduled_course_valid),
        ("Invalid scheduled course", test_is_scheduled_course_invalid),
        ("Valid course schedule", test_is_course_schedule_valid),
        ("Empty course schedule", test_is_course_schedule_empty),
        ("Wrong topological order", test_is_course_schedule_wrong_order),
        ("Missing prerequisite", test_is_course_schedule_missing_prereq),
        ("Course not offered", test_is_course_schedule_not_offered),
        ("Wrong temporal order", test_is_course_schedule_wrong_temporal_order),
        ("Temporal order across years", test_is_course_schedule_temporal_order_across_years),
        ("Courses taken satisfies prereq", test_courses_taken_satisfies_prereq),
        ("Courses taken allows topological order", test_courses_taken_allows_topological_order),
        ("Courses taken chain", test_courses_taken_chain),
        ("Courses taken partial schedule", test_courses_taken_partial_schedule),
    ]
    
    print("=" * 60)
    print("TEST: Course Schedule Validation")
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
        print("[PASS] TEST PASSED: All course schedule validation tests passed")
        return 0
    else:
        print("[FAIL] TEST FAILED: Some course schedule validation tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
