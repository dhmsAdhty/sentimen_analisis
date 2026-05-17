import re
import string
import nltk

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords

# ============================================================
# DOWNLOAD NLTK (AMAN)
# ============================================================

try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')

# ============================================================
# INIT
# ============================================================

stop_words = set(stopwords.words('indonesian'))

factory = StemmerFactory()
stemmer = factory.create_stemmer()


# ============================================================
# CLEANING TEXT
# ============================================================

def clean_text(text):

    text = str(text).lower()

    # hapus URL
    text = re.sub(r'http\S+', '', text)

    # hapus angka
    text = re.sub(r'\d+', '', text)

    # hapus tanda baca
    text = text.translate(str.maketrans('', '', string.punctuation))

    # hapus karakter aneh
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ============================================================
# TOKENIZE + STOPWORD
# ============================================================

def remove_stopwords(text):

    tokens = text.split()

    filtered = [word for word in tokens if word not in stop_words]

    return " ".join(filtered)


# ============================================================
# STEMMING
# ============================================================

def stemming(text):

    return stemmer.stem(text)


# ============================================================
# PIPELINE UTAMA
# ============================================================

def preprocess_pipeline(text):

    text = clean_text(text)
    text = remove_stopwords(text)
    text = stemming(text)

    return text