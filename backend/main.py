from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uuid
import os
import shutil
import joblib
import numpy as np

# Sklearn tools for training
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Internal utils
from utils.scraper import scrape_multiple_urls
from utils.preprocessing import preprocess_pipeline
from utils.lexicon import label_sentiment_lexicon
from utils.predictor import predict_sentiment, predict_cluster

app = FastAPI(title="Sentiment Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_data"
MODEL_DIR = "models"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================
# Pydantic Models
# ==========================================
class ScrapeRequest(BaseModel):
    urls: str
    max_reviews: int = 50

class SessionRequest(BaseModel):
    session_id: str

class ClusterEvaluateRequest(BaseModel):
    session_id: str
    max_k: int = 10

class ClusterApplyRequest(BaseModel):
    session_id: str
    k: int = 3

class TrainRequest(BaseModel):
    session_id: str
    max_features: int = 1000
    test_size: float = 0.2

class PredictRequest(BaseModel):
    text: str


# ==========================================
# Helper to read/write dataset
# ==========================================
def get_file_path(session_id: str, stage: str = "raw"):
    return os.path.join(TEMP_DIR, f"{session_id}_{stage}.csv")


# ==========================================
# ROUTES
# ==========================================

@app.get("/")
def read_root():
    return {"message": "Welcome to Sentiment Analysis API"}


# 1. INPUT DATA (UPLOAD)
@app.post("/api/data/upload")
async def upload_file(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    file_path = get_file_path(session_id, "raw")
    
    # Read file content into memory first
    content = await file.read()
    
    # Determine file type from filename
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".csv"):
            import io
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            import io
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Format file tidak didukung. Gunakan .csv atau .xlsx")
        
        # Validate required columns
        if "Review" not in df.columns:
            # Try common alternatives
            for col in df.columns:
                if col.lower() in ["review", "ulasan", "text", "teks", "komentar", "comment"]:
                    df = df.rename(columns={col: "Review"})
                    break
        
        if "Review" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Kolom 'Review' tidak ditemukan. Kolom yang tersedia: {list(df.columns)}"
            )
        
        # Save as CSV for consistent processing downstream
        df.to_csv(file_path, index=False)
        
        preview = df.head(5).to_dict(orient="records")
        
        return {
            "session_id": session_id,
            "message": "File berhasil diupload",
            "total_rows": len(df),
            "columns": list(df.columns),
            "preview": preview
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")



# 1. INPUT DATA (SCRAPING)
@app.post("/api/data/scrape")
async def scrape_data(request: ScrapeRequest):
    session_id = str(uuid.uuid4())
    url_list = [u.strip() for u in request.urls.split("\n") if u.strip()]
    
    try:
        df = scrape_multiple_urls(url_list, request.max_reviews)
        df.to_csv(get_file_path(session_id, "raw"), index=False)
        return {"session_id": session_id, "message": "Scraping successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 2.5. CLEANING DATA
@app.post("/api/data/clean")
async def clean_data(request: SessionRequest):
    raw_path = get_file_path(request.session_id, "raw")
    if not os.path.exists(raw_path):
        raise HTTPException(status_code=404, detail="Data mentah tidak ditemukan")
        
    df = pd.read_csv(raw_path)
    
    if "Review" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'Review' tidak ditemukan")
        
    original_len = len(df)
    df = df.dropna(subset=["Review"])
    df = df.drop_duplicates(subset=["Review"])
    df.reset_index(drop=True, inplace=True)
    clean_len = len(df)
    
    clean_path = get_file_path(request.session_id, "clean")
    df.to_csv(clean_path, index=False)
    
    preview = df.head(5).to_dict(orient="records")
    
    return {
        "message": "Cleaning selesai",
        "original_rows": original_len,
        "clean_rows": clean_len,
        "preview": preview
    }


# 3. PREPROCESSING
@app.post("/api/process/preprocess")
async def preprocess_data(request: SessionRequest):
    # Load data
    clean_path = get_file_path(request.session_id, "clean")
    raw_path = get_file_path(request.session_id, "raw")
    
    if os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    elif os.path.exists(raw_path):
        df = pd.read_csv(raw_path)
        # Drop NA and duplicates just in case clean step was skipped
        df = df.dropna(subset=["Review"])
        df = df.drop_duplicates(subset=["Review"])
    else:
        raise HTTPException(status_code=404, detail="Data not found")
    
    if "Review" not in df.columns:
        raise HTTPException(status_code=400, detail="Column 'Review' not found in dataset")
        
    df = df.dropna(subset=["Review"])
    df = df.drop_duplicates(subset=["Review"])
    df["Review"] = df["Review"].fillna("")
    
    # Run pipeline
    df["clean"] = df["Review"].apply(preprocess_pipeline)
    
    # Save to dedicated preprocessed stage (not overwriting the clean/raw data)
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    df.to_csv(preprocessed_path, index=False)
    
    preview = df.head(10).to_dict(orient="records")
    return {"message": "Preprocessing finished", "total_rows": len(df), "preview": preview}


# 3. CLUSTERING EVALUATION
@app.post("/api/cluster/evaluate")
async def evaluate_cluster(request: ClusterEvaluateRequest):
    # Try preprocessed first, then clean, then raw
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")
    
    if os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
    elif os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        raise HTTPException(status_code=404, detail="Data preprocessed tidak ditemukan. Lakukan preprocessing terlebih dahulu.")
        
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ada. Lakukan preprocessing terlebih dahulu.")
    
    # Drop NaN, empty strings, fill remaining NaN with empty string
    df = df.dropna(subset=["clean"])
    df = df[df["clean"].astype(str).str.strip() != ""]
    df["clean"] = df["clean"].fillna("").astype(str)
    df.reset_index(drop=True, inplace=True)
    
    if len(df) < 3:
        raise HTTPException(status_code=400, detail="Data terlalu sedikit untuk clustering (minimal 3 baris valid).")
        
    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(df["clean"])
    
    n_samples = X.shape[0]
    max_k = min(request.max_k, n_samples - 1)
    
    results = []
    for k in range(2, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        
        sil = silhouette_score(X, labels) if len(set(labels)) > 1 else 0
        ch = calinski_harabasz_score(X.toarray(), labels)
        
        results.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": float(sil),
            "calinski": float(ch)
        })
        
    return {"evaluation": results, "max_k": max_k}


# 3.5 DATA INFO
@app.post("/api/data/info")
async def data_info(request: SessionRequest):
    """Return basic stats about the labeled dataset for Training page"""
    labeled_path = get_file_path(request.session_id, "labeled")
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")

    if os.path.exists(labeled_path):
        df = pd.read_csv(labeled_path)
    elif os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
    elif os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"
    missing_label = int(df[label_col].isna().sum()) if label_col in df.columns else 0

    dist = {}
    if label_col in df.columns:
        dist = {int(k): int(v) for k, v in df[label_col].value_counts().to_dict().items()}

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_label": missing_label,
        "label_distribution": dist,
        "columns": list(df.columns)
    }


# 4. CLUSTERING APPLY
@app.post("/api/cluster/apply")
async def apply_cluster(request: ClusterApplyRequest):
    # Try preprocessed first, then clean
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")
    
    if os.path.exists(preprocessed_path):
        df = pd.read_csv(preprocessed_path)
    elif os.path.exists(clean_path):
        df = pd.read_csv(clean_path)
    else:
        raise HTTPException(status_code=404, detail="Data preprocessed tidak ditemukan")
    
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ada. Lakukan preprocessing terlebih dahulu.")

    # Drop NaN, empty strings, ensure string type before TF-IDF
    df = df.dropna(subset=["clean"])
    df = df[df["clean"].astype(str).str.strip() != ""]
    df["clean"] = df["clean"].fillna("").astype(str)
    df.reset_index(drop=True, inplace=True)

    if len(df) < request.k:
        raise HTTPException(status_code=400, detail=f"Data terlalu sedikit ({len(df)} baris) untuk K={request.k} cluster.")

    tfidf = TfidfVectorizer(max_features=1000)
    X = tfidf.fit_transform(df["clean"])
    
    km = KMeans(n_clusters=request.k, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(X)
    
    # Save artifacts
    joblib.dump(km, os.path.join(MODEL_DIR, "kmeans_model.pkl"))
    joblib.dump(tfidf, os.path.join(MODEL_DIR, "tfidf_cluster.pkl"))
    
    df.to_csv(get_file_path(request.session_id, "clustered"), index=False)
    
    dist = df["cluster"].value_counts().to_dict()
    preview = df.head(10).to_dict(orient="records")
    return {"message": "Clustering applied", "distribution": dist, "preview": preview}


# 4.5. CLUSTER TOPIC
@app.post("/api/cluster/topic")
async def cluster_topic(request: SessionRequest):
    clustered_path = get_file_path(request.session_id, "clustered")
    if not os.path.exists(clustered_path):
        raise HTTPException(status_code=404, detail="Clustered data not found")
        
    df = pd.read_csv(clustered_path)
    if "cluster" not in df.columns:
        raise HTTPException(status_code=400, detail="Data is not clustered yet")
    if "clean" not in df.columns:
        raise HTTPException(status_code=400, detail="Kolom 'clean' tidak ditemukan")

    # Sanitize clean column — drop NaN, ensure str type
    df = df.dropna(subset=["clean"])
    df["clean"] = df["clean"].fillna("").astype(str)
    df = df[df["clean"].str.strip() != ""]
    df.reset_index(drop=True, inplace=True)
        
    try:
        tfidf = joblib.load(os.path.join(MODEL_DIR, "tfidf_cluster.pkl"))
    except Exception:
        raise HTTPException(status_code=404, detail="TF-IDF model for clustering not found")
        
    X = tfidf.transform(df["clean"])
    feature_names = np.array(tfidf.get_feature_names_out())
    unique_clusters = sorted(df["cluster"].unique())
    
    topics = {}
    for cluster_id in unique_clusters:
        cluster_data = df[df["cluster"] == cluster_id]
        if cluster_data.empty:
            continue
            
        idx = cluster_data.index
        cluster_vec = X[idx].mean(axis=0).A1
        top_idx = cluster_vec.argsort()[::-1][:10]
        
        top_words = feature_names[top_idx].tolist()
        top_scores = cluster_vec[top_idx].tolist()
        
        topics[int(cluster_id)] = [{"word": w, "score": float(s)} for w, s in zip(top_words, top_scores)]
        
    return {"topics": topics}


# 4.6. INSIGHT
@app.post("/api/insight")
async def get_insight(request: SessionRequest):
    data_path = get_file_path(request.session_id, "labeled")
    if not os.path.exists(data_path):
        data_path = get_file_path(request.session_id, "clustered")
    if not os.path.exists(data_path):
        raise HTTPException(status_code=404, detail="Data not found for insight")
        
    df = pd.read_csv(data_path)
    
    insight = {
        "total_data": len(df),
        "cluster_distribution": {},
        "sentiment_distribution": {},
        "cluster_sentiment_mean": {}
    }
    
    if "cluster" in df.columns:
        insight["total_clusters"] = int(df["cluster"].nunique())
        # Convert keys to int for JSON serialization
        insight["cluster_distribution"] = {int(k): int(v) for k, v in df["cluster"].value_counts().to_dict().items()}
        
    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"
    if label_col in df.columns:
        insight["sentiment_distribution"] = {int(k): int(v) for k, v in df[label_col].value_counts().to_dict().items()}
        
    if "cluster" in df.columns and label_col in df.columns:
        try:
            cluster_sent = df.groupby("cluster")[label_col].mean()
            insight["cluster_sentiment_mean"] = {int(k): float(v) for k, v in cluster_sent.to_dict().items()}
            insight["best_cluster"] = int(cluster_sent.idxmax())
            insight["worst_cluster"] = int(cluster_sent.idxmin())
        except Exception:
            pass
            
    return insight


# 5. SENTIMENT LABELING
@app.post("/api/sentiment/label")
async def label_sentiment(request: SessionRequest):
    # Try reading clustered data → preprocessed → clean (in that order)
    clustered_path = get_file_path(request.session_id, "clustered")
    preprocessed_path = get_file_path(request.session_id, "preprocessed")
    clean_path = get_file_path(request.session_id, "clean")
    
    if os.path.exists(clustered_path):
        data_path = clustered_path
    elif os.path.exists(preprocessed_path):
        data_path = preprocessed_path
    elif os.path.exists(clean_path):
        data_path = clean_path
    else:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan. Lakukan preprocessing terlebih dahulu.")
        
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["clean"])
    
    df = label_sentiment_lexicon(df, text_column="clean")
    df.to_csv(get_file_path(request.session_id, "labeled"), index=False)
    
    dist = df["sentiment_label"].value_counts().to_dict()
    preview = df.head(10).to_dict(orient="records")
    return {"message": "Labeling applied", "distribution": dist, "preview": preview}


# 6. MODEL TRAINING
@app.post("/api/model/train")
async def train_model(request: TrainRequest):
    labeled_path = get_file_path(request.session_id, "labeled")
    if not os.path.exists(labeled_path):
        raise HTTPException(status_code=404, detail="Labeled data not found")
        
    df = pd.read_csv(labeled_path)
    label_col = "sentiment_label" if "sentiment_label" in df.columns else "label"
    df = df.dropna(subset=[label_col, "clean"])
    
    if len(df) < 5:
        raise HTTPException(status_code=400, detail="Not enough data to train")
        
    tfidf = TfidfVectorizer(max_features=request.max_features)
    X = tfidf.fit_transform(df["clean"])
    y = df[label_col]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=request.test_size, random_state=42, stratify=y
    )
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Confusion matrix
    labels_sorted = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)
    cm_list = cm.tolist()

    # Accuracies
    test_acc = float(accuracy_score(y_test, y_pred))
    train_acc = float(rf.score(X_train, y_train))

    # Save artifacts
    joblib.dump(rf, os.path.join(MODEL_DIR, "rf_model.pkl"))
    joblib.dump(tfidf, os.path.join(MODEL_DIR, "tfidf_sentiment.pkl"))

    return {
        "message": "Model trained successfully",
        "classification_report": report,
        "confusion_matrix": cm_list,
        "confusion_matrix_labels": [int(l) for l in labels_sorted],
        "test_accuracy": test_acc,
        "train_accuracy": train_acc
    }


# 7. PREDICTION INFERENCE (single)
@app.post("/api/model/predict")
async def predict_single(request: PredictRequest):
    try:
        clean_text = preprocess_pipeline(request.text)
        sent = predict_sentiment([clean_text])
        clus = predict_cluster([clean_text])
        return {
            "text": request.text,
            "sentiment": int(sent[0]),
            "cluster": int(clus[0])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 8. BATCH PREDICTION (file upload)
@app.post("/api/model/predict_batch")
async def predict_batch(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()
    
    try:
        import io
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Format tidak didukung. Gunakan .csv atau .xlsx")
        
        if "Review" not in df.columns:
            raise HTTPException(status_code=400, detail="File harus memiliki kolom 'Review'")
        
        df = df.dropna(subset=["Review"])
        df["clean"] = df["Review"].apply(preprocess_pipeline)
        
        sentiments = predict_sentiment(df["clean"].tolist())
        clusters = predict_cluster(df["clean"].tolist())
        
        df["sentiment_label"] = [int(s) for s in sentiments]
        df["cluster"] = [int(c) for c in clusters]
        
        label_map = {0: "Negatif", 1: "Netral", 2: "Positif"}
        df["sentimen"] = df["sentiment_label"].map(label_map)
        
        predictions = df[["Review", "clean", "sentiment_label", "sentimen", "cluster"]].head(100).to_dict(orient="records")
        
        return {
            "total": len(df),
            "unique_clusters": int(df["cluster"].nunique()),
            "sentiment_distribution": {int(k): int(v) for k, v in df["sentiment_label"].value_counts().to_dict().items()},
            "predictions": predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses file: {str(e)}")
