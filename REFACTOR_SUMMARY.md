# Scheduler Refactor Summary

## Overview
Successfully refactored the B2.0 Scheduling Tool to work with fixed shifts instead of flexible time slots, extended to 8 days (2 weeks), and implemented rigidity-based shift preferences.

## Key Changes Made

### 1. **Data Structure Updates**

#### Schedule Data Structure
- **Old**: `{day: {person_name: {'start': slot_idx, 'end': slot_idx, 'hours': float, 'is_short': bool}}}`
- **New**: `{day: {person_name: {'shifts': [shift_codes], 'hours': float}}}`

#### Temporary Schedule (Algorithm Tracking)
- **Old**: `{day: {slot_idx: [people]}}`
- **New**: `{day: {shift_code: [people]}}`

#### Shift Definitions
Fixed shifts with codes:
- `0930`: 9:30-10:30 (1.0h)
- `1030`: 10:30-12:45 (2.25h)
- `1315`: 13:15-15:30 (2.25h)
- `1530`: 15:30-17:00 (1.5h)

### 2. **Core Algorithm Rewrite**

#### `run_scheduling_algorithm(desks_per_day, rigidity, total_hours_target)`
**Complete rewrite** to work with fixed shift combinations:

- **Rigidity Parameter** (0-100):
  - **High (70-100)**: Prefer full morning (0930+1030) or full afternoon (1315+1530)
  - **Medium (30-70)**: Allow cross-break combinations (1030+1315)
  - **Low (0-30)**: Allow individual shifts including short ones

- **Four-Phase Approach**:
  1. **Phase 1**: Give everyone at least one shift combination
  2. **Phase 2**: Aggressively fill to preferred hours
  3. **Phase 3**: Use agreed hours tier if under target
  4. **Phase 4**: Use max hours tier as last resort

- **Hard Constraints**:
  - Never exceed desk capacity per shift
  - Never exceed max hours per person
  - Respect mandatory break (12:45-13:15)

### 3. **New Methods Created**

#### `find_best_available_shift_combo(person, desks_per_day, rigidity, shift_counts, mode)`
Replaces `find_best_available_shift()`. Finds optimal shift combinations based on:
- Rigidity level
- Person's availability
- Current hours budget
- Desk capacity
- Balanced distribution

**Shift combination priorities** vary by rigidity:
```python
# High rigidity
[['0930', '1030'], ['1315', '1530'], ['1030'], ['1315'], ['1530'], ['0930']]

# Medium rigidity
[['0930', '1030'], ['1315', '1530'], ['1030', '1315'], ['1030'], ['1315'], ['1530'], ['0930']]

# Low rigidity
[['1030', '1315'], ['0930', '1030'], ['1315', '1530'], ['1030'], ['1315'], ['1530'], ['0930']]
```

#### `assign_shift_combo_to_person(person, shift_combo, shift_counts)`
Replaces `assign_shift_to_person()`. Assigns a shift combination and updates tracking.

#### `export_csv()`
**NEW METHOD** - Exports schedule to CSV format:
- Columns: Name, Day, Shifts, Hours
- Shifts formatted as time ranges (e.g., "9:30-10:30, 10:30-12:45")

### 4. **Schedule Conversion Update**

#### `convert_to_person_schedule()`
**Rewritten** to convert shift-code-based schedule to person-based:
- Removed `min_shift` parameter
- Groups shift codes per person per day
- Calculates total hours from shift definitions

### 5. **Display Updates**

#### `display_schedule()`
**Restructured** for 2-week vertical layout:
- **Week 1 Section**: Days 0-3 in 2x2 grid
- **Week 2 Section**: Days 4-7 in 2x2 grid
- Vertical stacking with week labels

#### `create_day_block(parent, day, day_idx, desks, row, col)`
**Complete rewrite** using shift codes:
- Removed `min_shift` parameter
- Fixed shift heights: `{"0930": 40, "1030": 90, "1315": 90, "1530": 60}`
- Draws grid lines between shifts
- Lane assignment algorithm ensures person keeps same lane across shifts
- Displays shift codes with start/end times

### 6. **Export Functions**

#### `create_export_image(file_path, week_text)`
**Completely rewritten** for shift-based structure:
- Increased image dimensions (1600x1400) for 8 days
- 2x4 grid layout (2 columns, 4 rows)
- Uses shift heights instead of slot heights
- Simplified block rendering for space
- Maintains color coding and warnings

#### `export_csv()`
**NEW** - Exports schedule to CSV with shift time ranges

### 7. **Removed Methods**

- `fill_remaining_gaps_aggressively()` - No longer needed with new algorithm
- `find_any_available_shift_aggressive()` - No longer needed with new algorithm

### 8. **Bug Fixes**

- Removed undefined `min_shift` variable references in `generate_schedule()`
- Removed undefined `self.min_shift_length` references in `display_schedule()`
- Fixed schedule data structure inconsistencies

## Key Features Implemented

1. **Fixed Shifts**: 4 predefined shifts with specific times and durations
2. **8-Day Schedule**: Extended from 4 days to 8 days (2 weeks)
3. **Rigidity Parameter**: Controls preference for longer vs. shorter shift combinations
4. **Mandatory Break**: Enforced 30-min break between 12:45-13:15
5. **Split Shifts**: When someone works both morning and afternoon, shown as separate blocks
6. **CSV Export**: New export functionality for schedule data
7. **Vertical Layout**: 2-week layout displayed vertically with clear separation

## Data Flow

1. **CSV Input** → Parse availability by shift codes (0930, 1030, 1315, 1530)
2. **Algorithm** → Assigns shift combinations based on rigidity and constraints
3. **temp_schedule** → `{day: {shift_code: [people]}}`
4. **convert_to_person_schedule()** → `{day: {person: {'shifts': [codes], 'hours': float}}}`
5. **Display/Export** → Renders using shift codes and definitions

## Testing Recommendations

1. **Test with varying rigidity levels**: 0, 50, 100
2. **Test with different desk capacities**: Low (4), Medium (8), High (12)
3. **Test availability patterns**: Full days, morning only, afternoon only, mixed
4. **Test edge cases**: Very high target hours, very low target hours
5. **Test exports**: Both PNG and CSV formats
6. **Verify break enforcement**: No one scheduled 1030+1315 without split

## Files Modified

- `/home/user/B2.0Schedulingtool/scheduler.py` (Complete refactor)

## Next Steps

1. Test the scheduler with sample data
2. Verify all shift combinations work as expected
3. Test export functions thoroughly
4. Consider adding validation for CSV input format
5. Add user feedback for schedule generation progress
