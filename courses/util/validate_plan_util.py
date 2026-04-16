#!/usr/bin/env python3
"""
Utility functions for evaluating specific requirement operators.
"""

from util import load_catalog, get_catalog_path

# Load catalog once as global context
_CREDITS = None

def _get_credits():
    """Lazy load credits catalog."""
    global _CREDITS
    if _CREDITS is None:
        _CREDITS = load_catalog(get_catalog_path())
    return _CREDITS

def evaluate_requirement(requirement, plan):
    """
    Recursively evaluate a requirement against a plan.
    
    Returns (is_valid, message)
    """
    if not isinstance(requirement, list):
        # Base case: single course requirement
        return requirement in plan, f"Course {requirement}"
    
    operator = requirement[0]
    
    if operator == "AllOf":
        return evaluate_all_of(requirement, plan)
    
    elif operator == "Either":
        return evaluate_either(requirement, plan)
    
    elif operator == "Hours>=":
        return evaluate_hours_ge(requirement, plan)
    
    else:
        return False, f"Unknown operator: {operator}"

def evaluate_all_of(requirement, plan):
    """
    Evaluate an AllOf requirement - all courses must be in the plan.
    
    Args:
        requirement: List where [0] is "AllOf" and [1:] are required courses
        plan: List of courses in the student plan
    
    Returns:
        tuple: (is_valid, message)
    """
    required_courses = set(requirement[1:])
    plan_set = set(plan)
    missing = required_courses - plan_set
    if missing:
        return False, f"AllOf: Missing courses: {', '.join(sorted(missing))}"
    return True, f"AllOf: All courses present ({len(required_courses)} courses)"


def evaluate_either(requirement, plan):
    """
    Evaluate an Either requirement - at least one option must be satisfied.
    
    Args:
        requirement: List where [0] is "Either" and [1:] are option requirements
        plan: List of courses in the student plan
    
    Returns:
        tuple: (is_valid, message)
    """
    options = requirement[1:]
    
    # Check if any option is satisfied
    for i, option in enumerate(options, 1):
        is_valid, msg = evaluate_requirement(option, plan)
        if is_valid:
            return True, f"Either: Option {i} satisfied - {msg}"
    
    # None satisfied - build detailed message
    messages = []
    for i, option in enumerate(options, 1):
        is_valid, msg = evaluate_requirement(option, plan)
        messages.append(f"  Option {i}: {msg}")
    return False, f"Either: No option satisfied:\n" + "\n".join(messages)


def evaluate_hours_ge(requirement, plan):
    """
    Evaluate a Hours>= requirement - minimum credit hours from course options.
    
    Args:
        requirement: List where [0] is "Hours>=", [1] is min hours, [2:] are courses
        plan: List of courses in the student plan
    
    Returns:
        tuple: (is_valid, message)
    """
    credits = _get_credits()
    min_hours = requirement[1]
    course_options = requirement[2:]
    
    plan_set = set(plan)
    taken_courses = plan_set.intersection(set(course_options))
    total_hours = sum(credits.get(course, 0) for course in taken_courses)
    
    if total_hours >= min_hours:
        return True, f"Hours>=: {total_hours} credits (>= {min_hours}) from {taken_courses}"
    else:
        return False, f"Hours>=: Only {total_hours} credits (need {min_hours}). Taken: {taken_courses or 'none'}"
