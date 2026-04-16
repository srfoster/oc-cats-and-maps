#!/usr/bin/env python3
"""
Utility functions for working with course catalogs, plans, and programs.
"""

import json
from pathlib import Path


def load_catalog(catalog_path):
    """
    Load credit hours from catalog file.
    
    Args:
        catalog_path: Path to catalog CSV file (Course,Credits format)
    
    Returns:
        dict: Mapping of course codes to credit hours
    """
    credits = {}
    catalog_path = Path(catalog_path)
    
    with open(catalog_path, 'r') as f:
        lines = f.readlines()[1:]  # Skip header
        for line in lines:
            if line.strip():
                course, credit = line.strip().split(',')
                credits[course] = int(credit)
    return credits


def load_plan(plan_path):
    """
    Load courses from a plan file.
    
    Args:
        plan_path: Path to plan file (one course per line)
    
    Returns:
        list: List of course codes in the plan
    """
    plan_path = Path(plan_path)
    
    with open(plan_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def load_program(program_path):
    """
    Load program requirements from JSON file.
    
    Args:
        program_path: Path to program JSON file
    
    Returns:
        dict: Program data including name and requirements
    """
    program_path = Path(program_path)
    
    with open(program_path, 'r') as f:
        return json.load(f)


def get_catalog_path():
    """
    Get the default catalog path relative to this module.
    
    Returns:
        Path: Path to the catalog file
    """
    util_dir = Path(__file__).parent
    return util_dir.parent / "catalog"


def get_prereqs_path():
    """
    Get the default prereqs path relative to this module.
    
    Returns:
        Path: Path to the prereqs file
    """
    util_dir = Path(__file__).parent
    return util_dir.parent / "prereqs"


def load_prereqs(prereqs_path):
    """
    Load prerequisites from prereqs file.
    
    Args:
        prereqs_path: Path to prereqs file (prereq,course format)
    
    Returns:
        dict: Mapping of course codes to set of prerequisite course codes
    """
    prereqs = {}
    prereqs_path = Path(prereqs_path)
    
    with open(prereqs_path, 'r') as f:
        for line in f:
            if line.strip():
                prereq, course = line.strip().split(',')
                if course not in prereqs:
                    prereqs[course] = set()
                prereqs[course].add(prereq)
    return prereqs


def get_schedule_path():
    """Get the default schedule path relative to this module."""
    return Path(__file__).parent.parent / "schedule"


def load_schedule(schedule_path):
    """
    Load course schedule from schedule file.
    
    Args:
        schedule_path: Path to schedule file (course,quarter format)
    
    Returns:
        set: Set of (course, quarter) tuples
    """
    schedule = set()
    schedule_path = Path(schedule_path)
    
    with open(schedule_path, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(',')
                course, quarter = parts[0], parts[1]
                schedule.add((course, quarter))
    return schedule

