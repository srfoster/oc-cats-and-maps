#!/usr/bin/env python3
"""
Check if a student plan would satisfy degree program requirements.
"""

import sys
from pathlib import Path
from util import load_catalog, load_plan, load_program, get_catalog_path
from validate_plan_util import evaluate_requirement
from course_types import is_plan

def plan_would_satisfy_degree_program(program, plan):
    """Check if plan satisfies all program requirements."""
    # Evaluate each requirement
    all_valid = True
    for i, requirement in enumerate(program['requirements'], 1):
        is_valid, message = evaluate_requirement(requirement, plan)
        
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"Requirement {i}: {status}")
        print(f"  {message}")
        print()
        
        if not is_valid:
            all_valid = False
    
    # Final result
    print("=" * 60)
    if all_valid:
        print("✓ PLAN VALID: All requirements satisfied!")
        return 0
    else:
        print("✗ PLAN INVALID: Some requirements not met.")
        return 1


def validate_file_exists(path, description):
    """Check if a file exists, exit with error if not."""
    if not path.exists():
        print(f"Error: {description} not found: {path}")
        sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python plan_would_satisfy_degree_program.py <main.program> <plan_file>")
        sys.exit(1)
    
    program_path = Path(sys.argv[1])
    plan_path = Path(sys.argv[2])
    catalog_path = get_catalog_path()
    
    # Validate all required files exist
    validate_file_exists(program_path, "Program file")
    validate_file_exists(plan_path, "Plan file")
    validate_file_exists(catalog_path, "Catalog file")
    
    # Load data
    program = load_program(program_path)
    plan = load_plan(plan_path)
    
    # Validate plan courses exist in catalog
    if not is_plan(plan):
        print("Error: Plan contains courses not in catalog")
        sys.exit(1)
    
    # Run validation
    sys.exit(plan_would_satisfy_degree_program(program, plan))


if __name__ == "__main__":
    main()
