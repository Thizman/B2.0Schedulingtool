# B2.0 Scheduling Tool

An interactive Python scheduling tool that automates shift assignments based on employee availability and preferences.

## Features

### Automated Scheduling with Smart Priorities
1. **Equal Distribution** - Top priority: ensures all timeslots have roughly equal staffing
2. **Maximum Desk Utilization** - Fills as many desks as possible
3. **Fair Coverage** - Everyone gets at least one shift per week
4. **Minimum Shift Length** - Respects configurable minimum (default 3 hours)
5. **Hours Prioritization** - Assigns based on preferred → agreed → max hours
6. **Smart Gap Filling** - Only schedules short shifts as last resort (clearly marked)

### Interactive GUI Features
- **CSV Import** - Easy file selection with validation
- **Week Management** - Input week number, auto-calculates dates (Monday start)
- **Configuration Options**:
  - Desks available (simultaneous workers)
  - Minimum shift length (hours)
- **Visual Schedule Display**:
  - Daily view (Monday-Thursday)
  - Color-coded slots (green=filled, red=unfilled)
  - Short shifts marked in orange
  - Shows current staffing vs. capacity
- **Hours Tracker**:
  - Real-time hours per person
  - Color-coded status (green=good, orange=below preferred, red=below agreed)
  - Comparison with preferred/agreed/max hours

## CSV File Format

### Required Columns
```
name,agreed hours per week,max hours per week,preferred hours per week
```

### Availability Columns (Monday-Thursday)
Format: `[DAY][TIMECODE]`
- Days: `M` (Monday), `TU` (Tuesday), `W` (Wednesday), `TH` (Thursday)
- Time codes: `1011`, `1112`, `1213`, `1314`, `1415`, `1516`, `1617`
- Whole day: `MW`, `TUW`, `WW`, `THW`

### Example Columns
```
M1011,M1112,M1213,M1314,M1415,M1516,M1617,MW,TU1011,TU1112,...,THW
```

### Data Types
- **name**: string
- **hours columns**: integer
- **availability columns**: boolean (1/true/yes or 0/false/no)

## Installation

### Requirements
- Python 3.6 or higher
- tkinter (usually included with Python)

### Running the Tool
```bash
python scheduler.py
```

## Usage

1. **Launch the application**
   ```bash
   python scheduler.py
   ```

2. **Load CSV file**
   - Click "Browse" button
   - Select your availability CSV file
   - Confirmation message appears when loaded

3. **Configure settings**
   - Set number of desks available
   - Set minimum shift length (default: 3 hours)

4. **Set week information**
   - Enter week number
   - Click "Update" to see date range

5. **Generate schedule**
   - Click "Generate Schedule" button
   - View results in two tabs:
     - **Weekly Schedule**: See who's working when
     - **Hours Tracker**: Monitor individual hours

## Schedule Display

### Color Coding
- 🟢 **Green slots**: Fully staffed
- 🔴 **Red slots**: Understaffed (with warning)
- 🟠 **Orange text**: Short shift (below minimum)

### Reading the Schedule
- Each day shows 7 timeslots (10:00-16:30)
- People assigned to each slot are listed
- Capacity shown as "X/Y filled" when understaffed
- Short shifts marked with "[SHORT]" tag

## Hours Tracker

### Status Colors
- 🟢 **Green**: At or above preferred hours
- 🟠 **Orange**: Between agreed and preferred hours
- 🔴 **Red**: Below agreed hours

### Columns
- **Name**: Employee name
- **Scheduled**: Hours assigned this week
- **Preferred**: Target hours
- **Agreed**: Minimum contracted hours
- **Max**: Maximum available hours

## Working Hours

- **Days**: Monday - Thursday only
- **Times**: 10:00 - 16:30
- **Timeslots**:
  - 10:00-11:00
  - 11:00-12:00
  - 12:00-13:00
  - 13:00-14:00
  - 14:00-15:00
  - 15:00-16:00
  - 16:00-16:30 (0.5 hours)

## Algorithm Details

### Phase 1: Initial Assignment
- Gives everyone at least one shift
- Prioritizes people with higher preferred hours
- Maintains equal distribution across timeslots

### Phase 2: Hour Optimization
- Fills additional shifts based on preferences
- Prioritizes people furthest from their preferred hours
- Continues until max hours reached or no slots available

### Phase 3: Gap Filling
- Attempts to fill remaining empty slots
- Only assigns short shifts if absolutely necessary
- Clearly marks these as exceptions

## Sample CSV

A sample CSV file (`sample_availability.csv`) is included with 8 example employees showing the correct format.

## Troubleshooting

### Common Issues

**"Please load a CSV file first"**
- Make sure to browse and select a valid CSV file before generating schedule

**"Failed to load CSV"**
- Check that column names match exactly (case-sensitive)
- Verify boolean values are: 1/0, true/false, or yes/no
- Ensure all required columns are present

**Many red (unfilled) slots**
- Increase desks available if set too high
- Check if employees have sufficient availability
- Verify max hours aren't too restrictive

**Too many short shifts**
- Consider lowering minimum shift length
- Check if availability patterns allow longer continuous shifts
- Review employee availability for gaps

## Tips for Best Results

1. **Employee Availability**: Encourage continuous blocks of availability for better shift assignments
2. **Desk Configuration**: Set realistic desk numbers based on actual capacity
3. **Hours Balancing**: Set preferred hours slightly above agreed hours for flexibility
4. **Minimum Shift**: Use 3-4 hours for optimal scheduling results

## License

This tool is provided as-is for scheduling purposes
