#!/usr/bin/env python3
"""
Test that an invalid plan (incomplete plan) fails validation.
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
    plan_file = script_dir / "test_invalid_plan"
    
    print("=" * 60)
    print("TEST: Invalid Plan (Incomplete)")
    print("=" * 60)
    print()
    
    # Run validation
    result = subprocess.run(
        [sys.executable, str(validate_script), str(program_json), str(plan_file)],
        capture_output=False
    )
    
    print()
    if result.returncode != 0:
        print("[PASS] TEST PASSED: Invalid plan correctly rejected")
        return 0
    else:
        print("✗ TEST FAILED: Invalid plan should have failed validation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
