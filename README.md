# StudyPlanner
An app to plan organize and track the study plan to pass the exam within the examination preparation time
Features
1. User Authentication
Signup/Login: Users can create accounts and log in securely using hashed passwords stored in a JSON file.
Prevents unauthorized access and allows personalized study plans for each user.
2. Study Plan Management
Add Subjects and Topics: Users can add subjects, specify the topics to study, and set deadlines.
Generate Study Plan: Automatically creates a daily schedule for each subject based on the deadline and topics provided.
3. Progress Tracker
Update Progress: Users can mark topics as completed.
Progress Visualization: A horizontal bar chart displays the percentage of topics completed vs. remaining for each subject.
4. Data Management
Save Data: Save study plans and progress for future sessions.
Load Data: Load previously saved data upon login.
Clear Data: Option to reset and clear all stored data.
5. Logout Functionality
Users can securely log out, ensuring their data is protected.

Usage
1. Authentication
On launching the app, you'll see options to Login or Signup.
For new users, create an account by entering a username and password.
Existing users can log in to access their personalized study planner.
2. Managing Study Plan
Add subjects and topics via the sidebar form.
Specify deadlines (in days) for each subject.
Generate a study plan by clicking the Generate Study Plan button.
3. Updating Progress
Use the Update Progress form to mark completed topics.
The application automatically tracks and visualizes your progress.
4. Saving and Managing Data
Use the Save Data button in the sidebar to save your current study plan and progress.
To reset all data, use the Clear Data button.
File Structure
app.py: The main Streamlit application.
study_planner_data.json: Stores study plans and progress (auto-generated).
users.json: Stores user credentials (auto-generated).
Dependencies
Streamlit: For building the interactive web app.
Matplotlib: For visualizing study progress.
Bcrypt: For secure password hashing.
JSON: For storing user data and study plans.
Install all dependencies with:
pip install -r requirements.txt
