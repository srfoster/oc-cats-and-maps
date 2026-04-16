#!/usr/bin/env python3
"""Generate a schedule from a plan file."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "util"))

from util import load_plan
from plan_to_schedule import plan_to_schedule

def main():
    if len(sys.argv) < 2:
        print("Usage: generate_schedule_from_plan.py <plan_path> [course1,course2,...]")
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    courses_taken = sys.argv[2].split(",") if len(sys.argv) > 2 else []
    
    courses = load_plan(plan_path)
    schedule = plan_to_schedule(courses, courses_taken if courses_taken else None)
    
    if schedule:
        for course, quarter, year in schedule:
            print(f"{course},{quarter},{year}")
    else:
        print("No schedule found", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
