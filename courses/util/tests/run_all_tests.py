#!/usr/bin/env python3
"""
Run all validation tests.
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_script):
    """Run a test script and return True if it passes."""
    print()
    result = subprocess.run([sys.executable, str(test_script)])
    return result.returncode == 0

def main():
    script_dir = Path(__file__).parent
    
    tests = [
        script_dir / "test_all_valid_plans.py",
        script_dir / "test_invalid_plan.py",
        script_dir / "test_plan_with_invalid_courses.py",
        script_dir / "test_prereq_resolution.py",
        script_dir / "test_course_schedule_validation.py",
        script_dir / "test_plan_to_schedule.py",
    ]
    
    print("RUNNING ALL VALIDATION TESTS")
    print("=" * 60)
    
    results = {}
    for test in tests:
        if test.exists():
            passed = run_test(test)
            results[test.name] = passed
        else:
            print(f"[FAIL] Test not found: {test.name}")
            results[test.name] = False
    
    # Summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    print()
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
        return 0
    else:
        print("[FAIL] SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
