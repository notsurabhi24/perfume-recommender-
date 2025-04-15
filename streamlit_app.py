import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
df = pd.read_csv("final_perfume_data.csv", encoding="ISO-8859-1")

# Combine text fields for NLP
df["combined"] = df["Description"].fillna("") + " " + df["Notes"].fillna("")

# Vectorize text using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df["combined"])

# Streamlit UI
st.set_page_config(page_title="Perfume Recommender", layout="centered")
st.title("🌸 Perfume Recommender")
st.markdown("Enter a perfume name below and discover similar scents!")

user_input = st.text_input("Type a perfume name:")

if user_input:
    matches = df[df["Name"].str.contains(user_input, case=False, na=False)]

    if not matches.empty:
        index = matches.index[0]
        similarities = cosine_similarity(tfidf_matrix[index], tfidf_matrix).flatten()
        similar_indices = similarities.argsort()[-6:][::-1]

        st.subheader("✨ You might also like:")
        for i in similar_indices:
            if i == index:
                continue
            perfume = df.iloc[i]
            st.markdown(f"**{perfume['Name']}** by *{perfume['Brand']}*")
            if pd.notna(perfume["Image URL"]):
                st.image(perfume["Image URL"], width=150)
            st.write(perfume["Description"])
            st.markdown("---")
    else:
        st.error("Perfume not found 😢 Try a different name.")
