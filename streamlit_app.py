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

# Load perfume data with encoding fallback

try:
    df = pd.read_csv("final_perfume_data.csv", encoding="utf-8")
except UnicodeDecodeError:
    try:
        df = pd.read_csv("final_perfume_data.csv", encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Failed to load perfume data: {e}")
        st.stop()



# Combine text for searching
df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

# Initialize session state for questionnaire
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

# Step 1 – Mood
if st.session_state.step == 1:
    st.subheader("Step 1: What's your current vibe?")
    mood = st.radio("", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
    if st.button("Next ➡️"):
        st.session_state.answers["mood"] = mood
        st.session_state.step = 2

# Step 2 – Occasion
elif st.session_state.step == 2:
    st.subheader("Step 2: What's the occasion?")
    occasion = st.radio("", ["Everyday Wear", "Date Night", "Work", "Party"])
    if st.button("Next ➡️"):
        st.session_state.answers["occasion"] = occasion
        st.session_state.step = 3

# Step 3 – Notes
elif st.session_state.step == 3:
    st.subheader("Step 3: What kind of notes do you love?")
    notes = st.multiselect("Pick a few that speak to your soul 💫", 
                           ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
    if st.button("Get My Recommendations 💖"):
        st.session_state.answers["notes"] = notes
        st.session_state.step = 4

# Step 4 – Results
elif st.session_state.step == 4:
    st.subheader("💐 Based on your vibe, you might love these:")

    mood = st.session_state.answers["mood"]
    occasion = st.session_state.answers["occasion"]
    notes = st.session_state.answers["notes"]

    # Search using keywords in the combined column
    query_keywords = [mood, occasion] + notes
    query_string = "|".join(query_keywords)

    # Perform the search for matches in the combined column
    results = df[df["combined"].str.contains(query_string, case=False, na=False)]

    if not results.empty:
        for _, row in results.head(5).iterrows():
            st.markdown(f"### **{row['Name']}** by *{row['Brand']}*")
            if pd.notna(row["Image URL"]):
                st.image(row["Image URL"], width=180)
            st.write(row["Description"])
            st.markdown("---")
    else:
        st.error("No perfect match found 😢 Try a different mood or notes!")

    # Log user interaction
    log_data = {
        "username": st.session_state.user,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mood": mood,
        "occasion": occasion,
        "notes": ", ".join(notes),
        "recommendations": ", ".join(results["Name"].head(5)) if not results.empty else "None"
    }
    log_df = pd.DataFrame([log_data])
    log_df.to_csv("users.csv", mode="a", header=not os.path.exists("users.csv"), index=False)

    if st.button("🔄 Start Over"):
        st.session_state.step = 1
        st.session_state.answers = {}
        st.session_state.user = None
        st.session_state.authenticated = False
        save_credentials({"users": []})
        st.experimental_rerun()
