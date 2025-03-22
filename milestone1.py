import pandas as pd
import json
from collections import defaultdict
import os
import re
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Step 1: Load and Clean the Data
def load_and_clean_data(file_path='dataset.xlsx'):
    """
    Load and clean data from Excel file, standardizing formats and structure.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        dict: Structured data dictionary or None if loading fails
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"Error: File '{file_path}' not found.")
        return None
    
    # Check file size
    file_size = os.path.getsize(file_path)
    logger.info(f"File size: {file_size} bytes")
    if file_size == 0:
        logger.warning("Warning: The Excel file appears to be empty (0 bytes).")
    
    # Load Excel file
    try:
        xls = pd.ExcelFile(file_path)
        logger.info(f"Found sheets: {xls.sheet_names}")
        structured_data = {}
        
        # Update sheet mappings to match the actual sheet names in the file
        # Map actual sheet names to data structure keys
        sheet_mappings = {
            'Lecturer Details': 'course_listings',
            'Course list': 'course_characteristics',
            'Student requests': 'student_requests',
            'Rooms data': 'rooms'
        }
        
        # Process each sheet based on the actual sheet names
        for sheet_name, key in sheet_mappings.items():
            if sheet_name in xls.sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")
                sheet_data = pd.read_excel(xls, sheet_name)
                
                # Clean up sheet data - replace NaN with None for proper JSON serialization
                sheet_data = sheet_data.replace({np.nan: None})
                
                if not sheet_data.empty:
                    logger.info(f"{sheet_name} sheet has {len(sheet_data)} rows and {len(sheet_data.columns)} columns")
                    logger.info(f"Using original column names: {sheet_data.columns.tolist()}")
                    
                    # Process sheet-specific data
                    if key == 'course_characteristics':
                        structured_data[key] = []
                        # Process course characteristics with original column names
                        for _, row in sheet_data.iterrows():
                            row_dict = row.to_dict()
                            # Use original column names
                            if 'Available blocks' in row_dict and row_dict['Available blocks'] is not None:
                                row_dict['Available blocks'] = str(row_dict['Available blocks']).split(', ') if pd.notna(row_dict['Available blocks']) else []
                            if 'Unavailable blocks' in row_dict and row_dict['Unavailable blocks'] is not None:
                                row_dict['Unavailable blocks'] = str(row_dict['Unavailable blocks']).split(', ') if pd.notna(row_dict['Unavailable blocks']) else []
                            
                            # Convert numeric values to appropriate types
                            for field in ['Number of sections', 'Minimum section size', 'Target section size', 'Maximum section size', 'Length', 'Priority']:
                                if field in row_dict and row_dict[field] is not None:
                                    try:
                                        row_dict[field] = int(row_dict[field])
                                    except (ValueError, TypeError):
                                        # Keep as is if conversion fails
                                        pass
                            
                            structured_data[key].append(row_dict)
                    elif key == 'course_listings':
                        structured_data[key] = []
                        # Process course listings
                        for _, row in sheet_data.iterrows():
                            row_dict = row.to_dict()
                            
                            # Convert numeric values to appropriate types
                            for field in ['Lecturer ID', 'Section number', 'Length', 'Start Term']:
                                if field in row_dict and row_dict[field] is not None:
                                    try:
                                        row_dict[field] = int(row_dict[field])
                                    except (ValueError, TypeError):
                                        # Keep as is if conversion fails
                                        pass
                            
                            structured_data[key].append(row_dict)
                    elif key == 'student_requests':
                        structured_data[key] = []
                        # Process student requests
                        for _, row in sheet_data.iterrows():
                            row_dict = row.to_dict()
                            
                            # Convert numeric values to appropriate types
                            for field in ['student ID', 'Priority']:
                                if field in row_dict and row_dict[field] is not None:
                                    try:
                                        row_dict[field] = int(row_dict[field])
                                    except (ValueError, TypeError):
                                        # Keep as is if conversion fails
                                        pass
                            
                            structured_data[key].append(row_dict)
                    elif key == 'rooms':
                        structured_data[key] = []
                        # Process rooms data
                        for _, row in sheet_data.iterrows():
                            row_dict = row.to_dict()
                            
                            # Convert numeric values to appropriate types
                            for field in ['Room Number', 'Capacity']:
                                if field in row_dict and row_dict[field] is not None:
                                    try:
                                        row_dict[field] = int(row_dict[field])
                                    except (ValueError, TypeError):
                                        # Keep as is if conversion fails
                                        pass
                            
                            structured_data[key].append(row_dict)
                    else:
                        # Default processing for other sheets
                        structured_data[key] = []
                        for _, row in sheet_data.iterrows():
                            structured_data[key].append(row.to_dict())
                else:
                    logger.info(f"{sheet_name} sheet is empty")
                    structured_data[key] = []
            else:
                logger.info(f"Sheet '{sheet_name}' not found")
                # Initialize empty lists for missing mappings
                structured_data[key] = []
        
        # Extract rules from the RULES sheet
        if 'RULES' in xls.sheet_names:
            rules_data = pd.read_excel(xls, 'RULES').replace({np.nan: None})
            if not rules_data.empty:
                structured_data['rules'] = []
                for _, row in rules_data.iterrows():
                    rule_dict = row.to_dict()
                    structured_data['rules'].append(rule_dict)
                logger.info(f"Extracted {len(structured_data['rules'])} rules from RULES sheet")
        
        # Ensure all required keys exist
        for key in ['course_listings', 'course_characteristics', 'student_requests', 'rooms', 'rules']:
            if key not in structured_data:
                structured_data[key] = []
        
        # Add metadata about the data processing
        structured_data['metadata'] = {
            'source_file': file_path,
            'processing_date': pd.Timestamp.now().isoformat(),
            'total_courses': len(structured_data.get('course_characteristics', [])),
            'total_sections': len(structured_data.get('course_listings', [])),
            'total_requests': len(structured_data.get('student_requests', [])),
            'total_rooms': len(structured_data.get('rooms', []))
        }
        
        # Save to JSON
        with open('cleaned_data.json', 'w') as f:
            json.dump(structured_data, f, indent=4)
        logger.info("Data cleaned and saved to 'cleaned_data.json'")
        return structured_data
    
    except Exception as e:
        logger.error(f"Error loading Excel file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Extract blocks from rule text
def extract_blocks_from_rules(rules_data):
    """
    Extract block identifiers (e.g., "1A", "2B") from rule text.
    
    Args:
        rules_data (list): List of rule dictionaries
        
    Returns:
        list: List of unique block identifiers found in rules
    """
    blocks = []
    for rule in rules_data:
        if 'RULES' in rule and isinstance(rule['RULES'], str):
            # Look for block identifiers like "1A", "2B", etc.
            block_matches = re.findall(r'["\']\d+[A-Z]["\']', rule['RULES'])
            for match in block_matches:
                # Clean up the block identifier
                block = match.strip('\'"')
                if block not in blocks:
                    blocks.append(block)
    return blocks

# Step 2: Validate the Data and Generate Insights
def validate_data(data, file_path='dataset.xlsx'):
    """
    Validate the cleaned data, generate insights, and create validation report.
    
    Args:
        data (dict): Cleaned data dictionary
        file_path (str): Path to the original Excel file
        
    Returns:
        tuple: (validation_report, insights) lists
    """
    validation_report = []
    insights = []
    critical_issues = []
    warnings = []
    
    # Check if essential data is present
    for key in ['course_listings', 'course_characteristics', 'student_requests']:
        if key not in data or not data[key]:
            critical_issues.append(f"Missing or empty {key} data")
    
    # Process rules if available
    rules_text = []
    blocks = []
    if 'rules' in data and data['rules']:
        rules_text = [rule['RULES'] for rule in data['rules'] if 'RULES' in rule and rule['RULES'] is not None]
        blocks = extract_blocks_from_rules(data['rules'])
        insights.append(f"Identified {len(blocks)} unique blocks from rules: {', '.join(blocks)}")
    else:
        warnings.append("No rules found in the dataset")

    # Check request distribution (insight)
    request_types = defaultdict(int)
    for req in data['student_requests']:
        req_type = req.get('Type')
        if req_type:
            request_types[req_type] += 1
    
    total_requests = sum(request_types.values())
    insights.append(f"Total requests: {total_requests} (Required: {request_types.get('Required', 0)}, "
                    f"Requested: {request_types.get('Requested', 0)}, Recommended: {request_types.get('Recommended', 0)})")

    # Student demographics
    students_by_year = defaultdict(set)
    for req in data['student_requests']:
        student_id = req.get('student ID')
        year = req.get('College Year')
        if student_id is not None and year:
            students_by_year[year].add(student_id)
    
    total_students = sum(len(students) for students in students_by_year.values())
    insights.append(f"Total unique students: {total_students}")
    for year, students in sorted(students_by_year.items()):
        insights.append(f"{year}: {len(students)} students")

    # Check required courses by year
    required_courses = {
        '1st Year': 'BIB9', '2nd Year': 'BIB10', '3rd Year': 'BIB11', '4th Year': 'BIB12'
    }
    for year, course_code in required_courses.items():
        required_count = sum(1 for req in data['student_requests'] 
                            if req.get('College Year') == year and req.get('Course code') == course_code and req.get('Type') == 'Required')
        total_students = len(students_by_year[year])
        if total_students > 0 and required_count < total_students:
            warning_msg = f"Missing required course: Only {required_count}/{total_students} {year} students requested {course_code}"
            warnings.append(warning_msg)
        insights.append(f"{year} - {course_code}: {required_count}/{total_students} requested")

    # Check courses with no requests
    requested_courses = set(req.get('Course code') for req in data['student_requests'] if req.get('Course code'))
    all_courses = set(course.get('Course code') for course in data['course_characteristics'] if course.get('Course code'))
    no_request_courses = all_courses - requested_courses
    if no_request_courses:
        warnings.append(f"Courses with no requests: {', '.join(sorted(no_request_courses))}")
        insights.append(f"{len(no_request_courses)} courses have no student requests")

    # Check demand vs. capacity
    demand_by_course = defaultdict(int)
    for req in data['student_requests']:
        course_code = req.get('Course code')
        if course_code:
            demand_by_course[course_code] += 1
    
    oversubscribed_courses = []
    undersubscribed_courses = []
    no_demand_courses = []
    
    for course in data['course_characteristics']:
        course_code = course.get('Course code')
        if not course_code:
            continue
            
        demand = demand_by_course.get(course_code, 0)
        num_sections = course.get('Number of sections', 0)
        max_size = course.get('Maximum section size', 0)
        
        if num_sections and max_size:
            capacity = num_sections * max_size
            
            if demand > capacity:
                oversubscribed_courses.append((course_code, demand, capacity))
                warnings.append(f"Over-subscribed: {course_code} has {demand} requests but {capacity} spots")
            elif demand < 0.5 * capacity and demand > 0:
                undersubscribed_courses.append((course_code, demand, capacity))
                warnings.append(f"Under-subscribed: {course_code} has only {demand} requests for {capacity} spots")
            elif demand == 0 and num_sections > 0:
                no_demand_courses.append((course_code, num_sections))
                warnings.append(f"No demand: {course_code} has {num_sections} sections but 0 requests")
    
    if oversubscribed_courses:
        insights.append(f"{len(oversubscribed_courses)} courses are over-subscribed")
    if undersubscribed_courses:
        insights.append(f"{len(undersubscribed_courses)} courses are under-subscribed (less than 50% capacity)")
    if no_demand_courses:
        insights.append(f"{len(no_demand_courses)} courses have sections but no demand")

    # Check lecturer assignments
    lecturers = set(course.get('Lecturer ID') for course in data['course_listings'] if course.get('Lecturer ID'))
    insights.append(f"Total unique lecturers: {len(lecturers)}")
    
    # Courses per lecturer
    courses_per_lecturer = defaultdict(list)
    for course in data['course_listings']:
        lecturer_id = course.get('Lecturer ID')
        course_code = course.get('lecture Code')
        if lecturer_id and course_code:
            courses_per_lecturer[lecturer_id].append(course_code)
    
    # Calculate lecturer workload distribution
    if courses_per_lecturer:
        course_counts = [len(courses) for courses in courses_per_lecturer.values()]
        max_courses = max(course_counts)
        min_courses = min(course_counts)
        avg_courses = sum(course_counts) / len(course_counts)
        insights.append(f"Lecturers teach between {min_courses} and {max_courses} courses (avg: {avg_courses:.1f})")
        
        # Identify heavily loaded lecturers
        heavy_load = [lid for lid, courses in courses_per_lecturer.items() if len(courses) > avg_courses + 2]
        if heavy_load:
            warnings.append(f"{len(heavy_load)} lecturers have heavier than average course loads")
    
    # Check room data if available
    if 'rooms' in data and data['rooms']:
        unique_rooms = len(data['rooms'])
        total_capacity = sum(room.get('Capacity', 0) for room in data['rooms'])
        insights.append(f"Total unique rooms: {unique_rooms}")
        insights.append(f"Total room capacity: {total_capacity}")
        
        # Check if room capacity is sufficient
        total_students = sum(len(students) for students in students_by_year.values())
        if total_capacity < total_students:
            critical_issues.append(f"Insufficient room capacity: {total_capacity} seats for {total_students} students")
    else:
        rooms_available = False
        try:
            if os.path.exists(file_path):
                xls = pd.ExcelFile(file_path)
                if 'Rooms data' in xls.sheet_names:
                    rooms_data = pd.read_excel(file_path, 'Rooms data')
                    unique_rooms = rooms_data['Room Number'].nunique()
                    insights.append(f"Total unique rooms: {unique_rooms}")
                    rooms_available = True
        except Exception as e:
            logger.warning(f"Could not analyze Rooms data: {e}")
        
        if not rooms_available:
            warnings.append("No room data available for capacity planning")
    
    # Check data consistency
    course_codes_in_listings = set(course.get('lecture Code') for course in data['course_listings'] if course.get('lecture Code'))
    course_codes_in_characteristics = set(course.get('Course code') for course in data['course_characteristics'] if course.get('Course code'))
    
    missing_characteristics = course_codes_in_listings - course_codes_in_characteristics
    if missing_characteristics:
        warnings.append(f"Courses in listings but missing characteristics: {', '.join(sorted(missing_characteristics))}")
    
    missing_listings = course_codes_in_characteristics - course_codes_in_listings
    if missing_listings:
        warnings.append(f"Courses with characteristics but no listings: {', '.join(sorted(missing_listings))}")
    
    # Check for invalid priority values
    invalid_priorities = [(req.get('student ID'), req.get('Course code'), req.get('Priority')) 
                          for req in data['student_requests'] 
                          if req.get('Priority') not in [None, 1, 2, 3, 4, 5]]
    if invalid_priorities:
        warnings.append(f"Found {len(invalid_priorities)} requests with invalid priority values")
    
    # Check for duplicate requests
    student_course_pairs = defaultdict(list)
    for i, req in enumerate(data['student_requests']):
        student_id = req.get('student ID')
        course_code = req.get('Course code')
        if student_id and course_code:
            student_course_pairs[(student_id, course_code)].append(i)
    
    duplicate_requests = {k: v for k, v in student_course_pairs.items() if len(v) > 1}
    if duplicate_requests:
        warnings.append(f"Found {len(duplicate_requests)} duplicate student-course request pairs")

    # Write validation report
    with open('validation_report.md', 'w') as f:
        f.write("# Validation Report\n\n")
        
        f.write("## Data Overview\n")
        f.write(f"- Total courses: {len(data.get('course_characteristics', []))}\n")
        f.write(f"- Total course sections: {len(data.get('course_listings', []))}\n")
        f.write(f"- Total student requests: {total_requests}\n")
        f.write(f"- Total unique students: {total_students}\n\n")
        
        if critical_issues:
            f.write("## Critical Issues\n")
            f.write("\n".join(f"- CRITICAL: {issue}" for issue in critical_issues))
            f.write("\n\n")
        
        f.write("## Issues\n")
        f.write("\n".join(f"- {line}" for line in warnings) if warnings else "- No major issues found.\n")
        
        f.write("\n## Insights\n")
        f.write("\n".join(f"- {line}" for line in insights))
        
        # Add rules summary
        if rules_text:
            f.write("\n\n## Rules Summary\n")
            for i, rule in enumerate(rules_text, 1):
                if rule and len(rule) > 200:  # Truncate long rules
                    rule = rule[:200] + "..."
                f.write(f"- Rule {i}: {rule}\n")
    
    logger.info("Validation complete. Report saved to 'validation_report.md'")
    
    # Create a more detailed HTML report with screenshots and code
    create_detailed_report(data, warnings, insights, rules_text, critical_issues)
    
    return warnings, insights

# Create a more detailed report with screenshots and code
def create_detailed_report(data, warnings, insights, rules_text, critical_issues):
    with open('detailed_report.html', 'w') as f:
        f.write('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Course Scheduling Data Analysis - Detailed Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1, h2, h3 { color: #333; }
                .container { max-width: 1200px; margin: 0 auto; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Course Scheduling Data Analysis - Detailed Report</h1>
                
                <h2>1. Data Overview</h2>
        ''')
        
        # Data Overview
        student_count = len(set(req['student ID'] for req in data['student_requests'])) if data['student_requests'] else 0
        
        f.write(f'''
                <p>The dataset consists of:</p>
                <ul>
                    <li><strong>Courses:</strong> {len(data['course_characteristics'])}</li>
                    <li><strong>Course Sections:</strong> {len(data['course_listings'])}</li>
                    <li><strong>Student Requests:</strong> {len(data['student_requests'])}</li>
                    <li><strong>Unique Students:</strong> {student_count}</li>
                </ul>
                
                <h2>2. Data Processing</h2>
                <p>The raw Excel data was processed to create a structured JSON format with the following components:</p>
                <ul>
                    <li><strong>Course Listings:</strong> Information about course sections and lecturers</li>
                    <li><strong>Course Characteristics:</strong> Details about each course including availability and capacity</li>
                    <li><strong>Student Requests:</strong> Student course requests including priorities</li>
                    <li><strong>Rules:</strong> Scheduling rules extracted from the RULES sheet</li>
                </ul>
                
                <h3>Code Sample - Data Loading and Cleaning:</h3>
                <pre>
def load_and_clean_data(file_path='dataset.xlsx'):
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{{file_path}}' not found.")
        return None
    
    # Load Excel file
    try:
        xls = pd.ExcelFile(file_path)
        print(f"Found sheets: {{xls.sheet_names}}")
        structured_data = {{}}
        
        # Process sheets and create structured data
        # ...
        
        return structured_data
    except Exception as e:
        print(f"Error loading Excel file: {{e}}")
        return None
                </pre>
                
                <h2>3. Validation Results</h2>
                <h3>Issues Identified:</h3>
                <ul>
        ''')
        
        # Validation Issues
        if warnings:
            for issue in warnings:
                f.write(f'<li>{issue}</li>\n')
        else:
            f.write('<li>No major issues found.</li>\n')
        
        f.write('''
                </ul>
                
                <h3>Key Insights:</h3>
                <ul>
        ''')
        
        # Insights
        for insight in insights:
            f.write(f'<li>{insight}</li>\n')
        
        f.write('''
                </ul>
                
                <h2>4. Rules Analysis</h2>
                <p>The following scheduling rules were identified from the dataset:</p>
                <ul>
        ''')
        
        # Rules
        if rules_text:
            for i, rule in enumerate(rules_text, 1):
                if len(rule) > 200:  # Truncate long rules
                    rule = rule[:200] + "..."
                f.write(f'<li><strong>Rule {i}:</strong> {rule}</li>\n')
        else:
            f.write('<li>No rules found or extracted.</li>\n')
        
        f.write('''
                </ul>
                
                <h2>5. Data Samples</h2>
                <h3>Course Characteristics Sample:</h3>
                <table>
                    <tr>
                        <th>Course Code</th>
                        <th>Title</th>
                        <th>Length</th>
                        <th>Priority</th>
                        <th>Capacity</th>
                    </tr>
        ''')
        
        # Course Samples
        sample_courses = data['course_characteristics'][:5] if data['course_characteristics'] else []
        for course in sample_courses:
            f.write(f'''
                    <tr>
                        <td>{course.get('Course code', 'N/A')}</td>
                        <td>{course.get('Title', 'N/A')}</td>
                        <td>{course.get('Length', 'N/A')}</td>
                        <td>{course.get('Priority', 'N/A')}</td>
                        <td>{course.get('Maximum section size', 'N/A')}</td>
                    </tr>
            ''')
        
        f.write('''
                </table>
                
                <h3>Student Requests Sample:</h3>
                <table>
                    <tr>
                        <th>Student ID</th>
                        <th>College Year</th>
                        <th>Course Code</th>
                        <th>Type</th>
                        <th>Priority</th>
                    </tr>
        ''')
        
        # Student Request Samples
        sample_requests = data['student_requests'][:5] if data['student_requests'] else []
        for request in sample_requests:
            f.write(f'''
                    <tr>
                        <td>{request.get('student ID', 'N/A')}</td>
                        <td>{request.get('College Year', 'N/A')}</td>
                        <td>{request.get('Course code', 'N/A')}</td>
                        <td>{request.get('Type', 'N/A')}</td>
                        <td>{request.get('Priority', 'N/A')}</td>
                    </tr>
            ''')
        
        f.write('''
                </table>
                
                <h2>6. Conclusion</h2>
                <p>
                    This analysis provides a structured view of the course scheduling data, including validation of key metrics,
                    identification of potential issues, and extraction of scheduling rules. The data has been cleaned and 
                    structured to facilitate further scheduling optimizations.
                </p>
                
                <p>
                    Based on the analysis, we can identify scheduling constraints, course demand patterns, and potential 
                    capacity issues that need to be addressed in the scheduling process.
                </p>
            </div>
        </body>
        </html>
        ''')
    
    print("Detailed HTML report created at 'detailed_report.html'")

# Main Execution
if __name__ == "__main__":
    # Load and clean the data
    file_path = 'dataset.xlsx'
    cleaned_data = load_and_clean_data(file_path)
    
    # Validate the data if data was loaded successfully
    if cleaned_data:
        validate_data(cleaned_data, file_path)
    else:
        print("Data loading failed. Validation skipped.")