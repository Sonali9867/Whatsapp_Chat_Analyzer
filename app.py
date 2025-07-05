import matplotlib.pyplot as plt
import seaborn as sns
import helper
import preprocessor
import base64
from PIL import Image
from io import BytesIO
import streamlit as st
import datetime
import matplotlib

st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="📱")

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

logo = Image.open("whatsapp-logo.png")
logo_base64 = image_to_base64(logo)

st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{logo_base64}" width="53" style="margin-right: 15px;">
        <h1 style="margin: 0; padding: 0; font-size: 50px;">WhatsApp Chat Analyzer</h1>

    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)
st.info("🔒 **Privacy Notice:** Your uploaded chat file is processed locally and never stored. We do not save, share, or access your data beyond this session.")


# Sidebar for file upload
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file")


if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis of", user_list)

    if st.sidebar.button("Show Analysis"):

        report_lines = []
        # Stats
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics 📊")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            st.markdown('<h2 style="font-size:33px;">Total Messages</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:25px; margin:0;'>{num_messages}</p>", unsafe_allow_html=True)

        with col2:
            st.markdown('<h2 style="font-size:33px;">Total Words</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:25px; margin:0;'>{words}</p>", unsafe_allow_html=True)

        with col3:
            st.markdown('<h2 style="font-size:33px;"> Shared Media</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:25px; margin:0;'>{num_media_messages}</p>", unsafe_allow_html=True)

        with col4:
            st.markdown('<h2 style="font-size:33px;">Shared Links</h2>', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:25px; margin:0;'>{num_links}</p>", unsafe_allow_html=True)


        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Number of Messages", fontsize=12)
        st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Number of Messages", fontsize=12)
        st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Activity Map
        st.title('Activity Map')
        col1, spacer, col2 = st.columns([2, 0.5, 2])

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            ax.set_xlabel("Day", fontsize=12)
            ax.set_ylabel("Number of Messages", fontsize=12)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            ax.set_xlabel("Month", fontsize=12)
            ax.set_ylabel("Number of Messages", fontsize=12)
            st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Weekly Activity Heatmap
        st.title("Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.heatmap(user_heatmap, cbar_kws={'label': 'Activity Level'})
        plt.xlabel('Time')
        plt.ylabel('Day')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Busiest Users (only for group chats)
        if selected_user == "Overall":
            st.title('Most Active Users in Chat')
            x, new_df = helper.most_busy_users(df)
            new_df.columns = ['Person', 'Percent']
            col1, spacer, col2 = st.columns([2, 0.5, 2])

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='teal')
                plt.xticks(rotation='vertical')
                ax.set_xlabel("Users", fontsize=12)
                ax.set_ylabel("Number of Messages", fontsize=12)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        st.markdown("<br>", unsafe_allow_html=True)

        # Word Cloud
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis('off')
        st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Most Common Words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df['Word'], most_common_df['Count'], color='skyblue')
        plt.xticks(rotation='vertical')
        ax.set_xlabel("Count", fontsize=12)
        ax.set_ylabel("Words", fontsize=12)
        st.pyplot(fig)

        st.markdown("<br>", unsafe_allow_html=True)

        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, spacer, col2 = st.columns([2, 0.5, 2])

        # Rename columns first
        emoji_df.columns = ['Emoji', 'Count']

        with col1:
            st.dataframe(emoji_df)

        matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'
        matplotlib.rcParams['axes.unicode_minus'] = False

        with col2:
            if not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df['Count'].head(),
                    labels=emoji_df['Emoji'].head(),
                    autopct="%0.2f"
                )
                plt.title('Top 5 Used Emojis', fontsize=14, weight='bold')
                st.pyplot(fig)
            else:
                st.write("No emojis found in this chat.")


        #Generate Report
        report_lines.append("\nEmoji Usage:")
        report_lines.extend(emoji_df.to_string(index=False).split('\n'))

        # Report Download Section
        st.title("Download Report 📄")

        report_text = '\n'.join(report_lines)
        report_bytes = BytesIO()
        report_bytes.write(report_text.encode())
        report_bytes.seek(0)

        st.download_button(
            label="Download Full Report 📥",
            data=report_bytes,
            file_name=f'whatsapp_chat_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mime='text/plain'
        )




