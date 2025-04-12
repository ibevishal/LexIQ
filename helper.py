# Import required libraries
from urlextract import URLExtract  # Used to extract URLs from text
from wordcloud import WordCloud  # Used to generate word clouds
import pandas as pd  # For data manipulation
from collections import Counter  # To count frequency of items
import emoji  # To detect and extract emojis
import re  # For regular expressions

# Create an instance of URL extractor
extract = URLExtract()

# Function to calculate basic stats
def fetch_stats(selected_user, df):
    # Filter data for selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Total number of messages
    num_messages = df.shape[0]

    # Total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Count media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Extract and count links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    # Return all stats
    return num_messages, len(words), num_media_messages, len(links)


# Function to get most active users in group chat
def most_busy_users(df):
    top_users = df['user'].value_counts().head()  # Top 5 users by message count
    percent_df = round((df['user'].value_counts(normalize=True) * 100), 2).reset_index()
    percent_df.columns = ['name', 'percent']  # Rename columns
    return top_users, percent_df


# Function to generate word cloud after removing stop words
def create_wordcloud(selected_user, df):
    # Load stop words list
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()

    # Filter by user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications and media messages
    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    # Function to remove stop words from messages
    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])

    # Apply cleaning function to all messages
    temp['cleaned_message'] = temp['message'].apply(remove_stop_words)

    # Generate and return word cloud
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['cleaned_message'].str.cat(sep=" "))
    return df_wc


# Function to get most common words in chat
def most_common_words(selected_user, df):
    import string  # Used for punctuation handling

    # Load stop words
    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().splitlines())

    # Filter by user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications and media messages
    df = df[(df['user'] != 'group_notification') & (~df['message'].str.lower().str.contains('media omitted'))]

    words = []

    for message in df['message']:
        # Clean message by removing punctuation and converting to lowercase
        message = re.sub(r'[^\w\s]', '', message)
        message = message.lower()

        # Tokenize and remove stop words
        for word in message.split():
            word = word.strip(string.punctuation)
            if word and word not in stop_words and len(word) > 1:
                words.append(word)

    # Return an empty DataFrame if no words found
    if not words:
        return pd.DataFrame(columns=['word', 'count'])

    # Return top 20 most common words as DataFrame
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])
    return most_common_df


# Function to analyze emoji usage
def emoji_helper(selected_user, df):
    # Filter by user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        # Extract emoji characters from messages
        emojis.extend([char for char in message if char in emoji.EMOJI_DATA])

    # Create DataFrame with emoji counts
    emoji_df = pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])
    return emoji_df


# Function to create monthly timeline of messages
def monthly_timeline(selected_user, df):
    # Filter by user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group by year, month number, and month name, then count messages
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    # Create a 'time' column in format "Month-Year"
    timeline['time'] = timeline.apply(lambda row: f"{row['month']}-{row['year']}", axis=1)
    return timeline


# Function to create daily timeline of messages
def daily_timeline(selected_user, df):
    # Filter by user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group by date and count messages
    daily = df.groupby('only_date').count()['message'].reset_index()
    return daily


# Function to get most active days of the week
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


# Function to get most active months
def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


# Function to generate heatmap data (days vs. time periods)
def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Pivot table for heatmap: rows=days, columns=hourly periods, values=message count
    heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return heatmap

def hourly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['hour'].value_counts().sort_index()
