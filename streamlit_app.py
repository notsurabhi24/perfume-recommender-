import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# ---------- Utils ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.csv") and os.path.getsize("users.csv") > 0:
        return pd.read_csv("users.csv")
    return pd.DataFrame(columns=["username", "password"])

def save_user(username, password):
    users = load_users()
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)

def check_credentials(username, password):
    users = load_users()
    hashed = hash_password(password)
    return ((users["username"] == username) & (users["password"] == hashed)).any()

def load_perfume_data():
    if not os.path.exists("final_perfume_data.csv"):
        return pd.DataFrame()
    try:
        return pd.read_csv("final_perfume_data.csv", encoding="utf-8", errors="ignore")
    except:
        return pd.DataFrame()

def save_history(entry):
    columns = ["username", "timestamp", "mood", "occasion", "notes", "recommendations"]
    if os.path.exists("history.csv") and os.path.getsize("history.csv") > 0:
        history = pd.read_csv("history.csv")
    else:
        history = pd.DataFrame(columns=columns)
    history = pd.concat([history, pd.DataFrame([entry])], ignore_index=True)
    history.to_csv("history.csv", index=False)

# ---------- Init session ----------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "step" not in st.session_state:
    st.session_state.step = 0
if "data" not in st.session_state:
    st.session_state.data = load_perfume_data()
if "answers" not in st.session_state:
    st.session_state.answers = {}

# ---------- Auth ----------
st.title("💐 Perfume Matchmaker")

if not st.session_state.auth:
    mode = st.radio("Choose", ["Login", "Register"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button(mode):
        if u and p:
            if mode == "Register":
                if u in load_users()["username"].values:
                    st.error("Username taken.")
                else:
                    save_user(u, p)
                    st.success("Registered! Login now.")
            else:
                if check_credentials(u, p):
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.session_state.step = 1
                else:
                    st.error("Invalid login.")
        else:
            st.warning("Fill in both fields.")

# ---------- App ----------
elif st.session_state.auth:
    df = st.session_state.data

    if df.empty:
        st.error("Perfume data not found or failed to load.")
        st.stop()

    df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

    if st.session_state.step == 1:
        mood = st.radio("Your mood", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
        if st.button("Next"):
            st.session_state.answers["mood"] = mood
            st.session_state.step = 2

    elif st.session_state.step == 2:
        occasion = st.radio("Occasion", ["Everyday Wear", "Date Night", "Work", "Party"])
        if st.button("Next"):
            st.session_state.answers["occasion"] = occasion
            st.session_state.step = 3

    elif st.session_state.step == 3:
        notes = st.multiselect("Choose notes", ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
        if st.button("Get Results"):
            st.session_state.answers["notes"] = notes
            st.session_state.step = 4

    elif st.session_state.step == 4:
        mood = st.session_state.answers["mood"]
        occasion = st.session_state.answers["occasion"]
        notes = st.session_state.answers["notes"]

        query = "|".join([mood, occasion] + notes)
        res = df[df["combined"].str.contains(query, case=False, na=False)]

        if not res.empty:
            for _, r in res.head(5).iterrows():
                st.markdown(f"### **{r['Name']}** by *{r['Brand']}*")
                if pd.notna(r["Image URL"]):
                    st.image(r["Image URL"], width=150)
                st.write(r["Description"])
                st.markdown("---")
        else:
            st.warning("No results found. Try different notes.")

        save_history({
            "username": st.session_state.user,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mood": mood,
            "occasion": occasion,
            "notes": ", ".join(notes),
            "recommendations": ", ".join(res["Name"].head(5)) if not res.empty else "None"
        })

        if st.button("Start Over"):
            st.session_state.step = 1
            st.session_state.answers = {}
