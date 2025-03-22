# Scheduling System Instructions

## Setup

1. **Install Python**
   - Ensure you have Python 3.8+ installed
   - You can download it from [python.org](https://python.org)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the System

### Data Cleaning and Validation (Milestone 1)

```bash
python milestone1.py
```

This will:
- Load the raw Excel data
- Clean and validate the data
- Generate a validation report
- Save the cleaned data to `cleaned_data.json`

### Schedule Generation (Milestone 2)

For the original scheduler:
```bash
python milestone2.py
```

For the improved scheduler:
```bash
python simple_scheduler.py
```

This will:
- Load the cleaned data
- Generate a schedule
- Save results to `schedule_output` (original) or `simple_output` (improved)

### Visualizing Results

```bash
python visualize_schedule.py
```

This will:
- Generate charts and HTML reports
- Save visualizations to the `visualizations` directory
- Create a dashboard at `visualizations/dashboard.html`

## Viewing Results

1. Open `visualizations/dashboard.html` in a web browser to see the schedule overview
2. Explore the `visualizations` directory for detailed charts and reports
3. Check `simple_output` or `schedule_output` directories for raw JSON data

## Troubleshooting

If you encounter any issues:

1. **ImportError or ModuleNotFoundError**
   - Ensure you've installed all dependencies: `pip install -r requirements.txt`

2. **FileNotFoundError**
   - Make sure you've run the steps in order (milestone1.py before other scripts)
   - Check that `cleaned_data.json` exists

3. **Memory Errors**
   - The scheduling algorithm can be resource-intensive
   - Close other applications when running the scheduler

## Contact

For support or questions, please contact [your-email@example.com] 