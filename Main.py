import streamlit as st
import smtplib
import random
import json
import bcrypt
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File paths
USER_DATA_FILE = "all_users.json"  # User credentials file

# Function to load user data (stored usernames, emails, and hashed passwords)
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save user data
def save_user_data(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)
    st.success("User  data saved successfully!")

# Function to send OTP to email
def send_otp(email):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    sender_email = "aizen3006sosuke@gmail.com"  
    sender_app_password = "hxckrevoadruwagr"  
    smtp_server = "smtp.gmail.com"
    port = 587

    try:
        # Create the email message
        message = f"Subject: Your OTP\n\nYour OTP is {otp}. It will expire in 5 minutes."
        
        # Send the email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Upgrade connection to secure
        server.login(sender_email, sender_app_password)  # Use App Password for login
        server.sendmail(sender_email, email, message)
        server.quit()
        return otp
    except Exception as e:
        st.error(f"Error sending OTP: {e}")
        return None

# Function to send reminder email
def send_reminder_email(email, subject):
    sender_email = "aizen3006sosuke@gmail.com"  
    sender_app_password = "hxckrevoadruwagr"  
    smtp_server = "smtp.gmail.com"
    port = 587

    try:
        # Create the reminder email message
        message = f"Subject: Reminder for {subject}\n\nThis is a reminder that you have not completed the topic for {subject} by the deadline."
        
        # Send the email
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Upgrade connection to secure
        server.login(sender_email, sender_app_password)  # Use App Password for login
        server.sendmail(sender_email, email, message)
        server.quit()
        st.success(f"Reminder email sent to {email} for {subject}.")
    except Exception as e:
        st.error(f"Error sending reminder email: {e}")

# Function to check for deadlines and send reminders
def check_deadlines_and_send_reminders(users):
    today = datetime.now().date()
    for username, data in users.items():
        email = data['email']
        subjects = data.get('subjects', {})
        for subject, details in subjects.items():
            deadline = details['deadline']
            completed_topics = st.session_state.user_data["progress"].get(subject, 0)
            total_topics = len(details['topics'])
            if today > (datetime.now() + timedelta(days=deadline)).date() and completed_topics < total_topics:
                send_reminder_email(email, subject)

# Function to create a new user account
def signup():
    st.title("Signup")
    username = st.text_input("Enter username:")
    email = st.text_input("Enter email:")
    password = st.text_input("Enter password:", type="password")
    otp_sent = st.button("Send OTP")

    if otp_sent:
        if username and email and password:
            otp = send_otp(email)
            if otp:
                st.session_state.otp = otp
                st.session_state.email = email
                st.info("OTP sent to your email. Please verify it below.")
        else:
            st.warning("Please fill all the fields before sending OTP.")

    # OTP Verification and Account Creation
    otp_entered = st.text_input("Enter OTP:")
    if st.button("Verify and Create Account"):
        if otp_entered and st.session_state.get("otp") == int(otp_entered):
            users = load_user_data()
            if username in users or any(u['email'] == email for u in users.values()):
                st.warning("Username or email already exists. Please choose another.")
            else:
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                users[username] = {"email": email, "password": hashed_pw.decode('utf-8'), "subjects": {}}
                save_user_data(users)
                st.success("Account created successfully! You can now log in.")
                st.session_state.otp = None  # Clear OTP after successful signup
        else:
            st.error("Invalid OTP. Please try again.")

# Function to handle user login
def login():
    st.title("Login")
    identifier = st.text_input("Enter username or email:")
    password = st.text_input("Enter password:", type="password")

    if st.button("Login"):
        if identifier and password:
            users = load_user_data()
            # Find user by username or email
            user = next((u for u, data in users.items() if u == identifier or data["email"] == identifier), None)
            if user:
                stored_hashed_pw = users[user]["password"].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_pw):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.user_data = load_user_specific_data(user)  # Load user-specific data
                    st.success(f"Welcome, {user}!")
                    check_deadlines_and_send_reminders(users)  # Check deadlines and send reminders
                else:
                    st.warning("Incorrect password. Please try again.")
            else:
                st.warning("Username or email not found. Please sign up first.")
        else:
            st.warning("Please enter both an identifier and a password.")

# Function to handle password reset
def reset_password():
    st.title("Reset Password")
    email = st.text_input("Enter your registered email:")
    otp_sent = st.button("Send OTP")

    if otp_sent:
        if email:
            users = load_user_data()
            if any(data['email'] == email for data in users.values()):
                otp = send_otp(email)
                if otp:
                    st.session_state.reset_otp = otp
                    st.session_state.reset_email = email
                    st.info("OTP sent to your email. Please verify it below.")
            else:
                st.warning("Email not found. Please check and try again.")
        else:
            st.warning("Please enter your email before sending OTP.")

    # OTP Verification and Password Reset
    otp_entered = st.text_input("Enter OTP for password reset:")
    new_password = st.text_input("Enter new password:", type="password")
    if st.button("Verify OTP and Reset Password"):
        if otp_entered and st.session_state.get("reset_otp") == int(otp_entered):
            users = load_user_data()
            for username, data in users.items():
                if data['email'] == st.session_state.reset_email:
                    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    users[username]['password'] = hashed_pw.decode('utf-8')
                    save_user_data(users)
                    st.success("Password reset successfully! You can now log in.")
                    st.session_state.reset_otp = None  # Clear OTP after successful reset
                    break
        else:
            st.error("Invalid OTP. Please try again.")

# Function to load user-specific data
def load_user_specific_data(username):
    try:
        with open(f"{username}_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"subjects": {}, "study_plan": [], "progress": {}}

# Function to save user-specific data
def save_user_specific_data(username, data):
    with open(f"{username}_data.json", "w") as f:
        json.dump(data, f)
    st.success("User -specific data saved successfully!")

# Function to check if the user is logged in
def check_login():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        return False
    return True

# Study planner functionality
def generate_schedule(subjects):
    study_plan = []
    today = datetime.now()
    
    for subject, details in subjects.items():
        days = details['deadline']
        topics = details['topics']
        num_topics = len(topics)
        per_day_topics = num_topics // days
        remaining_topics = num_topics % days
        
        start_date = today
        topic_index = 0
        
        for i in range(days):
            end_date = start_date + timedelta(days=1)
            
            # Calculate topics for this day
            if i < remaining_topics:
                topics_for_day = topics[topic_index:topic_index + per_day_topics + 1]
                topic_index += per_day_topics + 1
            else:
                topics_for_day = topics[topic_index:topic_index + per_day_topics]
                topic_index += per_day_topics
            
            study_plan.append({
                "date": start_date.strftime("%Y-%m-%d"),
                "subject": subject,
                "topics": topics_for_day
            })
            start_date = end_date

    return study_plan

# Function to track progress and plot visualization
def track_progress(progress, subjects):
    st.subheader("Progress Tracker")
    
    completed_data = []
    remaining_data = []
    subject_names = []

    for subject, completed in progress.items():
        total_topics = len(subjects[subject]['topics'])
        completed_percentage = (completed / total_topics) * 100
        remaining_percentage = 100 - completed_percentage

        completed_data.append(completed_percentage)
        remaining_data.append(remaining_percentage)
        subject_names.append(subject)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(subject_names, completed_data, color='green', label='Completed')
    ax.barh(subject_names, remaining_data, left=completed_data, color='lightgray', label='Remaining')

    ax.set_xlabel("Progress (%)")
    ax.set_title("Study Progress by Subject")

    for i, subject in enumerate(subject_names):
        completed_topics = [t for i, t in enumerate(subjects[subject]['topics']) if i < progress[subject]]
        ax.text(completed_data[i] + 2, i, ', '.join(completed_topics), va='center', color='black', fontsize=9)

    ax.legend()
    st.pyplot(fig)

# Main function to run the app
def main():
    # Custom CSS for responsiveness
    st.markdown(
        """
        <style>
        @media (max-width: 600px) {
            .streamlit-expanderHeader {
                font-size: 16px;
            }
            .stButton>button {
                width: 100%;
            }
            .stTextInput>div>input {
                width: 100%;
            }
            .stTextArea>div>textarea {
                width: 100%;
            }
            .stSelectbox>div>select {
                width: 100%;
            }
            .stRadio>div>label {
                font-size: 14px;
            }
            .stMarkdown {
                font-size: 14px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if not check_login():
        # Show login or signup options if the user is not logged in
        st.title("Welcome to the Study Planner")
        option = st.radio("Choose an option", ("Login", "Signup", "Forgot Password"))
        
        if option == "Login":
            login()
        elif option == "Signup":
            signup()
        elif option == "Forgot Password":
            reset_password()
    else:
        # Once logged in, show the main app content
        st.title(f"Welcome to the Study Planner, {st.session_state.username}!")

        # Load existing user-specific data
        if "user_data" not in st.session_state:
            st.session_state.user_data = load_user_specific_data(st.session_state.username)

        # Input subjects and topics
        st.header("Add Subjects and Topics")
        subject = st.text_input("Enter subject name:")
        topics = st.text_area("Enter topics (comma-separated):")
        deadline = st.number_input("Enter deadline (in days):", min_value=1, step=1)
        add_subject = st.button("Add Subject")
        
        if add_subject and subject and topics and deadline:
            st.session_state.user_data["subjects"][subject] = {"topics": topics.split(','), "deadline": int(deadline)}
            if subject not in st.session_state.user_data["progress"]:
                st.session_state.user_data["progress"][subject] = 0
            st.success(f"Added {subject}!")

        st.write("Current Subjects:")
        st.json(st.session_state.user_data["subjects"])

        # Generate study plan
        if st.button("Generate Study Plan"):
            if st.session_state.user_data["subjects"]:
                st.session_state.user_data["study_plan"] = generate_schedule(st.session_state.user_data["subjects"])
                st.success("Study plan generated!")
            else:
                st.error("Add subjects first!")

        # Display study plan
        if "study_plan" in st.session_state.user_data:
            st.subheader("Your Study Plan")
            for entry in st.session_state.user_data["study_plan"]:
                st.write(f"Date: {entry['date']} | Subject: {entry['subject']} | Topics: {', '.join(entry['topics'])}")

        # Update progress
        st.subheader("Update Progress")
        subject = st.selectbox("Select subject:", list(st.session_state.user_data["subjects"].keys()))
        
        # Dropdown for topics
        topic_options = st.session_state.user_data["subjects"][subject]['topics'] if subject in st.session_state.user_data["subjects"] else []
        topic = st.selectbox("Select completed topic:", topic_options)
        
        update_progress = st.button("Update Progress")
        
        if update_progress:
            topics_normalized = [t.strip().lower() for t in st.session_state.user_data["subjects"][subject]['topics']]
            topic_normalized = topic.strip().lower()
            
            if topic_normalized in topics_normalized:
                current_progress = st.session_state.user_data["progress"][subject]
                total_topics = len(st.session_state.user_data["subjects"][subject]['topics'])
                
                if current_progress < total_topics:
                    topic_index = topics_normalized.index(topic_normalized)
                    if current_progress <= topic_index:
                        st.session_state.user_data["progress"][subject] += 1
                        st.success(f"Marked '{topic.strip()}' as completed for {subject}!")
                    else:
                        st.warning(f"'{topic.strip()}' has already been marked as completed for {subject}!")
                else:
                    st.warning(f"Progress for {subject} is already at 100%!")
            else:
                st.error("Invalid topic. Make sure you selected it correctly.")

        if "progress" in st.session_state.user_data:
            track_progress(st.session_state.user_data["progress"], st.session_state.user_data["subjects"])

        # Save and Clear Options
        st.subheader("Save and Manage Data")
        if st.button("Save Data"):
            save_user_specific_data(st.session_state.username, st.session_state.user_data)
        
        if st.button("Clear Data"):
            st.session_state.user_data = {"subjects": {}, "study_plan": [], "progress": {}}

        # Logout option
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_data = {}
            st.success("You have been logged out.")

# Run the app
if __name__ == "__main__":
    main()