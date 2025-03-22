import json
import pandas as pd
from collections import defaultdict
import os

def load_cleaned_data(file_path='cleaned_data.json'):
    """Load the cleaned data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def extract_rules_and_constraints(data):
    """Extract scheduling rules and constraints from data"""
    rules = {}
    
    # Default blocks
    all_blocks = ["1A", "1B", "2A", "2B", "3", "4A", "4B"]
    rules['all_blocks'] = all_blocks
    
    # Priority order for request types
    rules['priority_order'] = ['Required', 'Requested', 'Recommended']
    
    return rules

def preprocess_data(data, rules):
    """Prepare data structures for scheduling"""
    # Course to lecturer mapping
    course_to_lecturer = {}
    for course in data.get('course_listings', []):
        lecturer_id = course.get('Lecturer ID')
        course_code = course.get('lecture Code')
        section = course.get('Section number', 1)
        if course_code and lecturer_id:
            key = f"{course_code}_{section}"
            course_to_lecturer[key] = lecturer_id
    
    # Course details mapping
    course_details = {}
    for course in data.get('course_characteristics', []):
        course_code = course.get('Course code')
        if course_code:
            # Handle NoneType values
            available_blocks = course.get('Available blocks', [])
            if available_blocks is None:
                available_blocks = rules['all_blocks']
            
            unavailable_blocks = course.get('Unavailable blocks', [])
            if unavailable_blocks is None:
                unavailable_blocks = []
            
            course_details[course_code] = {
                'title': course.get('Title', ''),
                'length': course.get('Length', 1),
                'num_sections': course.get('Number of sections', 1),
                'max_size': course.get('Maximum section size', 25),
                'available_blocks': available_blocks,
                'unavailable_blocks': unavailable_blocks
            }
    
    # Group student requests by course
    course_requests = defaultdict(list)
    for req in data.get('student_requests', []):
        course_code = req.get('Course code')
        if course_code:
            course_requests[course_code].append(req)
    
    return {
        'course_to_lecturer': course_to_lecturer,
        'course_details': course_details,
        'course_requests': course_requests
    }

def generate_schedule(data, rules, preprocessed):
    """Generate a course schedule"""
    # Extract preprocessed data
    course_to_lecturer = preprocessed['course_to_lecturer']
    course_details = preprocessed['course_details']
    course_requests = preprocessed['course_requests']
    
    # Initialize data structures
    student_schedule = defaultdict(dict)  # {student_id: {block: course}}
    teacher_schedule = defaultdict(dict)  # {teacher_id: {block: course}}
    section_assignments = defaultdict(list)  # {course_section: [student_ids]}
    section_blocks = {}  # {course_section: block}
    
    # Track resolved/unresolved requests
    resolved = []
    unresolved = []
    
    print(f"Generating schedule with {len(course_requests)} courses...")
    
    # First pass: Assign course sections to blocks
    for course_code, requests in course_requests.items():
        print(f"Processing course: {course_code} with {len(requests)} requests")
        
        # Skip if no course details available
        if course_code not in course_details:
            print(f"  No details for course {course_code}, skipping")
            unresolved.extend(requests)
            continue
        
        course = course_details[course_code]
        num_sections = course.get('num_sections', 1)
        max_size = course.get('max_size', 25)
        
        # Get available blocks
        available_blocks = course.get('available_blocks', rules['all_blocks'])
        if not available_blocks:
            available_blocks = rules['all_blocks']
            
        unavailable_blocks = course.get('unavailable_blocks', [])
        if not unavailable_blocks:
            unavailable_blocks = []
            
        print(f"  Available blocks: {available_blocks}")
        print(f"  Unavailable blocks: {unavailable_blocks}")
        
        # Assign blocks to each section
        assigned_blocks = set()
        for section_num in range(1, num_sections + 1):
            section_key = f"{course_code}_{section_num}"
            print(f"  Processing section: {section_key}")
            
            # Find best block
            best_block = None
            for block in rules['all_blocks']:
                # Skip if block not available for this course or already assigned
                if block not in available_blocks or block in unavailable_blocks or block in assigned_blocks:
                    continue
                
                # Check lecturer availability
                lecturer_id = course_to_lecturer.get(section_key, f"unknown_{course_code}")
                if block in teacher_schedule[lecturer_id]:
                    continue
                
                # This block works
                best_block = block
                break
            
            if best_block:
                print(f"  Assigned block {best_block} to section {section_key}")
                assigned_blocks.add(best_block)
                section_blocks[section_key] = best_block
                
                # Assign lecturer
                lecturer_id = course_to_lecturer.get(section_key, f"unknown_{course_code}")
                course_info = f"{course_code} (Section {section_num})"
                teacher_schedule[lecturer_id][best_block] = course_info
            else:
                print(f"  No available block for section {section_key}")
    
    # Second pass: Assign students to sections
    for course_code, requests in course_requests.items():
        if course_code not in course_details:
            continue
            
        course = course_details[course_code]
        num_sections = course.get('num_sections', 1)
        max_size = course.get('max_size', 25)
        
        # Sort requests by priority
        priority_map = {p: i for i, p in enumerate(rules['priority_order'])}
        requests.sort(key=lambda x: priority_map.get(x.get('Type', 'Recommended'), 999))
        
        # Assign students to sections
        for req in requests:
            student_id = req.get('student ID')
            if not student_id:
                unresolved.append(req)
                continue
            
            # Try to assign to any available section
            assigned = False
            for section_num in range(1, num_sections + 1):
                section_key = f"{course_code}_{section_num}"
                block = section_blocks.get(section_key)
                
                # Skip if section has no block or is full
                if not block or len(section_assignments[section_key]) >= max_size:
                    continue
                
                # Skip if student already has a class in this block
                if block in student_schedule[student_id]:
                    continue
                
                # Assign student to this section
                course_info = f"{course_code} (Section {section_num})"
                student_schedule[student_id][block] = course_info
                section_assignments[section_key].append(student_id)
                resolved.append(req)
                assigned = True
                break
            
            if not assigned:
                unresolved.append(req)
    
    # Convert defaultdicts to regular dicts for JSON
    student_schedule_dict = {student: dict(blocks) for student, blocks in student_schedule.items()}
    teacher_schedule_dict = {teacher: dict(blocks) for teacher, blocks in teacher_schedule.items()}
    
    print(f"Schedule generated. Assigned {len(resolved)} requests, {len(unresolved)} unresolved.")
    print(f"Number of students scheduled: {len(student_schedule_dict)}")
    print(f"Number of teachers scheduled: {len(teacher_schedule_dict)}")
    
    return student_schedule_dict, teacher_schedule_dict, resolved, unresolved, section_assignments

def save_results(results, output_dir='simple_output'):
    """Save the scheduling results to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    student_schedule, teacher_schedule, resolved, unresolved, section_assignments = results
    
    # Save student schedules
    with open(f"{output_dir}/student_schedules.json", 'w') as f:
        json.dump(student_schedule, f, indent=4)
    
    # Save teacher schedules
    with open(f"{output_dir}/teacher_schedules.json", 'w') as f:
        json.dump(teacher_schedule, f, indent=4)
    
    # Save statistics
    total_requests = len(resolved) + len(unresolved)
    satisfaction_rate = (len(resolved) / total_requests * 100) if total_requests > 0 else 0
    
    stats = {
        'total_requests': total_requests,
        'resolved_requests': len(resolved),
        'unresolved_requests': len(unresolved),
        'satisfaction_rate': satisfaction_rate,
        'students_scheduled': len(student_schedule),
        'teachers_scheduled': len(teacher_schedule),
        'sections_created': len(section_assignments)
    }
    
    with open(f"{output_dir}/stats.json", 'w') as f:
        json.dump(stats, f, indent=4)
    
    print(f"Results saved to {output_dir} directory")
    print(f"Satisfaction rate: {satisfaction_rate:.2f}%")

def main():
    print("Starting simple scheduler...")
    
    # Load cleaned data
    data = load_cleaned_data()
    if not data:
        print("Failed to load data")
        return
    
    # Extract rules
    rules = extract_rules_and_constraints(data)
    
    # Preprocess data
    preprocessed = preprocess_data(data, rules)
    
    # Generate schedule
    results = generate_schedule(data, rules, preprocessed)
    
    # Save results
    save_results(results)
    
    print("Scheduling complete!")

if __name__ == "__main__":
    main() 