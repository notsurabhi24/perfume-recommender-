import streamlit as st
import pandas as pd

# Load dataset
df = pd.read_csv("final_perfume_data.csv", encoding="ISO-8859-1")

# Combine text for searching using the correct column names
df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

# Session state init
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# App title
st.set_page_config(page_title="Perfume Matchmaker", layout="centered")
st.title("🌸 Perfume Personality Matchmaker")
st.markdown("Let your vibes choose your scent. Answer a few questions and we'll match you with your signature fragrance!")

# Step 1 – Mood
if st.session_state.step == 1:
    st.subheader("Step 1: What's your current vibe?")
    mood = st.radio("", ["Romantic", "Bold", "Fresh", "Mysterious", "Cozy", "Energetic"])
    if st.button("Next ➡️"):
        st.session_state.answers["mood"] = mood
        st.session_state.step += 1
        st.experimental_rerun()

# Step 2 – Occasion
elif st.session_state.step == 2:
    st.subheader("Step 2: What's the occasion?")
    occasion = st.radio("", ["Everyday Wear", "Date Night", "Work", "Party"])
    if st.button("Next ➡️"):
        st.session_state.answers["occasion"] = occasion
        st.session_state.step += 1
        st.experimental_rerun()

# Step 3 – Notes
elif st.session_state.step == 3:
    st.subheader("Step 3: What kind of notes do you love?")
    notes = st.multiselect("Pick a few that speak to your soul 💫", 
                           ["Vanilla", "Oud", "Citrus", "Floral", "Spicy", "Woody", "Sweet", "Musky"])
    if st.button("Get My Recommendations 💖"):
        st.session_state.answers["notes"] = notes
        st.session_state.step += 1
        st.experimental_rerun()

# Step 4 – Results
elif st.session_state.step == 4:
    st.subheader("💐 Based on your vibe, you might love these:")

    mood = st.session_state.answers["mood"]
    occasion = st.session_state.answers["occasion"]
    notes = st.session_state.answers["notes"]

    # Search using keywords in the combined text
    query_keywords = [mood, occasion] + notes
    query_string = "|".join(query_keywords)

    # Perform the search for matches
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

    if st.button("🔄 Start Over"):
        st.session_state.step = 1
        st.session_state.answers = {}
        st.experimental_rerun()
