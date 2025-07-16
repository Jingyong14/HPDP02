import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# === CONFIG ===
CSV_INPUT = "../data/youtube_comments_no_label.csv"
CSV_OUTPUT_PREFIX = "../data/youtube_comments_sentiment_chunk"
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
BATCH_SIZE = 32
CHUNK_SIZE = 10_000  # Process 10k records at a time

# === Load Model & Tokenizer Once ===
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, truncation=True, max_length=512,
    padding=True)

# === Sentiment Label Mapping ===
label_map = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}

# === Process CSV in Chunks ===
chunks = pd.read_csv(CSV_INPUT, chunksize=CHUNK_SIZE)

for chunk_num, chunk in enumerate(chunks, start=1):
    print(f"\n📦 Processing chunk {chunk_num} with {len(chunk)} rows...")

    texts = chunk["text"].astype(str).tolist()
    sentiments = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        results = classifier(batch, truncation=True)
        sentiments.extend([label_map[res["label"]] for res in results])

    chunk["sentiment"] = sentiments

    # === Save each chunk separately ===
    output_file = f"{CSV_OUTPUT_PREFIX}{chunk_num}.csv"
    chunk.to_csv(output_file, index=False)
    print(f"✅ Saved chunk {chunk_num} to {output_file}")
