import pickle
import os

# ============================================================
# LOAD MODEL DARI FOLDER models/
# ============================================================

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_PATH, "models")


def load_models():
    """
    Load semua model:
    - Random Forest (sentimen)
    - TF-IDF sentimen
    - KMeans (cluster)
    - TF-IDF cluster
    """

    try:
        # ==============================
        # SENTIMENT MODEL
        # ==============================
        with open(os.path.join(MODEL_PATH, "rf_model.pkl"), "rb") as f:
            rf_model = pickle.load(f)

        with open(os.path.join(MODEL_PATH, "tfidf_sentiment.pkl"), "rb") as f:
            tfidf_sent = pickle.load(f)

        # ==============================
        # CLUSTER MODEL
        # ==============================
        with open(os.path.join(MODEL_PATH, "kmeans_model.pkl"), "rb") as f:
            kmeans_model = pickle.load(f)

        with open(os.path.join(MODEL_PATH, "tfidf_cluster.pkl"), "rb") as f:
            tfidf_cluster = pickle.load(f)

        return rf_model, tfidf_sent, kmeans_model, tfidf_cluster

    except Exception as e:
        raise ValueError(f"Gagal load model: {e}")