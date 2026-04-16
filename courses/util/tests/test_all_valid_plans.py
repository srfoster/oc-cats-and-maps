#!/usr/bin/env python3
"""
Test all valid plans found in programs/**/plans/*.plan files.
"""

import subprocess
import sys
from pathlib import Path

def test_plan(validate_script, program_json, plan_file):
    """Test a single plan file."""
    import os
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    # Run validation
    result = subprocess.run(
        [sys.executable, str(validate_script), str(program_json), str(plan_file)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    # Paths relative to this script
    script_dir = Path(__file__).parent
    courses_dir = script_dir.parent.parent
    validate_script = script_dir.parent / "plan_would_satisfy_degree_program.py"
    
    # Find all .plan files in programs/
    programs_dir = courses_dir / "programs"
    plan_files = list(programs_dir.glob("**/*.plan"))
    
    if not plan_files:
        print("[FAIL] No .plan files found in programs/")
        return 1
    
    print("=" * 60)
    print(f"Testing {len(plan_files)} valid plan(s)")
    print("=" * 60)
    print()
    
    all_passed = True
    results = []
    
    for plan_file in sorted(plan_files):
        # Find corresponding main.program (go up to plans/, then up to program dir)
        program_dir = plan_file.parent.parent
        program_json = program_dir / "main.program"
        
        if not program_json.exists():
            print(f"[SKIP] {plan_file.name} - No main.program found at {program_json}")
            all_passed = False
            continue
        
        print(f"Testing: {plan_file.relative_to(courses_dir)}")
        passed, stdout, stderr = test_plan(validate_script, program_json, plan_file)
        
        if passed:
            print(f"  [PASS]")
            results.append((plan_file.name, True))
        else:
            print(f"  [FAIL]")
            if stderr:
                print(f"    Error: {stderr[:200]}")
            all_passed = False
            results.append((plan_file.name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for plan_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {plan_name}")
    
    print()
    if all_passed:
        print("[PASS] ALL PLANS PASSED")
        return 0
    else:
        print("[FAIL] SOME PLANS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
