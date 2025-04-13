import streamlit as st
from ai_model import PerfumeRecommender

# Load model
model = PerfumeRecommender("final_perfume_data.csv")

st.set_page_config(page_title="Perfume Recommender", layout="centered")
st.title("🌸 AI-Powered Perfume Recommender")

st.markdown("Select your preferences below and discover perfumes tailored to your vibe 💅")

# Dropdowns
char = st.selectbox("💎 What characteristics are you looking for?", sorted(model.df['Characteristics'].dropna().unique()))
fam = st.selectbox("🌼 Choose a Fragrance Family", sorted(model.df['Fragrance Family'].dropna().unique()))
occ = st.selectbox("🎯 When do you plan to wear it?", sorted(model.df['Occasion'].dropna().unique()))

# Recommend button
if st.button("🔮 Find My Perfume"):
    results = model.recommend(char, fam, occ)
    st.subheader("✨ Your Top Picks")
    for _, row in results.iterrows():
        st.markdown(f"**{row['Name']}** by *{row['Brand']}*")
        st.markdown(f"- **Characteristics:** {row['Characteristics']}")
        st.markdown(f"- **Fragrance Family:** {row['Fragrance Family']}")
        st.markdown(f"- **Occasion:** {row['Occasion']}")
        st.markdown("---")
