# Course Scheduling System

This project implements a course scheduling system for Crestwood College, as described in the assignment. The solution is divided into two milestones:

## Milestone 1: Data Cleaning and Validation

In this milestone, we:

1. Loaded and cleaned the raw data from the Excel file
2. Standardized formats and structures
3. Validated the data to identify inconsistencies and missing information
4. Generated a comprehensive validation report

### Key Components:
- `milestone1.py`: Loads, cleans, and validates the data
- `cleaned_data.json`: Structured JSON output
- `validation_report.md`: Validation findings and insights
- `detailed_report.html`: Detailed report with visualizations

### Data Cleaning Process:
- Read Excel sheets (Lecturer Details, Course list, Student requests, Rooms data)
- Converted data into structured JSON format
- Handled missing values and data type conversions
- Extracted rules from the RULES sheet

### Validation Insights:
- Identified courses with no student requests
- Found over-subscribed and under-subscribed courses
- Analyzed lecturer workload distribution
- Checked room capacity against student demand
- Validated required course enrollment by year

## Milestone 2: Schedule Generation

In this milestone, we:

1. Loaded the cleaned data from Milestone 1
2. Extracted scheduling rules and constraints
3. Preprocessed the data for scheduling
4. Generated course schedules
5. Analyzed the schedule quality

### Key Components:
- `milestone2.py`: Original scheduling implementation
- `simple_scheduler.py`: Simplified and improved scheduler
- Generated outputs:
  - Student schedules by block
  - Teacher schedules by block
  - Section assignments
  - Schedule analysis metrics

### Scheduling Approach:
1. **First Pass**: Assign course sections to time blocks
   - Consider course availability constraints
   - Avoid lecturer conflicts
   - Prioritize required courses

2. **Second Pass**: Assign students to course sections
   - Prioritize by request type (Required > Requested > Recommended)
   - Avoid student schedule conflicts
   - Respect section capacity limits

### Schedule Results:
- **Satisfaction Rate**: 53.19%
- **Total Requests**: 1,252
- **Resolved Requests**: 666
- **Unresolved Requests**: 586
- **Students Scheduled**: 156
- **Teachers Scheduled**: 24
- **Sections Created**: 83

### Challenges and Improvements:
- Handling courses with NULL or missing blocks
- Resolving conflicts between popular courses in the same block
- Dealing with over-subscribed courses
- Optimizing room assignments

## Running the Code

1. Ensure you have the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run Milestone 1 to clean and validate the data:
   ```
   python milestone1.py
   ```

3. Run the scheduler to generate course schedules:
   ```
   python simple_scheduler.py
   ```

## Future Improvements

For future iterations, we could enhance the scheduler with:

1. More sophisticated optimization algorithms (e.g., constraint satisfaction)
2. Room capacity and features consideration
3. Teacher preference weighting
4. Better handling of course prerequisites
5. Improved visualization of the generated schedules 