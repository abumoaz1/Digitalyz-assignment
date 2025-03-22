import json
import matplotlib.pyplot as plt
import pandas as pd
import os

def load_schedule_data(directory='simple_output'):
    """Load schedule data from JSON files"""
    # Load student schedules
    with open(f"{directory}/student_schedules.json", 'r') as f:
        student_schedules = json.load(f)
    
    # Load teacher schedules
    with open(f"{directory}/teacher_schedules.json", 'r') as f:
        teacher_schedules = json.load(f)
    
    # Load stats
    with open(f"{directory}/stats.json", 'r') as f:
        stats = json.load(f)
    
    return student_schedules, teacher_schedules, stats

def create_block_distribution_chart(student_schedules, output_dir='visualizations'):
    """Create a bar chart showing class distribution by block"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Count courses per block
    block_counts = {}
    for student, schedule in student_schedules.items():
        for block in schedule:
            if block not in block_counts:
                block_counts[block] = 0
            block_counts[block] += 1
    
    # Sort blocks
    sorted_blocks = sorted(block_counts.keys())
    counts = [block_counts[block] for block in sorted_blocks]
    
    # Create chart
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_blocks, counts)
    plt.title('Student Class Distribution by Block')
    plt.xlabel('Block')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add count labels
    for i, count in enumerate(counts):
        plt.text(i, count + 5, str(count), ha='center')
    
    # Save chart
    plt.tight_layout()
    plt.savefig(f"{output_dir}/block_distribution.png")
    plt.close()
    
    return block_counts

def create_course_enrollment_chart(student_schedules, output_dir='visualizations'):
    """Create a bar chart showing enrollment by course"""
    # Count enrollment by course
    course_enrollments = {}
    for student, schedule in student_schedules.items():
        for block, course_info in schedule.items():
            course_code = course_info.split(' ')[0]
            if course_code not in course_enrollments:
                course_enrollments[course_code] = 0
            course_enrollments[course_code] += 1
    
    # Sort courses by enrollment
    sorted_courses = sorted(course_enrollments.items(), key=lambda x: x[1], reverse=True)
    
    # Only show top 20 courses
    top_courses = sorted_courses[:20]
    courses = [c[0] for c in top_courses]
    enrollments = [c[1] for c in top_courses]
    
    # Create chart
    plt.figure(figsize=(12, 7))
    bars = plt.bar(courses, enrollments)
    plt.title('Top 20 Courses by Enrollment')
    plt.xlabel('Course')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add enrollment labels
    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width()/2, 
            bar.get_height() + 1, 
            str(int(bar.get_height())), 
            ha='center'
        )
    
    # Save chart
    plt.tight_layout()
    plt.savefig(f"{output_dir}/course_enrollment.png")
    plt.close()
    
    return course_enrollments

def create_student_schedule_table(student_schedules, output_dir='visualizations'):
    """Create an HTML table showing sample student schedules"""
    # Get all blocks
    all_blocks = set()
    for student, schedule in student_schedules.items():
        all_blocks.update(schedule.keys())
    sorted_blocks = sorted(all_blocks)
    
    # Sample 10 students
    sample_students = list(student_schedules.keys())[:10]
    
    # Create a DataFrame for easier display
    data = []
    for student in sample_students:
        row = {'Student ID': student}
        schedule = student_schedules[student]
        for block in sorted_blocks:
            row[block] = schedule.get(block, '')
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save as HTML
    html_table = df.to_html(index=False)
    with open(f"{output_dir}/student_schedules.html", 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sample Student Schedules</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>Sample Student Schedules</h1>
        """)
        f.write(html_table)
        f.write("""
        </body>
        </html>
        """)

def create_satisfaction_chart(stats, output_dir='visualizations'):
    """Create a pie chart showing request satisfaction rate"""
    resolved = stats['resolved_requests']
    unresolved = stats['unresolved_requests']
    
    # Create chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        [resolved, unresolved], 
        labels=['Resolved', 'Unresolved'], 
        autopct='%1.1f%%',
        colors=['#4CAF50', '#F44336'],
        explode=(0.1, 0),
        shadow=True,
        startangle=90
    )
    plt.title('Request Resolution Rate')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    # Save chart
    plt.tight_layout()
    plt.savefig(f"{output_dir}/satisfaction_rate.png")
    plt.close()

def create_summary_dashboard(stats, block_counts, output_dir='visualizations'):
    """Create a summary dashboard HTML page"""
    with open(f"{output_dir}/dashboard.html", 'w') as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Schedule Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                .dashboard { display: flex; flex-wrap: wrap; }
                .metric-card { 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    padding: 15px; 
                    margin: 10px; 
                    flex: 1 1 200px; 
                    text-align: center;
                }
                .stat { font-size: 24px; font-weight: bold; color: #007bff; }
                .charts { display: flex; flex-wrap: wrap; }
                .chart { margin: 10px; flex: 1 1 45%; }
                img { max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Schedule Dashboard</h1>
            
            <div class="dashboard">
                <div class="metric-card">
                    <h3>Satisfaction Rate</h3>
                    <div class="stat">""")
        f.write(f"{stats['satisfaction_rate']:.2f}%")
        f.write("""</div>
                </div>
                <div class="metric-card">
                    <h3>Total Requests</h3>
                    <div class="stat">""")
        f.write(f"{stats['total_requests']}")
        f.write("""</div>
                </div>
                <div class="metric-card">
                    <h3>Students Scheduled</h3>
                    <div class="stat">""")
        f.write(f"{stats['students_scheduled']}")
        f.write("""</div>
                </div>
                <div class="metric-card">
                    <h3>Teachers Scheduled</h3>
                    <div class="stat">""")
        f.write(f"{stats['teachers_scheduled']}")
        f.write("""</div>
                </div>
            </div>
            
            <h2>Schedule Visualizations</h2>
            <div class="charts">
                <div class="chart">
                    <h3>Request Resolution Rate</h3>
                    <img src="satisfaction_rate.png" alt="Satisfaction Rate">
                </div>
                <div class="chart">
                    <h3>Student Distribution by Block</h3>
                    <img src="block_distribution.png" alt="Block Distribution">
                </div>
                <div class="chart">
                    <h3>Top Courses by Enrollment</h3>
                    <img src="course_enrollment.png" alt="Course Enrollment">
                </div>
            </div>
            
            <h2>View More Details</h2>
            <p><a href="student_schedules.html">Sample Student Schedules</a></p>
            
        </body>
        </html>
        """)

def main():
    """Main function to create visualizations"""
    print("Creating schedule visualizations...")
    
    # Create output directory
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    student_schedules, teacher_schedules, stats = load_schedule_data()
    
    # Create visualizations
    block_counts = create_block_distribution_chart(student_schedules, output_dir)
    create_course_enrollment_chart(student_schedules, output_dir)
    create_student_schedule_table(student_schedules, output_dir)
    create_satisfaction_chart(stats, output_dir)
    create_summary_dashboard(stats, block_counts, output_dir)
    
    print(f"Visualizations created in {output_dir} directory")

if __name__ == "__main__":
    main() 