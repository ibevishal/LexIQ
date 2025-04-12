# Import necessary libraries
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import io
import streamlit.components.v1 as components

# Apply custom CSS and animations
st.markdown("""
    <style>
        .css-1d391kg { padding-top: 2rem; }
        .animated-title {
            animation: fadeIn 2s ease-in-out;
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 1.8rem;
            margin-top: 2rem;
            color: #1f77b4;
            animation: slideIn 1s ease-in-out;
        }
        .stHeader { color: #ff5722; }
        .stSubheader { color: #607d8b; }
        @keyframes fadeIn {
            0% { opacity: 0; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar title
st.sidebar.title("WhatsApp Chat Analyzer")
st.sidebar.markdown("by **@ibe.vishal**")

# File uploader in the sidebar (accepts .txt or .zip files)
uploaded_file = st.sidebar.file_uploader("📂 Choose a WhatsApp chat (.txt or .zip)", type=["txt", "zip"])

# Function to extract .txt file content from a zip file
def extract_txt_from_zip(zip_file):
    with zipfile.ZipFile(zip_file) as z:
        for file_name in z.namelist():  # Loop through all files in the zip
            if file_name.endswith('.txt'):  # Check if the file is a .txt file
                with z.open(file_name) as f:
                    return f.read().decode("utf-8")  # Return decoded text content
    return None  # If no .txt file is found

# If a file is uploaded
if uploaded_file is not None:
    # Handle .txt file directly
    if uploaded_file.name.endswith('.txt'):
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
    # Handle .zip file and extract text
    elif uploaded_file.name.endswith('.zip'):
        data = extract_txt_from_zip(uploaded_file)
        if data is None:
            st.error("❌ No .txt file found inside the ZIP archive.")
            st.stop()
    else:
        st.error("Unsupported file type.")
        st.stop()

    # Preprocess the raw chat data
    df = preprocessor.preprocess(data)

    # Get list of unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')  # Remove system messages
    user_list.sort()
    user_list.insert(0, "Overall")  # Add 'Overall' option for group-level analysis

    # Dropdown to select user for analysis
    selected_user = st.sidebar.selectbox("👤 Show analysis with respect to user list", user_list)

    # When 'Show Analysis' button is clicked
    if st.sidebar.button("🚀 Show Analysis"):

        # Title with animation
        st.markdown('<div class="animated-title"> WhatsApp Chat Analysis</div>', unsafe_allow_html=True)

        # Top statistics section
        st.markdown('<div class="section-title"> Top Statistics</div>', unsafe_allow_html=True)
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        # Display stats in four columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Messages")
            st.markdown(f"<h3 style='margin-top: -42px;'>{num_messages}</h3>", unsafe_allow_html=True)
        with col2:
            st.header("Words")
            st.subheader(words)
        with col3:
            st.header("Media")
            st.subheader(num_media_messages)
        with col4:
            st.header("Links")
            st.subheader(num_links)

        # Monthly timeline chart
        st.markdown('<div class="section-title">🗓️ Monthly Timeline</div>', unsafe_allow_html=True)
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(timeline['time'], timeline['message'], color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily timeline chart
        st.markdown('<div class="section-title">📅 Daily Timeline</div>', unsafe_allow_html=True)
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='blue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity map section
        st.markdown('<div class="section-title">🧭 Activity Map</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        # Busy Day Bar Chart
        with col1:
            st.header("Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Busy Month Bar Chart
        with col2:
            st.header("Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly heatmap of activity
        st.markdown('<div class="section-title">📊 Weekly Activity Heatmap</div>', unsafe_allow_html=True)
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax = sns.heatmap(user_heatmap, cmap="YlGnBu")
        st.pyplot(fig)
        
        # Daily time-wise analysis
        st.markdown('<div class="section-title">⏰ Hourly Activity Trend</div>', unsafe_allow_html=True)
        hourly_activity = helper.hourly_activity_map(selected_user, df)
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.plot(hourly_activity.index, hourly_activity.values, marker='o', color='teal')
        ax.set_xticks(range(0, 24))
        ax.set_xlabel("Hour")
        ax.set_ylabel("Messages")
        ax.set_title("Message per Hour")
        st.pyplot(fig)


        # Busiest users chart - only for group chats
        if selected_user == "Overall":
            st.markdown('<div class="section-title">👥 Most Active Users</div>', unsafe_allow_html=True)
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='pink')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)  # Show data in table format

        # Word cloud visualization
        st.markdown('<div class="section-title">☁️ Word Cloud</div>', unsafe_allow_html=True)
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)  # Display the word cloud image
        ax.axis("off")  # Hide axes
        st.pyplot(fig)

        # Most common words bar chart
        st.markdown('<div class="section-title">💬 Most Common Words</div>', unsafe_allow_html=True)
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'], color='skyblue')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Emoji usage analysis
        st.markdown('<div class="section-title">😀 Emoji Analysis</div>', unsafe_allow_html=True)
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)  # Show emoji data in table

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.1f%%")
                st.pyplot(fig)
            else:
                st.write("No emojis found.")  # Handle case with no emojis
