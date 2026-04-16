#!/usr/bin/env python3
"""
Add all prerequisites (recursively) to a plan and return topologically sorted.
"""

import sys
from util import load_prereqs, get_prereqs_path

def add_prereqs_to_plan(plan):
    """
    Add all prerequisites to a plan and return topologically sorted list.
    
    Args:
        plan: List of courses
        
    Returns:
        List of courses with all prerequisites, topologically sorted
        (prerequisites appear before courses that depend on them)
    """
    prereqs = load_prereqs(get_prereqs_path())
    
    # First, collect all courses (plan + all prerequisites)
    all_courses = set(plan)
    added = True
    
    while added:
        added = False
        for course in list(all_courses):
            if course in prereqs:
                for prereq in prereqs[course]:
                    if prereq not in all_courses:
                        all_courses.add(prereq)
                        added = True
    
    # Now perform topological sort using Kahn's algorithm
    # Build in-degree map for courses in our set
    in_degree = {course: 0 for course in all_courses}
    
    for course in all_courses:
        if course in prereqs:
            for prereq in prereqs[course]:
                if prereq in all_courses:
                    in_degree[course] += 1
    
    # Start with courses that have no prerequisites
    queue = [course for course in all_courses if in_degree[course] == 0]
    queue.sort()  # Sort for deterministic output
    result = []
    
    while queue:
        # Take course with no remaining prerequisites
        course = queue.pop(0)
        result.append(course)
        
        # For each course that depends on this one, reduce in-degree
        for dependent in all_courses:
            if dependent in prereqs and course in prereqs[dependent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
                    queue.sort()  # Keep queue sorted for deterministic output
    
    return result
