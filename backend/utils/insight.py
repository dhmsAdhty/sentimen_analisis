import pandas as pd


# ============================================================
# HITUNG DISTRIBUSI SENTIMEN
# ============================================================

def get_sentiment_summary(df):
    return df['sentimen'].value_counts()


# ============================================================
# SENTIMEN DOMINAN
# ============================================================

def get_dominant_sentiment(df):
    counts = df['sentimen'].value_counts()
    return counts.idxmax()


# ============================================================
# SENTIMEN PER CLUSTER
# ============================================================

def get_sentiment_per_cluster(df):
    return pd.crosstab(df['cluster_label'], df['sentimen'])


# ============================================================
# CLUSTER PALING POSITIF
# ============================================================

def get_most_positive_cluster(df):

    table = pd.crosstab(df['cluster_label'], df['sentimen'])

    if 'positif' not in table.columns:
        return None

    return table['positif'].idxmax()


# ============================================================
# CLUSTER PALING NEGATIF
# ============================================================

def get_most_negative_cluster(df):

    table = pd.crosstab(df['cluster_label'], df['sentimen'])

    if 'negatif' not in table.columns:
        return None

    return table['negatif'].idxmax()


# ============================================================
# AUTO KESIMPULAN PER CLUSTER
# ============================================================

def generate_cluster_insight(df):
    """
    Output:
    {
        'Fasilitas Kampus': "Mayoritas positif...",
        ...
    }
    """

    insights = {}

    table = pd.crosstab(df['cluster_label'], df['sentimen'])

    for cluster in table.index:

        row = table.loc[cluster]

        total = row.sum()

        pos = row.get('positif', 0)
        neg = row.get('negatif', 0)
        net = row.get('netral', 0)

        # hitung proporsi
        pos_pct = pos / total if total > 0 else 0
        neg_pct = neg / total if total > 0 else 0

        # buat kalimat insight
        if pos_pct > 0.6:
            insights[cluster] = f"Mayoritas review pada {cluster} bersifat positif."
        elif neg_pct > 0.4:
            insights[cluster] = f"Banyak keluhan ditemukan pada {cluster}."
        else:
            insights[cluster] = f"Review pada {cluster} cenderung beragam (netral)."

    return insights


# ============================================================
# RINGKASAN GLOBAL
# ============================================================

def generate_global_insight(df):

    total = len(df)
    dominant = get_dominant_sentiment(df)
    most_pos = get_most_positive_cluster(df)
    most_neg = get_most_negative_cluster(df)

    insight = {
        "total_data": total,
        "sentimen_dominan": dominant,
        "cluster_terbaik": most_pos,
        "cluster_terburuk": most_neg
    }

    return insight