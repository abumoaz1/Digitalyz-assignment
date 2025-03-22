import json
import pandas as pd
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import os
from tabulate import tabulate
import numpy as np

# Step 1: Load Cleaned Data
def load_cleaned_data(file_path='cleaned_data.json'):
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None
            
        print(f"Opening file: {file_path}")
        with open(file_path, 'r') as f:
            print("Reading JSON data...")
            data = json.load(f)
            print(f"Data loaded successfully. Keys: {list(data.keys())}")
            return data
    except Exception as e:
        print(f"Error loading cleaned data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Step 2: Extract Rules and Constraints
def extract_rules_and_constraints(data):
    """Extract scheduling rules and constraints from data"""
    rules = {}
    
    # Extract blocks information from rules if available
    if 'rules' in data:
        for rule in data['rules']:
            if 'RULES' in rule:
                rule_text = rule['RULES']
                if "blocks" in rule_text.lower():
                    # Try to extract blocks information
                    rules['blocks_info'] = rule_text
    
    # Get all available blocks from course characteristics
    all_blocks = set()
    for course in data['course_characteristics']:
        if 'Available blocks' in course:
            all_blocks.update(course['Available blocks'])
    
    # Default blocks if not found in data
    if not all_blocks:
        all_blocks = {"1A", "1B", "2A", "2B", "3", "4A", "4B", "5A", "5B"}
    
    rules['all_blocks'] = sorted(list(all_blocks))
    
    # Extract other constraints
    rules['required_courses'] = {
        '1st Year': ['BIB9'], 
        '2nd Year': ['BIB10'], 
        '3rd Year': ['BIB11'], 
        '4th Year': ['BIB12']
    }
    
    # Priority order for request types
    rules['priority_order'] = ['Required', 'Requested', 'Recommended']
    
    return rules

# Step 3: Pre-process Data for Scheduling
def preprocess_data(data, rules):
    """Prepare data structures needed for scheduling"""
    # Map courses to lecturer IDs
    course_to_lecturer = {}
    for course in data['course_listings']:
        lecturer_id = course.get('Lecturer ID', '')
        course_code = course.get('lecture Code', '')
        if course_code and lecturer_id:
            # Handle multiple sections of the same course
            section = course.get('Section number', 1)
            course_key = f"{course_code}_{section}"
            course_to_lecturer[course_key] = lecturer_id
    
    # Map course codes to course details
    course_details = {}
    for course in data['course_characteristics']:
        course_code = course.get('Course code', '')
        if course_code:
            course_details[course_code] = {
                'title': course.get('Title', ''),
                'length': course.get('Length', 4),
                'priority': course.get('Priority', 0),
                'available_blocks': course.get('Available blocks', rules['all_blocks']),
                'unavailable_blocks': course.get('Unavailable blocks', []),
                'min_size': course.get('Minimum section size', 5),
                'target_size': course.get('Target section size', 20),
                'max_size': course.get('Maximum section size', 25),
                'num_sections': course.get('Number of sections', 1)
            }
    
    # Group student requests by course code
    course_requests = defaultdict(list)
    for req in data['student_requests']:
        course_code = req.get('Course code', '')
        if course_code:
            course_requests[course_code].append(req)
    
    # Sort requests by priority
    for course_code, requests in course_requests.items():
        # Sort by priority: Required > Requested > Recommended
        priority_map = {p: i for i, p in enumerate(rules['priority_order'])}
        requests.sort(key=lambda x: priority_map.get(x.get('Type', 'Recommended'), 999))
    
    return {
        'course_to_lecturer': course_to_lecturer,
        'course_details': course_details,
        'course_requests': course_requests
    }

# Step 4: Generate Schedule Using Optimization
def generate_schedule(data, rules, preprocessed_data):
    """Generate optimized schedule based on constraints and priorities"""
    # Debug information
    print(f"Data is None? {data is None}")
    print(f"Rules is None? {rules is None}")
    print(f"Preprocessed data is None? {preprocessed_data is None}")
    
    if preprocessed_data:
        print(f"Preprocessed data keys: {list(preprocessed_data.keys())}")
    
    # Check if input data is valid
    if not data or not rules or not preprocessed_data:
        print("Error: Missing required data for scheduling. Ensure data, rules, and preprocessed_data are properly initialized.")
        return {}, {}, [], [], {}
        
    # Extract preprocessed data
    print("Extracting preprocessed data...")
    try:
        print("Getting course_to_lecturer...")
        course_to_lecturer = preprocessed_data.get('course_to_lecturer', {})
        print("Getting course_details...")
        course_details = preprocessed_data.get('course_details', {})
        print("Getting course_requests...")
        course_requests = preprocessed_data.get('course_requests', defaultdict(list))
        
        print(f"Extracted course_to_lecturer: {bool(course_to_lecturer)}")
        print(f"Extracted course_details: {bool(course_details)}")
        print(f"Extracted course_requests: {bool(course_requests)}")
        
        # Print types for debugging
        print(f"Type of course_to_lecturer: {type(course_to_lecturer)}")
        print(f"Type of course_details: {type(course_details)}")
        print(f"Type of course_requests: {type(course_requests)}")
        
        # Check if course_requests is iterable
        print("Checking if course_requests is iterable...")
        try:
            print(f"course_requests: {type(course_requests)}, is empty? {len(course_requests) == 0}")
            # Check the first item if course_requests is not empty
            if course_requests:
                first_key = next(iter(course_requests), None)
                if first_key:
                    first_value = course_requests[first_key]
                    print(f"First course code: {first_key}, value type: {type(first_value)}, length: {len(first_value)}")
                    if first_value:
                        print(f"Sample request: {first_value[0] if first_value else None}")
                else:
                    print("course_requests has no keys")
            else:
                print("course_requests is empty")
                
            # Safe iteration
            count = 0
            for course_code, requests in course_requests.items():
                print(f"Found course_code: {course_code} with {len(requests)} requests")
                count += 1
                if count >= 3:  # Only show first 3 to avoid overwhelming output
                    break
            print("course_requests is iterable")
        except Exception as e:
            print(f"Error iterating course_requests: {str(e)}")
            print("Resetting course_requests to empty defaultdict")
            course_requests = defaultdict(list)
    except Exception as e:
        print(f"Error extracting preprocessed data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}, {}, [], [], {}
    
    # Initialize data structures for scheduling
    student_schedule = defaultdict(dict)  # {student_id: {block: course_info}}
    teacher_schedule = defaultdict(dict)  # {lecturer_id: {block: course_info}}
    section_assignments = defaultdict(list)  # {course_code_section: [student_ids]}
    section_blocks = {}  # {course_code_section: block}
    
    # Track resolved/unresolved requests
    resolved_requests = []
    unresolved_requests = []
    
    # First pass: Assign required courses to ensure they're scheduled
    # This handles BIB9, BIB10, BIB11, BIB12 and other required courses
    try:
        print("Starting first pass - assigning required courses...")
        print(f"Priority order: {rules['priority_order']}")
        for req_type in rules['priority_order']:
            print(f"Processing request type: {req_type}")
            course_count = 0
            for course_code, requests in course_requests.items():
                course_count += 1
                if course_count <= 3:  # Show debugging for first 3 courses
                    print(f"Processing course: {course_code} with {len(requests)} requests")
                
                # Get course details
                course = course_details.get(course_code, {})
                num_sections = course.get('num_sections', 1)
                max_size = course.get('max_size', 25)
                available_blocks = course.get('available_blocks', rules['all_blocks'])
                unavailable_blocks = course.get('unavailable_blocks', [])
                
                # Filter requests by current priority type
                type_requests = [r for r in requests if r.get('Type', '') == req_type]
                if not type_requests:
                    continue
                
                if course_count <= 3:  # Show debugging for first 3 courses
                    print(f"  Found {len(type_requests)} requests of type {req_type}")
                
                # Determine how many sections we need to create
                needed_sections = min(num_sections, (len(type_requests) + max_size - 1) // max_size)
                
                if course_count <= 3:  # Show debugging for first 3 courses
                    print(f"  Need {needed_sections} sections out of {num_sections} total")
                
                # Create sections and assign blocks
                assigned_blocks = set()
                for section_num in range(1, needed_sections + 1):
                    section_key = f"{course_code}_{section_num}"
                    
                    # Find best block for this section that doesn't conflict
                    best_block = None
                    if course_count <= 3 and section_num <= 2:  # Show debugging for first 3 courses, first 2 sections
                        print(f"  Looking for available block. Available blocks: {available_blocks}")
                        print(f"  Unavailable blocks: {unavailable_blocks}")
                        print(f"  Already assigned blocks: {assigned_blocks}")
                    
                    for block in available_blocks:
                        if block in unavailable_blocks or block in assigned_blocks:
                            if course_count <= 3 and section_num <= 2:
                                print(f"    Block {block} is unavailable or already assigned")
                            continue
                        
                        # Check lecturer availability for this block
                        lecturer_id = course_to_lecturer.get(section_key, f"unknown_{course_code}")
                        if block in teacher_schedule[lecturer_id]:
                            if course_count <= 3 and section_num <= 2:
                                print(f"    Block {block} conflicts with lecturer {lecturer_id}'s schedule")
                            continue
                        
                        # This block works
                        best_block = block
                        if course_count <= 3 and section_num <= 2:
                            print(f"    Found available block: {block}")
                        break
                    
                    if best_block:
                        assigned_blocks.add(best_block)
                        section_blocks[section_key] = best_block
                        
                        # Pre-assign the lecturer to this block
                        lecturer_id = course_to_lecturer.get(section_key, f"unknown_{course_code}")
                        course_info_str = f"{course_code} (Section {section_num})"
                        teacher_schedule[lecturer_id][best_block] = course_info_str
                        
                        if course_count <= 3 and section_num <= 2:  # Show debugging for first 3 courses, first 2 sections
                            print(f"  Assigned section {section_num} to block {best_block}")
                    else:
                        if course_count <= 3 and section_num <= 2:
                            print(f"  No available block found for section {section_num}!")
    except Exception as e:
        print(f"Error in first pass: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Second pass: Assign students to sections
    for req_type in rules['priority_order']:
        for course_code, requests in course_requests.items():
            # Filter requests by current priority type
            type_requests = [r for r in requests if r.get('Type', '') == req_type]
            if not type_requests:
                continue
            
            # Get course details
            course = course_details.get(course_code, {})
            num_sections = course.get('num_sections', 1)
            max_size = course.get('max_size', 25)
            
            # Assign students to pre-created sections
            for req in type_requests:
                student_id = req.get('student ID', '')
                if not student_id:
                    unresolved_requests.append(req)
                    continue
                
                # Try to assign to any available section
                assigned = False
                for section_num in range(1, num_sections + 1):
                    section_key = f"{course_code}_{section_num}"
                    block = section_blocks.get(section_key)
                    
                    # Skip if section wasn't assigned a block or is full
                    if not block or len(section_assignments[section_key]) >= max_size:
                        continue
                    
                    # Check if student is available in this block
                    if block in student_schedule[student_id]:
                        continue
                    
                    # Assign student to this section
                    course_info_str = f"{course_code} (Section {section_num})"
                    student_schedule[student_id][block] = course_info_str
                    section_assignments[section_key].append(student_id)
                    resolved_requests.append(req)
                    assigned = True
                    break
                
                if not assigned:
                    unresolved_requests.append(req)
    
    # Convert defaultdicts to regular dicts for JSON serialization
    student_schedule_dict = {student: dict(blocks) for student, blocks in student_schedule.items()}
    teacher_schedule_dict = {teacher: dict(blocks) for teacher, blocks in teacher_schedule.items()}
    
    return student_schedule_dict, teacher_schedule_dict, resolved_requests, unresolved_requests, section_assignments

# Step 5: Analyze Schedule Quality
def analyze_schedule(student_schedule, teacher_schedule, resolved, unresolved, section_assignments, course_details):
    """Analyze schedule quality metrics"""
    analysis = {}
    
    # Overall satisfaction rate
    total_requests = len(resolved) + len(unresolved)
    if total_requests > 0:
        satisfaction_rate = len(resolved) / total_requests * 100
    else:
        satisfaction_rate = 100
    
    analysis['satisfaction_rate'] = satisfaction_rate
    
    # Analyze by request type
    request_types = {}
    for req in resolved:
        req_type = req.get('Type', 'Unknown')
        request_types[req_type] = request_types.get(req_type, 0) + 1
    
    for req in unresolved:
        req_type = req.get('Type', 'Unknown')
        request_types[req_type] = request_types.get(req_type, 0)
    
    analysis['request_types'] = request_types
    
    # Section fill rates
    section_fill_rates = {}
    for section_key, students in section_assignments.items():
        course_code = section_key.split('_')[0]
        if course_code in course_details:
            max_size = course_details[course_code].get('max_size', 25)
            fill_rate = len(students) / max_size * 100 if max_size > 0 else 0
            section_fill_rates[section_key] = {
                'students': len(students),
                'capacity': max_size,
                'fill_rate': fill_rate
            }
    
    analysis['section_fill_rates'] = section_fill_rates
    
    # Average courses per student
    courses_per_student = {student: len(blocks) for student, blocks in student_schedule.items()}
    if courses_per_student:
        analysis['avg_courses_per_student'] = sum(courses_per_student.values()) / len(courses_per_student)
    else:
        analysis['avg_courses_per_student'] = 0
    
    # Average teaching load per teacher
    courses_per_teacher = {teacher: len(blocks) for teacher, blocks in teacher_schedule.items()}
    if courses_per_teacher:
        analysis['avg_courses_per_teacher'] = sum(courses_per_teacher.values()) / len(courses_per_teacher)
    else:
        analysis['avg_courses_per_teacher'] = 0
    
    return analysis

# Step 6: Visualize Schedule
def visualize_schedule(student_schedule, teacher_schedule, section_assignments, rules, analysis, output_dir='.'):
    """Create visualizations of the schedule"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a heatmap of student schedules by block
    blocks = rules['all_blocks']
    
    # Student block distribution
    block_counts = {block: 0 for block in blocks}
    for student, schedule in student_schedule.items():
        for block in schedule:
            if block in block_counts:
                block_counts[block] += 1
    
    # Plot student distribution by block
    plt.figure(figsize=(10, 6))
    plt.bar(block_counts.keys(), block_counts.values())
    plt.title('Student Distribution by Block')
    plt.xlabel('Block')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/student_block_distribution.png")
    plt.close()
    
    # Section fill rates visualization
    if analysis.get('section_fill_rates'):
        section_keys = list(analysis['section_fill_rates'].keys())
        fill_rates = [analysis['section_fill_rates'][k]['fill_rate'] for k in section_keys]
        
        plt.figure(figsize=(12, 6))
        plt.bar(section_keys, fill_rates)
        plt.title('Section Fill Rates')
        plt.xlabel('Section')
        plt.ylabel('Fill Rate (%)')
        plt.axhline(y=100, color='r', linestyle='-', alpha=0.3)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/section_fill_rates.png")
        plt.close()
    
    # Create a text-based visualization of some student schedules (sample of 5)
    student_samples = {}
    sample_students = list(student_schedule.keys())[:5]
    for student in sample_students:
        schedule = student_schedule[student]
        student_samples[student] = {block: schedule.get(block, '') for block in blocks}
    
    # Create a text-based visualization of some teacher schedules (sample of 5)
    teacher_samples = {}
    sample_teachers = list(teacher_schedule.keys())[:5]
    for teacher in sample_teachers:
        schedule = teacher_schedule[teacher]
        teacher_samples[teacher] = {block: schedule.get(block, '') for block in blocks}
    
    # Save as HTML tables
    with open(f"{output_dir}/schedule_visualization.html", 'w') as f:
        f.write('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Schedule Visualization</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .metrics { display: flex; flex-wrap: wrap; }
                .metric-card { border: 1px solid #ddd; border-radius: 5px; 
                               padding: 15px; margin: 10px; flex: 1 1 200px; }
                .stat { font-size: 24px; font-weight: bold; color: #007bff; }
            </style>
        </head>
        <body>
            <h1>Schedule Visualization</h1>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Satisfaction Rate</h3>
                    <div class="stat">''')
        f.write(f"{analysis['satisfaction_rate']:.2f}%")
        f.write('''</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Courses/Student</h3>
                    <div class="stat">''')
        f.write(f"{analysis['avg_courses_per_student']:.2f}")
        f.write('''</div>
                </div>
                <div class="metric-card">
                    <h3>Avg Courses/Teacher</h3>
                    <div class="stat">''')
        f.write(f"{analysis['avg_courses_per_teacher']:.2f}")
        f.write('''</div>
                </div>
            </div>
            
            <h2>Student Schedule Samples</h2>
            <table>
                <tr>
                    <th>Student ID</th>
        ''')
        
        # Write block headers
        for block in blocks:
            f.write(f"<th>{block}</th>")
        f.write("</tr>")
        
        # Write student schedules
        for student, schedule in student_samples.items():
            f.write(f"<tr><td>{student}</td>")
            for block in blocks:
                f.write(f"<td>{schedule.get(block, '')}</td>")
            f.write("</tr>")
        
        f.write('''
            </table>
            
            <h2>Teacher Schedule Samples</h2>
            <table>
                <tr>
                    <th>Teacher ID</th>
        ''')
        
        # Write block headers
        for block in blocks:
            f.write(f"<th>{block}</th>")
        f.write("</tr>")
        
        # Write teacher schedules
        for teacher, schedule in teacher_samples.items():
            f.write(f"<tr><td>{teacher}</td>")
            for block in blocks:
                f.write(f"<td>{schedule.get(block, '')}</td>")
            f.write("</tr>")
        
        f.write('''
            </table>
            
            <h2>Images</h2>
            <img src="student_block_distribution.png" alt="Student Block Distribution">
            <img src="section_fill_rates.png" alt="Section Fill Rates">
        </body>
        </html>
        ''')

# Step 7: Save Outputs
def save_outputs(student_schedule, teacher_schedule, resolved, unresolved, section_assignments, rules, analysis, output_dir='.'):
    """Save all outputs to files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Student Schedules
    with open(f"{output_dir}/student_schedules.json", 'w') as f:
        json.dump(student_schedule, f, indent=4)
    
    # Teacher Schedules
    with open(f"{output_dir}/teacher_schedules.json", 'w') as f:
        json.dump(teacher_schedule, f, indent=4)
    
    # Create a user-friendly version of student schedules
    with open(f"{output_dir}/student_schedules.md", 'w') as f:
        f.write("# Student Schedules\n\n")
        sample_students = list(student_schedule.keys())[:20]  # Show first 20 students
        
        for student in sample_students:
            f.write(f"## Student: {student}\n\n")
            
            # Create a table for this student's schedule
            headers = ["Block", "Course"]
            rows = []
            for block in sorted(rules['all_blocks']):
                course = student_schedule[student].get(block, "")
                rows.append([block, course])
            
            f.write(tabulate(rows, headers=headers, tablefmt="pipe"))
            f.write("\n\n")
    
    # Create a user-friendly version of teacher schedules
    with open(f"{output_dir}/teacher_schedules.md", 'w') as f:
        f.write("# Teacher Schedules\n\n")
        sample_teachers = list(teacher_schedule.keys())[:20]  # Show first 20 teachers
        
        for teacher in sample_teachers:
            f.write(f"## Teacher: {teacher}\n\n")
            
            # Create a table for this teacher's schedule
            headers = ["Block", "Course"]
            rows = []
            for block in sorted(rules['all_blocks']):
                course = teacher_schedule[teacher].get(block, "")
                rows.append([block, course])
            
            f.write(tabulate(rows, headers=headers, tablefmt="pipe"))
            f.write("\n\n")
    
    # Request resolution stats
    with open(f"{output_dir}/request_stats.md", 'w') as f:
        total_requests = len(resolved) + len(unresolved)
        resolved_count = len(resolved)
        unresolved_count = len(unresolved)
        
        f.write("# Request Resolution Stats\n\n")
        f.write(f"- **Total Requests**: {total_requests}\n")
        
        # Fix the syntax error in these lines
        if total_requests > 0:
            resolved_percentage = resolved_count/total_requests*100
            unresolved_percentage = unresolved_count/total_requests*100
        else:
            resolved_percentage = 0
            unresolved_percentage = 0
            
        f.write(f"- **Resolved**: {resolved_count} ({resolved_percentage:.2f}%)\n")
        f.write(f"- **Unresolved**: {unresolved_count} ({unresolved_percentage:.2f}%)\n\n")
        
        # Break down by priority
        f.write("## Priority Breakdown\n\n")
        f.write("| Priority | Resolved | Unresolved | Total | Success Rate |\n")
        f.write("|----------|----------|------------|-------|-------------|\n")
        
        # Count by priority
        priority_stats = defaultdict(lambda: {'resolved': 0, 'unresolved': 0})
        
        for req in resolved:
            priority = req.get('Type', 'Unknown')
            priority_stats[priority]['resolved'] += 1
        
        for req in unresolved:
            priority = req.get('Type', 'Unknown')
            priority_stats[priority]['unresolved'] += 1
        
        for priority, stats in priority_stats.items():
            total = stats['resolved'] + stats['unresolved']
            success_rate = (stats['resolved'] / total * 100) if total > 0 else 0
            f.write(f"| {priority} | {stats['resolved']} | {stats['unresolved']} | {total} | {success_rate:.2f}% |\n")
    
    # Save analysis results
    with open(f"{output_dir}/schedule_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=4)
    
    # Visualization
    visualize_schedule(student_schedule, teacher_schedule, section_assignments, rules, analysis, output_dir)

# Main execution
def main():
    """Main function to run the scheduling process"""
    try:
        print("Starting scheduling process...")
        
        # Create output directory
        output_dir = 'schedule_output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Load the cleaned data
        print("Loading cleaned data...")
        data = load_cleaned_data('cleaned_data.json')
        print(f"Data loaded: {'Success' if data else 'Failed'}")
        
        # Step 2: Extract rules and constraints
        print("Extracting rules and constraints...")
        rules = extract_rules_and_constraints(data)
        print(f"Rules extracted: {'Success' if rules else 'Failed'}")
        
        # Step 3: Preprocess data
        print("Preprocessing data...")
        preprocessed_data = preprocess_data(data, rules)
        print(f"Data preprocessed: {'Success' if preprocessed_data else 'Failed'}")
        
        # Step 4: Generate the schedule
        print("Generating schedule...")
        # Check if all required data is available
        if data is None or rules is None or preprocessed_data is None:
            print("Error: Missing required data for scheduling.")
            print(f"Data: {'Available' if data else 'Missing'}")
            print(f"Rules: {'Available' if rules else 'Missing'}")
            print(f"Preprocessed data: {'Available' if preprocessed_data else 'Missing'}")
            return
        
        try:
            print("Calling generate_schedule function...")
            result = generate_schedule(data, rules, preprocessed_data)
            print("Schedule generation successful")
            
            student_schedule, teacher_schedule, resolved, unresolved, section_assignments = result
            print(f"Got student schedule: {bool(student_schedule)}")
            print(f"Got teacher schedule: {bool(teacher_schedule)}")
            print(f"Got resolved requests: {len(resolved)}")
            print(f"Got unresolved requests: {len(unresolved)}")
            print(f"Got section assignments: {len(section_assignments)}")
        except Exception as e:
            print(f"Error in generate_schedule: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 5: Analyze the schedule
        print("Analyzing schedule quality...")
        try:
            analysis = analyze_schedule(
                student_schedule, teacher_schedule, resolved, unresolved, 
                section_assignments, preprocessed_data['course_details']
            )
            print("Schedule analysis complete")
        except Exception as e:
            print(f"Error in analyze_schedule: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 6 & 7: Visualize and save outputs
        print("Saving outputs and visualizations...")
        try:
            save_outputs(
                student_schedule, teacher_schedule, resolved, unresolved, 
                section_assignments, rules, analysis, output_dir
            )
            print("Outputs saved successfully")
        except Exception as e:
            print(f"Error in save_outputs: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"Scheduling complete! Results saved to '{output_dir}' directory.")
        if 'satisfaction_rate' in analysis:
            print(f"Satisfaction rate: {analysis['satisfaction_rate']:.2f}%")
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()