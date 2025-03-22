# Project Structure

## Core Files

```
SchedulingSystem/
├── milestone1.py           # Data cleaning and validation script
├── milestone2.py           # Original scheduling algorithm
├── simple_scheduler.py     # Improved scheduling algorithm
├── visualize_schedule.py   # Visualization generator
├── requirements.txt        # Python dependencies
├── README.md               # Project overview
├── INSTRUCTIONS.md         # Usage instructions
├── algorithm_approach.md   # Algorithm documentation
├── final_report.md         # Comprehensive project report
```

## Input Data

```
SchedulingSystem/
├── data/
│   └── raw_data.xlsx       # Raw Excel data from Crestwood College
├── cleaned_data.json       # Processed data (output from milestone1.py)
```

## Output Directories

```
SchedulingSystem/
├── schedule_output/        # Output from milestone2.py
│   ├── schedule_analysis.json
│   ├── request_stats.md
│   ├── student_schedules.json
│   └── teacher_schedules.json
│
├── simple_output/          # Output from simple_scheduler.py
│   ├── stats.json
│   ├── student_schedules.json
│   └── teacher_schedules.json
│
├── visualizations/         # Output from visualize_schedule.py
│   ├── dashboard.html      # Main dashboard
│   ├── student_schedules.html
│   ├── block_distribution.png
│   ├── course_enrollment.png
│   └── satisfaction_rate.png
```

## Documentation Files

```
SchedulingSystem/
├── README.md               # Project overview
├── INSTRUCTIONS.md         # Usage instructions
├── algorithm_approach.md   # Algorithm documentation
├── final_report.md         # Comprehensive project report
├── PROJECT_STRUCTURE.md    # This file
```

## File Descriptions

### Core Scripts

- **milestone1.py**: Processes raw Excel data, cleans it, and generates validation reports
- **milestone2.py**: Original scheduling algorithm that attempts to optimize course assignments
- **simple_scheduler.py**: Improved scheduling algorithm with enhanced conflict resolution
- **visualize_schedule.py**: Generates visualizations and reports based on scheduling output

### Output Files

- **schedule_analysis.json**: Metrics and statistics about the generated schedule
- **request_stats.md**: Detailed breakdown of request resolution by priority
- **student_schedules.json**: Maps students to their assigned courses and blocks
- **teacher_schedules.json**: Maps teachers to their assigned courses and blocks
- **stats.json**: Summary statistics from the scheduler

### Visualization Files

- **dashboard.html**: Main dashboard with key metrics and charts
- **student_schedules.html**: HTML table of sample student schedules
- **block_distribution.png**: Chart showing student distribution across blocks
- **course_enrollment.png**: Chart showing enrollment by course
- **satisfaction_rate.png**: Pie chart of resolved vs. unresolved requests

### Documentation

- **README.md**: Overview of the project, goals, and approach
- **INSTRUCTIONS.md**: Step-by-step instructions for running the system
- **algorithm_approach.md**: Detailed explanation of the scheduling algorithm
- **final_report.md**: Comprehensive project report with results and analysis 