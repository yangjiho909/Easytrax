# predict_and_visualizer.py

import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def find_similar_cases(user_input, top_k=10):
    with open("model/case_index.pkl", "rb") as f:
        case_data = pickle.load(f)

    with open("model/tfidf_vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    input_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(input_vec, case_data["tfidf_matrix"]).flatten()
    top_indices = similarities.argsort()[::-1][:top_k]

    top_cases = []
    for idx in top_indices:
        case = case_data["cases"][idx]
        case["유사도"] = round(float(similarities[idx]), 3)
        top_cases.append(case)

    return pd.DataFrame(top_cases)

