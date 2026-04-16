#!/usr/bin/env python3
"""
Convert a course plan into a scheduled course list using backtracking search.
"""

from datetime import date
import sys
from util import load_schedule, get_schedule_path, load_catalog, get_catalog_path
from add_prereqs_to_plan import add_prereqs_to_plan
from course_types import is_course_schedule


def current_quarter(today=None):
    if today is None:
        today = date.today()
    return _which_quarter(today)


def _which_quarter(today):
    y = today.year
    if _in_range(today, y, 1, 2, 3, 31):
        return "Winter", y
    return _check_other_quarters(today, y)


def _check_other_quarters(today, y):
    if _in_range(today, y, 4, 1, 6, 30):
        return "Spring", y
    if _in_range(today, y, 7, 1, 8, 31):
        return "Summer", y
    return "Fall", y


def _in_range(today, y, m1, d1, m2, d2):
    return date(y, m1, d1) <= today <= date(y, m2, d2)


def next_quarter(quarter, year):
    transitions = {'Fall': ('Winter', year + 1), 'Winter': ('Spring', year),
                   'Spring': ('Summer', year), 'Summer': ('Fall', year)}
    return transitions[quarter]


def max_credits_per_quarter(schedule, courses_taken):
    """Default: max 15 credits per quarter."""
    return _check_max_credits(schedule, 15)


def make_max_credits_constraint(limit):
    """Factory: create constraint with custom credit limit."""
    def constraint(schedule, courses_taken):
        return _check_max_credits(schedule, limit)
    constraint.__name__ = f'max_{limit}_credits_per_quarter'
    return constraint


def _check_max_credits(schedule, limit):
    """Check if all quarters in schedule are under credit limit."""
    catalog = load_catalog(get_catalog_path())
    for q, y in set((s[1], s[2]) for s in schedule):
        if _credits_in_quarter(schedule, q, y, catalog) > limit:
            return False
    return True


def _credits_in_quarter(schedule, quarter, year, catalog):
    courses = [s[0] for s in schedule if s[1] == quarter and s[2] == year]
    return sum(catalog[c] for c in courses)


def max_2_years_duration(schedule, courses_taken):
    """Check if schedule completes within 2 years."""
    if not schedule:
        return True
    first_key = _temporal_key(schedule[0][1], schedule[0][2])
    last_key = _temporal_key(schedule[-1][1], schedule[-1][2])
    quarters_elapsed = (last_key[0] - first_key[0]) * 4 + (last_key[1] - first_key[1])
    return quarters_elapsed <= 9


def _temporal_key(quarter, year):
    """Convert (quarter, year) to sortable tuple."""
    quarters = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
    return (year, quarters[quarter])


def plan_to_schedule(courses_to_schedule, courses_taken=None, custom_constraints=None):
    taken = courses_taken if courses_taken else []
    default = [max_credits_per_quarter, max_2_years_duration]
    constraints = custom_constraints if custom_constraints else default
    to_schedule = _get_courses_to_schedule(courses_to_schedule, taken)
    _preflight_check(to_schedule)
    return _search_schedule(to_schedule, taken, constraints)


def _preflight_check(courses):
    """Verify courses are schedulable before attempting backtracking."""
    start_q, start_y = next_quarter(*current_quarter())
    missing = _find_missing_courses(courses, start_q, start_y)
    if missing:
        _report_missing_courses(missing, start_q, start_y)


def _find_missing_courses(courses, start_q, start_y):
    """Find courses not in schedule file."""
    schedule = load_schedule(get_schedule_path())
    return [c for c in courses 
            if not any(course == c for course, q in schedule)]


def _report_missing_courses(missing, start_q, start_y):
    """Raise error with details about missing courses."""
    msg = f"\n{len(missing)} course(s) not in schedule file:\n"
    msg += "\n".join(f"  - {c}" for c in missing)
    raise ValueError(msg)


def _get_courses_to_schedule(courses, taken):
    with_prereqs = add_prereqs_to_plan(taken + courses)
    return [c for c in with_prereqs if c not in taken]


def _search_schedule(courses, taken, constraints):
    start_q, start_y = next_quarter(*current_quarter())
    if not _all_courses_offered(courses, start_q, start_y):
        return None
    return _quarter_by_quarter_schedule(courses, taken, constraints, start_q, start_y)


def _quarter_by_quarter_schedule(courses, taken, constraints, start_q, start_y):
    """Fill quarters chronologically, like a human advisor would."""
    from util import load_prereqs, get_prereqs_path
    
    # Build prerequisite map
    all_prereqs = load_prereqs(get_prereqs_path())
    course_set = set(courses)
    prereq_map = {}
    for course in courses:
        if course in all_prereqs:
            prereq_map[course] = all_prereqs[course] & course_set
        else:
            prereq_map[course] = set()
    
    # Build offerings map
    schedule_file = load_schedule(get_schedule_path())
    offerings = {}
    for course in courses:
        offerings[course] = set(q for c, q in schedule_file if c == course)
    
    # Fill quarters chronologically
    schedule = []
    remaining = set(courses)
    current_q, current_y = start_q, start_y
    max_quarters = 12
    
    for _ in range(max_quarters):
        if not remaining:
            return schedule  # Success!
        
        # Find available courses for this quarter
        scheduled_set = set(c for c, _, _ in schedule)
        available = [
            c for c in remaining
            if current_q in offerings[c]
            and prereq_map[c].issubset(scheduled_set | set(taken))
        ]
        
        if not available:
            # No courses available, move to next quarter
            current_q, current_y = next_quarter(current_q, current_y)
            continue
        
        # Try to pack this quarter with backtracking
        selected = _backtrack_quarter_fill(available, [], schedule, taken, 
                                           constraints, current_q, current_y)
        
        if selected is None:
            # Couldn't fill this quarter - try skipping it
            current_q, current_y = next_quarter(current_q, current_y)
            continue
        
        # Add selected courses to schedule
        for course in selected:
            schedule.append((course, current_q, current_y))
            remaining.remove(course)
        
        print(f"{current_q} {current_y}: {len(selected)} courses, {len(remaining)} remaining", file=sys.stderr)
        
        # Move to next quarter
        current_q, current_y = next_quarter(current_q, current_y)
    
    return None  # Couldn't schedule all courses in time limit


def _backtrack_quarter_fill(available, selected, prior_schedule, taken, 
                            constraints, quarter, year):
    """Try to select courses for this quarter using backtracking."""
    catalog = load_catalog(get_catalog_path())
    
    # If we've tried all available courses, return what we selected
    if not available:
        return selected if selected else None
    
    # Try adding next available course
    course = available[0]
    rest = available[1:]
    
    # Option 1: Include this course
    new_selected = selected + [course]
    new_schedule = prior_schedule + [(c, quarter, year) for c in new_selected]
    
    if _is_valid(new_schedule, taken, constraints):
        # This course fits, try to add more
        result = _backtrack_quarter_fill(rest, new_selected, prior_schedule, 
                                        taken, constraints, quarter, year)
        if result is not None:
            return result
    
    # Option 2: Skip this course (don't include it in this quarter)
    return _backtrack_quarter_fill(rest, selected, prior_schedule, 
                                  taken, constraints, quarter, year)


def _search_schedule(courses, taken, constraints):
    start_q, start_y = next_quarter(*current_quarter())
    if not _all_courses_offered(courses, start_q, start_y):
        return None
    return _quarter_by_quarter_schedule(courses, taken, constraints, start_q, start_y)


def _greedy_schedule(courses, taken, constraints, start_q, start_y):
    """Greedy algorithm: schedule courses in earliest valid slots (topological order)."""
    quarters_map = {c: _get_offerings(c, start_q, start_y) for c in courses}
    schedule = []
    for course in courses:  # Already in topological order
        best_slot = _find_earliest_slot(course, schedule, taken, quarters_map, constraints)
        if best_slot is None:
            print(f"Cannot schedule {course} - no valid quarter found", file=sys.stderr)
            return None
        schedule.append((course, best_slot[0], best_slot[1]))
    return schedule


def _find_earliest_slot(course, partial_schedule, taken, quarters_map, constraints):
    """Find earliest quarter that satisfies all constraints for this course."""
    for quarter, year in quarters_map[course]:
        candidate = partial_schedule + [(course, quarter, year)]
        if _is_valid(candidate, taken, constraints):
            return (quarter, year)
    return None


def _all_courses_offered(courses, start_q, start_y):
    schedule = load_schedule(get_schedule_path())
    return all(_is_in_schedule(course, schedule) for course in courses)


def _is_in_schedule(course, schedule):
    return any(c == course for c, q in schedule)


def _is_after_or_equal(q1, y1, q2, y2):
    order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
    return (y1, order[q1]) >= (y2, order[q2])


def _get_offerings(course_id, start_q, start_y):
    schedule = load_schedule(get_schedule_path())
    quarters = [q for c, q in schedule if c == course_id]
    return _generate_future_offerings(quarters, start_q, start_y)


def _generate_future_offerings(quarters, start_q, start_y):
    offerings = []
    for year in range(start_y, start_y + 5):
        for quarter in quarters:
            if _is_after_or_equal(quarter, year, start_q, start_y):
                offerings.append((quarter, year))
    return sorted(offerings, key=lambda x: (x[1], {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}[x[0]]))


def _is_valid(schedule, taken, constraints):
    return (is_course_schedule(schedule, taken) and 
            all(constraint(schedule, taken) for constraint in constraints))
