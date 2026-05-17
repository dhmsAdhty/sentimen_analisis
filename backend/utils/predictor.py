import joblib
import os
import numpy as np

# ============================================================
# LOAD MODEL (SAFE PATH)
# ============================================================

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_PATH, "models")

rf_model = None
tfidf_sent = None
kmeans_model = None
tfidf_cluster = None

try:
    rf_model = joblib.load(os.path.join(MODEL_PATH, "rf_model.pkl"))
    tfidf_sent = joblib.load(os.path.join(MODEL_PATH, "tfidf_sentiment.pkl"))
    kmeans_model = joblib.load(os.path.join(MODEL_PATH, "kmeans_model.pkl"))
    tfidf_cluster = joblib.load(os.path.join(MODEL_PATH, "tfidf_cluster.pkl"))
except Exception as e:
    print("⚠️ Model belum tersedia:", e)


# ============================================================
# PREDICT SENTIMEN
# ============================================================

def predict_sentiment(texts, tfidf=None, model=None):

    if model is None:
        model = rf_model
    if tfidf is None:
        tfidf = tfidf_sent

    if model is None or tfidf is None:
        raise ValueError("Model sentiment belum tersedia")

    X = tfidf.transform(texts)
    return model.predict(X)


# ============================================================
# PREDICT CLUSTER
# ============================================================

def predict_cluster(texts, tfidf=None, model=None):

    if model is None:
        model = kmeans_model
    if tfidf is None:
        tfidf = tfidf_cluster

    if model is None or tfidf is None:
        raise ValueError("Model cluster belum tersedia")

    X = tfidf.transform(texts)
    return model.predict(X)


# ============================================================
# TEST TERMINAL (SAFE)
# ============================================================

if __name__ == "__main__":

    print("✅ Predictor OK")

    sample = ["kampus ini bersih dan nyaman"]

    try:
        print("Sentiment:", predict_sentiment(sample))
        print("Cluster:", predict_cluster(sample))
    except Exception as e:
        print("⚠️ ERROR:", e)