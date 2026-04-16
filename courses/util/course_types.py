#!/usr/bin/env python3
"""
Type validation functions for main course data structures.

* Plan: A list of course codes (e.g. ["CIS 110", "MATH& 141"])
* Course Schedule: A list of tuples (course_code, quarter, year) (e.g. [("CIS 110", "Fall", 2026), ("MATH& 141", "Winter", 2027)])
  - The course schedule must satisfy all of the following:
    1. All items are valid scheduled courses (tuples of (course_code, quarter, year))
    2. All course codes exist in the catalog
    3. All prerequisites are satisfied (either in courses_taken or earlier in the schedule)
    4. The courses are in topological order (no course scheduled to be taken before its prereqs)
    5. All courses will be offered in the scheduled quarter/year
    6. The schedule is temporally ordered (no course appears after a later quarter/year).  Not strictly necessary, but nice

"""

from util import (load_catalog, get_catalog_path, load_prereqs, 
                  get_prereqs_path, load_schedule, get_schedule_path)
from add_prereqs_to_plan import add_prereqs_to_plan

# A plan is any list of courses that all exist in the catalog
#  It can be empty (planning to take no courses is still a plan)
#  It doesn't have to correspond to a degree program (planning to just take some random courses is still a plan)
#  It doesn't have to include prereqs (planning to take a course without its prereqs is still a plan)
def is_plan(courses):
    """Check if courses is a list and all courses exist in the catalog."""
    if not isinstance(courses, list):
        return False
    catalog = load_catalog(get_catalog_path())
    return all(course in catalog for course in courses)

def is_course_schedule(schedule, courses_taken=None):
    """Validate a course schedule list."""
    if not _is_valid_schedule_structure(schedule):
        return False
    return _validate_schedule_requirements(schedule, courses_taken)


def _is_valid_schedule_structure(schedule):
    """Check basic schedule structure."""
    return (isinstance(schedule, list) and 
            all(is_scheduled_course(item) for item in schedule))


def _validate_schedule_requirements(schedule, courses_taken):
    """Validate all schedule requirements."""
    course_ids = [item[0] for item in schedule]
    return (_all_courses_in_catalog(course_ids) and
            _prereqs_satisfied(course_ids, courses_taken) and
            _schedule_topologically_sorted(course_ids, courses_taken) and
            _all_courses_offered(schedule) and
            _is_temporally_ordered(schedule) and
            _prereqs_in_earlier_quarters(schedule, courses_taken))


def _prereqs_satisfied(course_ids, courses_taken):
    """Check if all prerequisites are satisfied."""
    all_courses = (courses_taken + course_ids) if courses_taken else course_ids
    with_prereqs = add_prereqs_to_plan(all_courses)
    return set(with_prereqs) == set(all_courses)


def _schedule_topologically_sorted(course_ids, courses_taken):
    """Check if schedule courses are topologically sorted."""
    taken_set = set(courses_taken) if courses_taken else None
    return _is_topologically_sorted(course_ids, taken_set)



def is_scheduled_course(item):
    """Check if item is a valid scheduled course (course_id, quarter, year)."""
    if not isinstance(item, (tuple, list)) or len(item) != 3:
        return False
    course_id, quarter, year = item
    return quarter in ['Fall', 'Winter', 'Spring', 'Summer'] and isinstance(year, int)


def _all_courses_in_catalog(course_ids):
    """Check if all course IDs exist in catalog."""
    catalog = load_catalog(get_catalog_path())
    return all(course_id in catalog for course_id in course_ids)



def _is_topologically_sorted(course_ids, courses_taken_set=None):
    """Check if course IDs are in topological order."""
    seen = set(courses_taken_set) if courses_taken_set else set()
    prereqs = load_prereqs(get_prereqs_path())
    return _check_topo_order(course_ids, prereqs, seen)


def _check_topo_order(course_ids, prereqs, seen):
    """Check topological order iteratively."""
    for course in course_ids:
        if not _course_prereqs_seen(course, course_ids, prereqs, seen):
            return False
        seen.add(course)
    return True


def _course_prereqs_seen(course, course_ids, prereqs, seen):
    """Check if all course prerequisites have been seen."""
    if course not in prereqs:
        return True
    return all(p not in course_ids or p in seen for p in prereqs[course])


def _all_courses_offered(scheduled_courses):
    """Check if all courses are offered in given quarter."""
    schedule = load_schedule(get_schedule_path())
    return all((sc[0], sc[1]) in schedule for sc in scheduled_courses)


def _temporal_key(quarter, year):
    """Convert (quarter, year) to sortable tuple."""
    quarters = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
    return (year, quarters[quarter])


def _is_temporally_ordered(scheduled_courses):
    """Check if scheduled courses are in temporal order."""
    for i in range(len(scheduled_courses) - 1):
        if not _is_before_or_equal(scheduled_courses[i], scheduled_courses[i+1]):
            return False
    return True


def _is_before_or_equal(course1, course2):
    """Check if course1 is temporally before or equal to course2."""
    key1 = _temporal_key(course1[1], course1[2])
    key2 = _temporal_key(course2[1], course2[2])
    return key1 <= key2


def _prereqs_in_earlier_quarters(schedule, courses_taken):
    """Check if all prerequisites are in strictly earlier quarters."""
    course_map = {c: (q, y) for c, q, y in schedule}
    prereqs = load_prereqs(get_prereqs_path())
    taken_set = set(courses_taken) if courses_taken else set()
    return all(_prereq_check(c, q, y, course_map, prereqs, taken_set) 
               for c, q, y in schedule)


def _prereq_check(course, quarter, year, course_map, prereqs, taken_set):
    """Check if course's prerequisites are in earlier quarters."""
    if course not in prereqs:
        return True
    return all(_is_prereq_earlier(p, quarter, year, course_map, taken_set) 
               for p in prereqs[course])


def _is_prereq_earlier(prereq, quarter, year, course_map, taken_set):
    """Check if prerequisite is earlier than given quarter/year."""
    if prereq in taken_set or prereq not in course_map:
        return True
    prereq_q, prereq_y = course_map[prereq]
    return _temporal_key(prereq_q, prereq_y) < _temporal_key(quarter, year)

