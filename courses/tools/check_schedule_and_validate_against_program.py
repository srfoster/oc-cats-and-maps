#!/usr/bin/env python3
"""
Validate a schedule and check if it satisfies program requirements.

Usage:
  python check_schedule_and_validate_against_program.py <program_file> <courses_taken> <schedule>

Arguments:
  - program_file: Path to .program file (e.g., ../programs/IT_Software_Development_AAS-T/main.program)
  - courses_taken: Comma-separated list of course IDs (e.g., "CIS 236,ENGL& 101,MATH 99")
  - schedule: JSON-style list of [course,quarter,year] (e.g., "[['ENGL& 235',Summer,2026],['CS 110',Fall,2026]]")

Example:
  python check_schedule_and_validate_against_program.py \\
    ../programs/IT_Software_Development_AAS-T/main.program \\
    "CIS 236,ENGL& 101,MATH 99,CIS 110" \\
    "[['ENGL& 235',Summer,2026],['CMST& 210',Summer,2026],['CS 110',Fall,2026]]"
"""

import sys
import ast
from pathlib import Path

# Add util to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'util'))

from util import load_program, load_catalog
from plan_to_schedule import is_course_schedule, max_credits_per_quarter
from validate_plan_util import evaluate_requirement


def parse_courses_taken(arg):
    """Parse comma-separated course list."""
    if not arg:
        return []
    return [c.strip() for c in arg.split(',') if c.strip()]


def parse_schedule(arg):
    """Parse schedule from list format."""
    if not arg:
        return []
    
    # Replace unquoted quarter names with quoted versions
    for quarter in ['Winter', 'Spring', 'Summer', 'Fall']:
        arg = arg.replace(f',{quarter},', f',"{quarter}",')
        arg = arg.replace(f"'{quarter}'", f'"{quarter}"')
    
    # Use ast.literal_eval to safely parse the list
    try:
        raw_schedule = ast.literal_eval(arg)
        schedule = []
        for item in raw_schedule:
            if len(item) != 3:
                print(f"Warning: Invalid schedule item (need 3 elements): {item}")
                continue
            course, quarter, year = item
            schedule.append((str(course), str(quarter), int(year)))
        return schedule
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing schedule: {e}")
        print("Schedule should be in format: [['course1',quarter,year],['course2',quarter,year]]")
        print("Quarters can be unquoted: Winter, Spring, Summer, Fall")
        sys.exit(1)


def print_schedule_summary(schedule, catalog):
    """Print credit breakdown by quarter."""
    from collections import defaultdict
    
    credits_by_quarter = defaultdict(int)
    courses_by_quarter = defaultdict(list)
    
    for course, quarter, year in schedule:
        credits = catalog[course]
        credits_by_quarter[(quarter, year)] += credits
        courses_by_quarter[(quarter, year)].append((course, credits))
    
    print("Schedule Summary:")
    print("=" * 60)
    quarter_order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
    
    for (q, y) in sorted(credits_by_quarter.keys(), key=lambda x: (x[1], quarter_order[x[0]])):
        print(f"\n{q} {y}: {credits_by_quarter[(q, y)]} credits")
        for course, creds in sorted(courses_by_quarter[(q, y)]):
            print(f"  - {course} ({creds} cr)")
    
    total_credits = sum(credits_by_quarter.values())
    num_quarters = len(credits_by_quarter)
    print(f"\nTotal: {total_credits} credits across {num_quarters} quarters")
    print("=" * 60)
    print()


def check_program_requirements(program, all_courses):
    """Check if courses satisfy program requirements."""
    print("Program Requirements Check:")
    print("=" * 60)
    print()
    
    all_valid = True
    for i, requirement in enumerate(program['requirements'], 1):
        is_valid, message = evaluate_requirement(requirement, all_courses)
        
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"Requirement {i}: {status}")
        print(f"  {message}")
        print()
        
        if not is_valid:
            all_valid = False
    
    return all_valid


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    program_path = Path(sys.argv[1])
    courses_taken_arg = sys.argv[2]
    schedule_arg = sys.argv[3]
    
    # Validate program file exists
    if not program_path.exists():
        print(f"Error: Program file not found: {program_path}")
        sys.exit(1)
    
    # Load data
    program = load_program(program_path)
    courses_taken = parse_courses_taken(courses_taken_arg)
    schedule = parse_schedule(schedule_arg)
    catalog = load_catalog(Path(__file__).parent.parent / 'catalog')
    
    print("SCHEDULE VALIDATION")
    print("=" * 60)
    print()
    
    # Validate schedule structure
    print("1. Checking schedule validity...")
    valid_structure = is_course_schedule(schedule, courses_taken)
    if valid_structure:
        print("   ✓ Valid schedule (prerequisites, offerings, temporal order OK)")
    else:
        print("   ✗ Invalid schedule")
        print("\n   Schedule has structural problems. Cannot proceed.")
        sys.exit(1)
    print()
    
    # Check credit limits
    print("2. Checking credit limits (≤15 per quarter)...")
    valid_credits = max_credits_per_quarter(schedule, courses_taken)
    if valid_credits:
        print("   ✓ All quarters within credit limit")
    else:
        print("   ✗ Some quarters exceed 15 credits")
    print()
    
    # Print schedule summary
    print_schedule_summary(schedule, catalog)
    
    # Check program requirements
    all_courses = courses_taken + [course for course, _, _ in schedule]
    all_valid = check_program_requirements(program, all_courses)
    
    # Final summary
    print("=" * 60)
    print("FINAL RESULT:")
    if valid_structure and valid_credits and all_valid:
        print("✓ PASS: Schedule is valid and satisfies all program requirements!")
        sys.exit(0)
    else:
        print("✗ FAIL: Issues found")
        if not valid_structure:
            print("  - Schedule structure invalid")
        if not valid_credits:
            print("  - Credit limits violated")
        if not all_valid:
            print("  - Program requirements not satisfied")
        sys.exit(1)


if __name__ == "__main__":
    main()
