
Workflows:

* Double check this student's MAP:
  - Extract plan, future schedule, and course taken from MAP screenshot
    * ChatGPT prompt: "..."
  - If there are courses taken not in their MAP, extract course history from CTCLink
    * Script ...
  - Get it in a format for automatic validation, then...
  - python tools/check_schedule_and_validate_against_program.py \
      <path/to/program.program> \
      "course,ids,already,taken,..." \
      "[['course1',quarter,year],...]"

* Generate a MAP for this student
  - Get their degree program (ensure we have as .program file)
  - Generate their .plan custom (automatically?) or pick off the shelf. 
  - If they've taken previous classes, subtract out those course ideas
  - python tools/generate_schedule_from_plan PATH/TO/PLAN "ids,of,courses,already,taken"

---

Tech notes:



Files in global context (course catalog and schedule basically)
* catalog
* prereqs 
* schedule (TODO: add years...)


Is this plan a plan?  (All courses are in the catalog)
* is_plan

Would this plan satisfy a given degree program's requirements today?
* plan_would_satisfy_degree_program

What is my plan when prereqs are added in?
* add_prereqs_to_plan
  - Returned plan is sorted topologically

  
Given a quarter by quarter schedule, is it valid?
* is_course_schedule
    - Schedule implies feasible. 
        - Goes in topological order?
        - All courses are in catalog?
        - All prereqs accounted for?  (Can pass in courses_taken to override the prereq validation)
        - All courses offered in the given quarter?
        - Goes in temporal order?
    - Schedule implies future.  
        -  All courses are in the current quarter or future ones? 
    


For this plan, what is my quarter by quarter schedule?
* plan_to_schedule
  - If past coursework, subtract out the plan that is passed in
  - Will add in prereqs (getting back sorted list)
  - Get a subset of the global schedule that involves those courses
    - Error if a course can't be scheduled (e.g. discontinued).  I.e. no possible schedule exists to execute on the given plan
  - Generate all possible schedules assuming a standard load (what is this?)
    - Make modifiable based on given load constraints (mapping of quarter->hours)
  - Output shortest


What are all valid plans for this degree program?
  - Might not be necessary because we have enough named programs "e.g. IT_SD BSCS track"