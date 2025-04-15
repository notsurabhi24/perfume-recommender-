import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# File paths
USERS_FILE = 'users.csv'
HISTORY_FILE = 'history.csv'
DATA_FILE = 'final_perfume_data.csv'

# Ensure CSV files exist
for file in [USERS_FILE, HISTORY_FILE]:
    if not os.path.isfile(file):
        pd.DataFrame().to_csv(file, index=False)

# Load perfume dataset
df = pd.read_csv(DATA_FILE, encoding="ISO-8859-1")
df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User registration
def register_user(username, password):
    if os.path.isfile(USERS_FILE):
        users_df = pd.read_csv(USERS_FILE)
        if username in users_df['username'].values:
            return False, "Username already exists."
    else:
        users_df = pd.DataFrame(columns=['username', 'password'])

    hashed_pw = hash_password(password)
    new_user = pd.DataFrame([[username, hashed_pw]], columns=['username', 'password'])
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    return True, "User registered successfully."

# User login
def login_user(username, password):
    if not os.path.isfile(USERS_FILE):
        return False, "No users registered yet."
    users_df = pd.read_csv(USERS_FILE)
    hashed_pw = hash_password(password)
    if username in users_df['username'].values:
        stored_pw = users_df[users_df['username'] == username]['password'].values[0]
        if hashed_pw == stored_pw:
            return True, "Login successful."
        else:
            return False, "Incorrect password."
    else:
        return False, "Username not found."

# Save user history
def save_history(username, mood, occasion, notes, recommendations):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = pd.DataFrame([[username, mood, occasion, ', '.join(notes), ', '.join(recommendations), timestamp]],
                                 columns=['username', 'mood', 'occasion', 'notes', 'recommendations', 'timestamp'])
    if os.path.isfile(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        history_df = pd.concat([history_df, history_entry], ignore_index=True)
    else:
        history_df = history_entry
    history_df.to_csv(HISTORY_FILE, index=False)

# Streamlit app
st.set_page_config(page_title="Perfume Matchmaker", layout="centered")
st.title("🌸 Perfume Personality Matchmaker")

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# Registration and Login
if not st.session_state.logged_in:
    auth_choice = st.selectbox("Choose an option:", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_choice == "Register":
        if st.button("Register"):
            success, message = register_user(username, password)
            if success:
                st.success(message)
            else:
                st.error(message)
    else:
        if st.button("Login"):
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.step = 1
            else:
                st.error(message)
else:
    st.write(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.step = 0
        st.session_state.answers = {}
        st.experimental_rerun()

    # Questionnaire Steps
    if st.session_state.step == 1:
        st.subheader("Step 1: What's your current vibe?")
        mood = st.radio("", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
        if st.button("Next ➡️"):
            st.session_state.answers["mood"] = mood
            st.session_state.step = 2

    elif st.session_state.step == 2:
        st.subheader("Step 2: What's the occasion?")
        occasion = st.radio("", ["Everyday Wear", "Date Night", "Work", "Party"])
        if st.button("Next ➡️"):
            st.session_state.answers["occasion"] = occasion
            st.session_state.step = 3

    elif st.session_state.step == 3:
        st.subheader("Step 3: What kind of notes do you love?")
        notes = st.multiselect("Pick a few that speak to your soul 💫",
                               ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
        if st.button("Get My Recommendations 💖"):
            if notes:
                st.session_state.answers["notes"] = notes
                st.session_state.step = 4
            else:
                st.error("Please select at least one note.")

    elif st.session_state.step == 4:
        st.subheader("💐 Based on your vibe, you might love these:")
        mood = st.session_state.answers["mood"]
        occasion = st.session_state.answers["occasion"]
        notes = st.session_state.answers["notes"]

        # Search using keywords in the combined text
        query_keywords = [mood, occasion] + notes
        query_string = "|".join(query_keywords)

        # Perform the search for matches in the combined column
        results = df[df["combined"].str.contains(query_string, case=False, na=False)]

        if not results.empty:
            recommendations = []
            for _, row in results.head(5).iterrows():
                st.markdown(f"### **{row['Name']}** by *{row['Brand']}*")
                if pd.notna(row["
::contentReference[oaicite:10]{index=10}
 
