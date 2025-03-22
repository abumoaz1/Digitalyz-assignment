# Scheduling Algorithm Approach

## Problem Overview

The course scheduling problem involves assigning courses to time blocks and students to course sections while respecting various constraints:

1. No student can be in two courses at the same time
2. No teacher can teach two courses at the same time
3. Courses can only be scheduled in their available blocks
4. Section capacities must be respected
5. Request priorities must be considered (Required > Requested > Recommended)

## Algorithm Design

We implemented a two-pass greedy algorithm with the following steps:

### First Pass: Course-to-Block Assignment

In the first pass, we assign course sections to time blocks:

1. Iterate through all courses, starting with those having the most requests
2. For each course:
   - Determine the number of sections needed based on enrollment requests
   - For each section:
     - Find an available block that doesn't conflict with the lecturer's existing schedule
     - Assign the section to that block
     - Update the lecturer's schedule

Pseudocode:
```
for each course:
    num_sections = min(course.max_sections, ceil(requests.count / course.max_size))
    assigned_blocks = []
    
    for section_num = 1 to num_sections:
        section_key = f"{course_code}_{section_num}"
        best_block = null
        
        for each block in available_blocks:
            if block not in unavailable_blocks and block not in assigned_blocks:
                lecturer = get_lecturer_for_section(section_key)
                if block not in lecturer_schedule[lecturer]:
                    best_block = block
                    break
                    
        if best_block:
            assigned_blocks.add(best_block)
            section_blocks[section_key] = best_block
            lecturer_schedule[lecturer][best_block] = course_info
```

### Second Pass: Student-to-Section Assignment

In the second pass, we assign students to course sections:

1. Sort student requests by priority (Required > Requested > Recommended)
2. For each request:
   - Try to find an available section that:
     - Has space available
     - Is in a block where the student doesn't have another class
   - If found, assign the student to that section
   - If not found, mark the request as unresolved

Pseudocode:
```
for each course:
    # Sort requests by priority
    requests.sort(by_priority)
    
    for each request in requests:
        assigned = false
        student = request.student_id
        
        for section_num = 1 to course.num_sections:
            section_key = f"{course_code}_{section_num}"
            block = section_blocks[section_key]
            
            if section_assignments[section_key].count < course.max_size and 
               block not in student_schedule[student]:
                # Assign student to section
                student_schedule[student][block] = course_info
                section_assignments[section_key].add(student)
                resolved_requests.add(request)
                assigned = true
                break
                
        if not assigned:
            unresolved_requests.add(request)
```

## Optimization Considerations

Our algorithm prioritizes:

1. **Required courses**: These are scheduled first to ensure students get their required courses
2. **Block availability**: Respects course-specific block restrictions
3. **Teacher conflicts**: Ensures no teacher has two courses in the same block
4. **Student conflicts**: Ensures no student has two courses in the same block
5. **Section capacity**: Respects maximum section sizes

## Limitations and Trade-offs

The current implementation has some limitations:

1. **Greedy approach**: Makes locally optimal choices without guaranteeing global optimality
2. **No backtracking**: Once a decision is made, it's not revisited even if it leads to conflicts later
3. **Order dependency**: Results may vary based on the order courses are processed
4. **Room assignment**: The current version doesn't consider room capacities or features

## Performance Metrics

We evaluate the schedule quality using:

1. **Satisfaction rate**: Percentage of student requests successfully fulfilled
2. **Priority fulfillment**: Success rates by priority level (Required, Requested, Recommended)
3. **Section fill rates**: How efficiently sections are filled
4. **Distribution balance**: How evenly students are distributed across blocks

## Future Improvements

To enhance the algorithm, we could:

1. Implement a constraint satisfaction solver for more optimal results
2. Add backtracking to revisit decisions that lead to conflicts
3. Consider room assignments and capacities
4. Add a scoring function to better evaluate schedule quality
5. Implement a multi-objective optimization approach that balances different constraints 