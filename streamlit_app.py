import streamlit as st
import pandas as pd
import yaml
import os
from datetime import datetime
import streamlit_authenticator as stauth

# --- USER AUTH ---

def load_credentials():
    if os.path.exists("credentials.yaml"):
        with open("credentials.yaml", "r") as file:
            return yaml.safe_load(file)
    return {"users": []}

def save_credentials(credentials):
    with open("credentials.yaml", "w") as file:
        yaml.dump(credentials, file)

# --- SESSION STATE SETUP ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION ---
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

# --- LOAD PERFUME DATA SAFELY ---
if st.session_state.authenticated:
    try:
        # Try reading the file using UTF-8 and fallback to ISO-8859-1
        try:
            df = pd.read_csv("final_perfume_data.csv", encoding="utf-8")
        except:
            df = pd.read_csv("final_perfume_data.csv", encoding="ISO-8859-1")
    except Exception as e:
        st.error("Error loading perfume data. Please check the CSV file.")
        st.stop()

    df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

    if "step" not in st.session_state:
        st.session_state.step = 1
    if "answers" not in st.session_state:
        st.session_state.answers = {}

    # --- STEP 1 ---
    if st.session_state.step == 1:
        st.subheader("Step 1: What's your current vibe?")
        mood = st.radio("", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
        if st.button("Next ➡️"):
            st.session_state.answers["mood"] = mood
            st.session_state.step = 2

    # --- STEP 2 ---
    elif st.session_state.step == 2:
        st.subheader("Step 2: What's the occasion?")
        occasion = st.radio("", ["Everyday Wear", "Date Night", "Work", "Party"])
        if st.button("Next ➡️"):
            st.session_state.answers["occasion"] = occasion
            st.session_state.step = 3

    # --- STEP 3 ---
    elif st.session_state.step == 3:
        st.subheader("Step 3: What kind of notes do you love?")
        notes = st.multiselect("Pick a few that speak to your soul 💫",
                               ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
        if st.button("Get My Recommendations 💖"):
            st.session_state.answers["notes"] = notes
            st.session_state.step = 4

    # --- STEP 4: RESULTS ---
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
        else:
            st.error("No perfect match found 😢 Try a different mood or notes!")

        # --- LOG INTERACTION ---
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
