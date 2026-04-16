#!/usr/bin/env python3
"""
Test that a plan with invalid course codes is rejected.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Paths relative to this script
    script_dir = Path(__file__).parent
    courses_dir = script_dir.parent.parent
    
    validate_script = script_dir.parent / "plan_would_satisfy_degree_program.py"
    program_json = courses_dir / "programs" / "IT_Software_Development_AAS-T" / "main.program"
    plan_file = script_dir / "test_plan_with_invalid_courses"
    
    print("=" * 60)
    print("TEST: Plan with Invalid Course Codes")
    print("=" * 60)
    print()
    
    # Run validation
    result = subprocess.run(
        [sys.executable, str(validate_script), str(program_json), str(plan_file)],
        capture_output=True,
        text=True
    )
    
    print()
    # Check for specific error about invalid courses in catalog
    output = result.stdout + result.stderr
    if result.returncode != 0 and "not in catalog" in output:
        print("[PASS] TEST PASSED: Plan with invalid courses correctly rejected")
        return 0
    else:
        print("[FAIL] TEST FAILED: Plan with invalid courses should have been rejected with catalog error")
        if result.returncode == 0:
            print("  Expected non-zero exit code")
        else:
            print(f"  Expected 'not in catalog' error")
            print(f"  stdout: {result.stdout[:200]}")
            print(f"  stderr: {result.stderr[:200]}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
