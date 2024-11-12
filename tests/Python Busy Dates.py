# Import the necessary libraries
import pandas as pd

# Assuming Power BI will pass the table as 'dataset'
df = dataset

# Convert 'StartDt' and 'EndDt' to datetime for processing
df['StartDt'] = pd.to_datetime(df['StartDt'], errors='coerce')
df['EndDt'] = pd.to_datetime(df['EndDt'], errors='coerce')

# Extract the unique trainer names from the 'FullName' column
trainers = df['FullName'].unique()

# Helper function to group consecutive busy days into date ranges
def consecutive_date_ranges(dates, activity_names):
    ranges = []
    activities = []
    start_date = dates[0]
    current_activity = activity_names[0]
    
    for i in range(1, len(dates)):
        # If the current date is not consecutive or the activity changes, close the current range and start a new one
        if (dates[i] - dates[i-1]).days != 1 or activity_names[i] != current_activity:
            end_date = dates[i-1]
            ranges.append((start_date, end_date))
            activities.append(current_activity)
            start_date = dates[i]
            current_activity = activity_names[i]
    
    # Add the final range
    ranges.append((start_date, dates[-1]))
    activities.append(current_activity)
    
    return ranges, activities

# Function to identify and group busy days for each trainer
def get_busy_days(trainer, df):
    # Filter rows for the given trainer
    trainer_df = df[df['FullName'] == trainer]

    # Create lists to hold all the busy days and their associated activities
    busy_days = []
    activity_names = []

    # Iterate through each training session and capture all the days between StartDt and EndDt
    for index, row in trainer_df.iterrows():
        session_days = pd.date_range(row['StartDt'], row['EndDt'], freq='B').date  # Business days only
        busy_days.extend(session_days)
        activity_names.extend([row['ActivityName']] * len(session_days))  # Repeat ActivityName for each day

    if not busy_days:
        return pd.DataFrame({'FullName': [], 'Busy Start': [], 'Busy End': [], 'Days Busy': [], 'Status': []})

    # Sort the busy days and group them into consecutive ranges
    busy_days, activity_names = zip(*sorted(zip(busy_days, activity_names)))
    busy_ranges, activities = consecutive_date_ranges(busy_days, activity_names)

    # Calculate the number of days in each busy period
    days_busy = [(r[1] - r[0]).days + 1 for r in busy_ranges]  # +1 to include both start and end date

    # Create a DataFrame for the busy date ranges, number of days busy, and associated activities
    return pd.DataFrame({
        'FullName': trainer,
        'Busy Start': [r[0] for r in busy_ranges],
        'Busy End': [r[1] for r in busy_ranges],
        'Days Busy': days_busy,
        'Status': activities
    })

# Collect the busy ranges for all trainers
all_busy_ranges = pd.concat([get_busy_days(trainer, df) for trainer in trainers], ignore_index=True)

# Output the result to Power BI
all_busy_ranges
