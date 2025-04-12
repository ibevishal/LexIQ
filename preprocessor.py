import re  # For working with regular expressions
import pandas as pd  # For data manipulation and analysis
import unicodedata  # For Unicode normalization

def preprocess(data):
    # Normalize unicode characters to standard form (e.g., remove non-breaking spaces)
    data = unicodedata.normalize("NFKC", data)

    # Define regex pattern to match WhatsApp message start: date, time, and dash separator
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\s?(am|pm|AM|PM)?\s-\s'

    # Split the entire chat into list entries using the pattern, skipping the first split part (not a message)
    messages = re.split(pattern, data)[1:]

    # Group every 4 entries into chunks: [date, time, am/pm, message]
    chunks = [messages[i:i+4] for i in range(0, len(messages), 4)]

    # Prepare lists to hold parsed date objects and corresponding messages
    dates, full_msgs = [], []
    for chunk in chunks:
        if len(chunk) == 4:
            date_str, time_str, ampm, message = chunk
            timestamp = f"{date_str} {time_str} {ampm}".strip()  # Construct complete timestamp string
            try:
                # Try parsing date with 2-digit year
                date_obj = pd.to_datetime(timestamp, format="%d/%m/%y %I:%M %p")
            except:
                try:
                    # Fallback: try parsing with 4-digit year
                    date_obj = pd.to_datetime(timestamp, format="%d/%m/%Y %I:%M %p")
                except:
                    continue  # Skip if parsing fails
            dates.append(date_obj)
            full_msgs.append(message)

    # Create a DataFrame with the parsed date and user-message text
    df = pd.DataFrame({'date': dates, 'user_message': full_msgs})

    # Split each message into user and actual message text
    users, messages = [], []
    for msg in df['user_message']:
        # Split based on first occurrence of ': ' assuming "User: message"
        parts = re.split(r'([^:]+):\s', msg, maxsplit=1)
        if len(parts) == 3:
            users.append(parts[1])  # Extract user name
            messages.append(parts[2])  # Extract actual message
        else:
            users.append("group_notification")  # System or group notification message
            messages.append(msg)

    # Add user and message columns to the DataFrame
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)  # Remove combined column

    # Extract and add time-based features from the datetime column
    df['only_date'] = df['date'].dt.date  # Only date part
    df['year'] = df['date'].dt.year  # Year
    df['month_num'] = df['date'].dt.month  # Month as number
    df['month'] = df['date'].dt.month_name()  # Month as full name
    df['day'] = df['date'].dt.day  # Day of the month
    df['day_name'] = df['date'].dt.day_name()  # Day of the week
    df['hour'] = df['date'].dt.hour  # Hour of the day
    df['minute'] = df['date'].dt.minute  # Minute of the hour

    # Create time period strings (e.g., "08-09") for hourly heatmap grouping
    df['period'] = df['hour'].apply(lambda h: f"{h:02d}-{(h+1)%24:02d}")

    return df  # Return the cleaned and processed DataFrame
