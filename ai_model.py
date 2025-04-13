import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PerfumeRecommender:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path, encoding='ISO-8859-1')

        self.df.fillna("", inplace=True)
        self.df['Combined'] = (
            self.df['Characteristics'] + " " +
            self.df['Fragrance Family'] + " " +
            self.df['Occasion']
        )
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['Combined'])

    def recommend(self, char, fam, occ, top_n=5):
        input_text = f"{char} {fam} {occ}"
        input_vec = self.vectorizer.transform([input_text])
        sim_scores = cosine_similarity(input_vec, self.tfidf_matrix).flatten()
        top_indices = sim_scores.argsort()[-top_n:][::-1]
        return self.df.iloc[top_indices]
