import streamlit as st
import pandas as pd
import yaml
import os
from datetime import datetime
import streamlit_authenticator as stauth

# Load user credentials
def load_credentials():
    if os.path.exists("credentials.yaml"):
        with open("credentials.yaml", "r") as file:
            return yaml.safe_load(file)
    return {"users": []}

# Save user credentials
def save_credentials(credentials):
    with open("credentials.yaml", "w") as file:
        yaml.dump(credentials, file)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# Authentication
if not st.session_state.authenticated:
    credentials = load_credentials()
    usernames = [user["username"] for user in credentials["users"]]
    passwords = [user["password"] for user in credentials["users"]]
    authenticator = stauth.Authenticate(usernames, passwords, "perfume_app", "secret_key", cookie_expiry_days=30)
    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        st.session_state.authenticated = True
        st.session_state.user = username
        st.session_state.step = 1
    elif authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")

# Load perfume data
df = pd.read_csv("final_perfume_data.csv", encoding="ISO-8859-1")
df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

# Questionnaire Steps
if st.session_state.step == 1:
    st.subheader("Step 1: What's your current vibe?")
    mood = st.radio("", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
    if st.button("Next ➡️"):
        st.session_state.answers = {"mood": mood}
        st.session_state.step = 2

elif st.session_state.step == 2:
    st.subheader("Step 2: What's the occasion?")
    occasion = st.radio("", ["Everyday Wear", "Date Night", "Work", "Party"])
    if st.button("Next ➡️"):
        st.session_state.answers["occasion"] = occasion
        st.session_state.step = 3

elif st.session_state.step == 3:
    st.subheader("Step 3: What kind of notes do you love?")
    notes = st.multiselect("Pick a few that speak to your soul 💫", ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
    if st.button("Get My Recommendations 💖"):
        st.session_state.answers["notes"] = notes
        st.session_state.step = 4

elif st.session_state.step == 4:
    st.subheader("💐 Based on your vibe, you might love these:")
    mood = st.session_state.answers["mood"]
    occasion = st.session_state.answers["occasion"]
    notes = st.session_state.answers["notes"]

    query_keywords = [mood, occasion] + notes
    query_string = "|".join(query_keywords)

    results = df[df["combined"].str.contains(query_string, case=False, na=False)]

    if not results.empty:
        for _, row in results.head(5).iterrows():
            st.markdown(f"### **{row['Name']}** by *{row['Brand']}*")
            if pd.notna(row["Image URL"]):
                st.image(row["Image URL"], width=180)
            st.write(row["Description"])
            st.markdown("---")
        # Log user data
        user_data = {
            "username": st.session_state.user,
            "mood": mood,
            "occasion": occasion,
            "notes": ", ".join(notes),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        log_user_data(user_data)
    else:
        st.error("No perfect match found 😢 Try a different mood or notes!")

    if st.button("🔄 Start Over"):
        st.session_state.step = 1
        st.session_state.answers = {}

# Function to log user data
def log_user_data(user_data):
    log_file = "user_data_log.csv"
    if os.path.exists(log_file):
        df_log = pd.read_csv(log_file)
    else:
        df_log = pd.DataFrame(columns=user_data.keys())
    df_log = df_log.append(user_data, ignore_index=True)
    df_log.to_csv(log_file, index=False)

# Registration
if not st.session_state.authenticated:
    st.subheader("New User? Register Here")
    with st.form("registration_form"):
        new_username = st.text_input("Choose a username")
        new_password = st.text_input("Choose a password", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            credentials = load_credentials()
            if any(user["username"] == new_username for user in credentials["users"]):
                st.error("Username already exists")
            else:
                credentials["users"].append({"username": new_username, "password": new_password})
                save_credentials(credentials)
                st.success("Registration successful. Please log in.")
