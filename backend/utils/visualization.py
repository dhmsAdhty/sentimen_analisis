import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# BAR CHART - JUMLAH DATA PER CLUSTER
# ============================================================

def plot_cluster_distribution(df):
    data = df['cluster_label'].value_counts()

    fig, ax = plt.subplots()
    ax.bar(data.index, data.values)

    ax.set_title("Distribusi Data per Cluster")
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Jumlah")

    return fig


# ============================================================
# BAR CHART - DISTRIBUSI SENTIMEN
# ============================================================

def plot_sentiment_distribution(df):
    data = df['sentimen'].value_counts()

    fig, ax = plt.subplots()
    ax.bar(data.index, data.values)

    ax.set_title("Distribusi Sentimen")
    ax.set_xlabel("Sentimen")
    ax.set_ylabel("Jumlah")

    return fig


# ============================================================
# PIE CHART - SENTIMEN KESELURUHAN
# ============================================================

def plot_sentiment_pie(df):
    data = df['sentimen'].value_counts()

    fig, ax = plt.subplots()
    ax.pie(data.values, labels=data.index, autopct='%1.1f%%')

    ax.set_title("Persentase Sentimen")

    return fig


# ============================================================
# PIE CHART - PER CLUSTER
# ============================================================

def plot_sentiment_per_cluster(df):
    """
    Output:
    dict cluster -> fig
    """

    figs = {}

    clusters = df['cluster_label'].unique()

    for c in clusters:
        subset = df[df['cluster_label'] == c]
        data = subset['sentimen'].value_counts()

        fig, ax = plt.subplots()
        ax.pie(data.values, labels=data.index, autopct='%1.1f%%')
        ax.set_title(f"Sentimen pada {c}")

        figs[c] = fig

    return figs


# ============================================================
# PIE CHART - DISTRIBUSI CLUSTER
# ============================================================

def plot_cluster_pie(df):
    data = df['cluster_label'].value_counts()

    fig, ax = plt.subplots()
    ax.pie(data.values, labels=data.index, autopct='%1.1f%%')

    ax.set_title("Distribusi Cluster")

    return fig